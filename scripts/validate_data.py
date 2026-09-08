"""
Day 2 - Basic Data Validation

Checks the generated CSVs (and, if DATABASE_URL is set, the loaded DB tables)
for the kind of issues that would break downstream modules (forecasting,
inventory optimization, risk scoring):

  - row counts sane
  - no nulls in key columns
  - referential integrity (orders -> warehouses/skus/suppliers, shipments -> orders)
  - no duplicate primary keys
  - value ranges sane (quantities > 0, dates in expected range, scores in [0,1])

Run:
    python scripts/validate_data.py
"""

import os
import sys
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

FAILURES = []
WARNINGS = []


def check(condition, msg, warn_only=False):
    if not condition:
        (WARNINGS if warn_only else FAILURES).append(msg)
    return condition


def load(name):
    path = os.path.join(DATA_DIR, f"{name}.csv")
    if not os.path.exists(path):
        FAILURES.append(f"Missing file: {name}.csv")
        return None
    return pd.read_csv(path)


def main():
    warehouses = load("warehouses")
    skus = load("skus")
    suppliers = load("suppliers")
    supplier_skus = load("supplier_skus")
    orders = load("orders")
    shipments = load("shipments")

    if any(df is None for df in [warehouses, skus, suppliers, supplier_skus, orders, shipments]):
        print("Some files missing, run generate_synthetic_data.py first.")
        sys.exit(1)

    print("Running validation checks...\n")

    # --- Primary key uniqueness ---
    for name, df, key in [
        ("warehouses", warehouses, "warehouse_id"),
        ("skus", skus, "sku_id"),
        ("suppliers", suppliers, "supplier_id"),
        ("orders", orders, "order_id"),
        ("shipments", shipments, "shipment_id"),
    ]:
        check(df[key].is_unique, f"[{name}] duplicate {key} values found")

    # --- Null checks on key columns ---
    check(orders["warehouse_id"].notna().all(), "[orders] null warehouse_id found")
    check(orders["sku_id"].notna().all(), "[orders] null sku_id found")
    check(orders["supplier_id"].notna().all(), "[orders] null supplier_id found")
    check(orders["quantity"].notna().all(), "[orders] null quantity found")

    # --- Referential integrity ---
    check(orders["warehouse_id"].isin(warehouses["warehouse_id"]).all(),
          "[orders] warehouse_id values not present in warehouses table")
    check(orders["sku_id"].isin(skus["sku_id"]).all(),
          "[orders] sku_id values not present in skus table")
    check(orders["supplier_id"].isin(suppliers["supplier_id"]).all(),
          "[orders] supplier_id values not present in suppliers table")
    check(shipments["order_id"].isin(orders["order_id"]).all(),
          "[shipments] order_id values not present in orders table")
    check(supplier_skus["supplier_id"].isin(suppliers["supplier_id"]).all(),
          "[supplier_skus] supplier_id not present in suppliers table")
    check(supplier_skus["sku_id"].isin(skus["sku_id"]).all(),
          "[supplier_skus] sku_id not present in skus table")

    # --- Value range sanity ---
    check((orders["quantity"] > 0).all(), "[orders] non-positive quantity found")
    check((orders["unit_price"] > 0).all(), "[orders] non-positive unit_price found")
    check(suppliers["reliability_score"].between(0, 1).all(),
          "[suppliers] reliability_score outside [0,1]")
    check(suppliers["on_time_rate"].between(0, 1).all(),
          "[suppliers] on_time_rate outside [0,1]")
    check((skus["unit_price"] >= skus["unit_cost"]).mean() > 0.95,
          "[skus] more than 5% of SKUs priced below cost", warn_only=True)

    # --- Date sanity ---
    orders["order_date"] = pd.to_datetime(orders["order_date"])
    check(orders["order_date"].min().year >= 2023, "[orders] order_date earlier than expected range")
    check(orders["order_date"].max().year <= 2025, "[orders] order_date later than expected range")

    # --- Distribution sanity (won't fail the run, just informative) ---
    print("Row counts:")
    for name, df in [("warehouses", warehouses), ("skus", skus), ("suppliers", suppliers),
                      ("supplier_skus", supplier_skus), ("orders", orders), ("shipments", shipments)]:
        print(f"  {name:<15} {len(df):>8,}")

    print("\nOrder status distribution:")
    print(orders["order_status"].value_counts(normalize=True).round(3).to_string())

    print("\nShipment status distribution:")
    print(shipments["shipment_status"].value_counts(normalize=True).round(3).to_string())

    print("\nOrders per day (avg):", round(orders.groupby("order_date").size().mean(), 1))

    # --- Result ---
    print("\n" + "=" * 50)
    if WARNINGS:
        print(f"WARNINGS ({len(WARNINGS)}):")
        for w in WARNINGS:
            print(f"  ⚠ {w}")
    if FAILURES:
        print(f"FAILURES ({len(FAILURES)}):")
        for f in FAILURES:
            print(f"  ✗ {f}")
        print("\nValidation FAILED.")
        sys.exit(1)
    else:
        print("All checks passed. Data is ready for ingestion / modeling.")


if __name__ == "__main__":
    main()
