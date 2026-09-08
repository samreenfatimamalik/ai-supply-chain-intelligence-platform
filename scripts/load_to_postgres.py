"""
Day 2 - Load synthetic CSVs into PostgreSQL

Requires a .env file (see .env.example) with:
    DATABASE_URL=postgresql://user:password@localhost:5432/supply_chain_db

Run:
    python scripts/load_to_postgres.py
"""

import os
import sys
import time
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    sys.exit("ERROR: DATABASE_URL not set. Copy .env.example to .env and fill it in.")

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(BASE_DIR, "data")
SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "schema.sql")

# Order matters: parents before children (FK dependencies)
LOAD_ORDER = [
    ("warehouses", "warehouses.csv"),
    ("skus", "skus.csv"),
    ("suppliers", "suppliers.csv"),
    ("supplier_skus", "supplier_skus.csv"),
    ("orders", "orders.csv"),
    ("shipments", "shipments.csv"),
]


def run_schema(engine):
    print("Applying schema (schema.sql)...")
    with open(SCHEMA_FILE) as f:
        ddl = f.read()
    with engine.begin() as conn:
        for statement in ddl.split(";"):
            statement = statement.strip()
            if statement:
                conn.execute(text(statement))
    print("Schema applied.\n")


def load_table(engine, table_name, csv_file):
    path = os.path.join(DATA_DIR, csv_file)
    if not os.path.exists(path):
        print(f"  SKIP {table_name}: {csv_file} not found in data/")
        return

    t0 = time.time()
    df = pd.read_csv(path)

    # Pandas reads integer columns that contain nulls (e.g. shelf_life_days) as
    # float64, which writes values like "30.0" instead of "30" — Postgres INTEGER
    # columns reject that. Convert any whole-number float columns to pandas'
    # nullable Int64 dtype so nulls stay empty and integers stay integers.
    for col in df.columns:
        if df[col].dtype == "float64":
            non_null = df[col].dropna()
            if len(non_null) == 0 or (non_null % 1 == 0).all():
                df[col] = df[col].astype("Int64")

    # to_sql with method='multi' is slow for 150k rows; use raw COPY via psycopg2 for orders/shipments
    raw_conn = engine.raw_connection()
    try:
        cur = raw_conn.cursor()
        cols = ",".join(df.columns)
        # write to an in-memory buffer as CSV (no header) for COPY
        import io
        buf = io.StringIO()
        df.to_csv(buf, index=False, header=False)
        buf.seek(0)
        cur.copy_expert(
            f"COPY {table_name} ({cols}) FROM STDIN WITH (FORMAT csv, NULL '')",
            buf,
        )
        raw_conn.commit()
        cur.close()
    finally:
        raw_conn.close()

    print(f"  {table_name:<15} {len(df):>7,} rows loaded  ({time.time()-t0:.1f}s)")


def main():
    engine = create_engine(DATABASE_URL)

    run_schema(engine)

    print("Loading tables...")
    for table_name, csv_file in LOAD_ORDER:
        load_table(engine, table_name, csv_file)

    print("\nDone. Row count check:")
    with engine.connect() as conn:
        for table_name, _ in LOAD_ORDER:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            print(f"  {table_name:<15} {count:>7,}")


if __name__ == "__main__":
    main()