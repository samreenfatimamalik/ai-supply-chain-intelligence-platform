"""
Day 2 - Synthetic Dataset Generator
AI Supply Chain Intelligence Platform (SC-001)

Generates realistic-scaled synthetic data for:
  warehouses, skus, suppliers, supplier_skus, orders, shipments

Scale (Medium): 50 warehouses | 5,000 SKUs | 400 suppliers | ~150k orders

Run:
    python scripts/generate_synthetic_data.py

Output:
    data/warehouses.csv
    data/skus.csv
    data/suppliers.csv
    data/supplier_skus.csv
    data/orders.csv
    data/shipments.csv
"""

import numpy as np
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta
import random
import os

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
fake = Faker()
Faker.seed(SEED)

N_WAREHOUSES = 50
N_SKUS = 5000
N_SUPPLIERS = 400
N_ORDERS = 150_000

ORDER_DATE_START = datetime(2023, 1, 1)
ORDER_DATE_END = datetime(2025, 12, 31)

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUT_DIR, exist_ok=True)

CATEGORIES = {
    "Electronics": ["Mobile Accessories", "Audio", "Computing", "Wearables", "Cameras"],
    "Grocery": ["Snacks", "Beverages", "Dairy", "Staples", "Frozen Foods"],
    "Apparel": ["Menswear", "Womenswear", "Kidswear", "Footwear", "Accessories"],
    "Home & Living": ["Furniture", "Kitchenware", "Decor", "Bedding", "Storage"],
    "Health & Beauty": ["Skincare", "Haircare", "Personal Care", "Wellness", "Cosmetics"],
    "Toys & Sports": ["Outdoor", "Indoor Games", "Fitness Equipment", "Toys", "Cycling"],
    "Office & Stationery": ["Paper Products", "Writing", "Office Supplies", "Organizers", "Printers"],
}

REGIONS = ["North", "South", "East", "West", "Central"]
COUNTRIES = ["Pakistan", "UAE", "Saudi Arabia", "Bangladesh", "Sri Lanka", "China", "Vietnam", "Turkey"]
CARRIERS = ["FastTrack Logistics", "SwiftShip", "CargoLine", "MetroFreight", "UnionCarrier", "TransGlobal"]
ORDER_STATUSES = ["delivered", "in_transit", "delayed", "cancelled", "pending"]
ORDER_STATUS_WEIGHTS = [0.72, 0.10, 0.10, 0.03, 0.05]


def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


# ---------------------------------------------------------------------------
# 1. Warehouses
# ---------------------------------------------------------------------------
def generate_warehouses(n=N_WAREHOUSES):
    rows = []
    for i in range(1, n + 1):
        city = fake.city()
        rows.append({
            "warehouse_id": i,
            "warehouse_code": f"WH-{i:04d}",
            "name": f"{city} Distribution Center",
            "city": city,
            "region": random.choice(REGIONS),
            "country": "Pakistan" if random.random() < 0.6 else random.choice(COUNTRIES),
            "latitude": round(float(fake.latitude()), 6),
            "longitude": round(float(fake.longitude()), 6),
            "capacity_units": random.randint(50_000, 500_000),
            "opened_date": random_date(datetime(2010, 1, 1), datetime(2022, 1, 1)).date(),
            "is_active": True,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 2. SKUs
# ---------------------------------------------------------------------------
def generate_skus(n=N_SKUS):
    rows = []
    for i in range(1, n + 1):
        category = random.choice(list(CATEGORIES.keys()))
        subcategory = random.choice(CATEGORIES[category])
        unit_cost = round(np.random.lognormal(mean=2.8, sigma=1.0), 2)
        margin_pct = random.uniform(0.15, 0.65)
        rows.append({
            "sku_id": i,
            "sku_code": f"SKU-{i:06d}",
            "product_name": f"{subcategory} {fake.word().capitalize()} {random.choice(['Pro','Max','Lite','Plus','Standard','Classic'])}",
            "category": category,
            "subcategory": subcategory,
            "unit_cost": unit_cost,
            "unit_price": round(unit_cost * (1 + margin_pct), 2),
            "weight_kg": round(np.random.uniform(0.05, 25.0), 2),
            "shelf_life_days": random.choice([None, 30, 60, 90, 180, 365, 730]),
            "reorder_point": random.randint(20, 500),
            "is_active": random.random() > 0.03,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 3. Suppliers
# ---------------------------------------------------------------------------
def generate_suppliers(n=N_SUPPLIERS):
    rows = []
    for i in range(1, n + 1):
        # base reliability skewed high (most suppliers are decent), with a risky tail
        reliability = np.clip(np.random.beta(a=6, b=2), 0, 1)
        rows.append({
            "supplier_id": i,
            "supplier_code": f"SUP-{i:05d}",
            "supplier_name": fake.company(),
            "country": random.choice(COUNTRIES),
            "region": random.choice(REGIONS),
            "reliability_score": round(reliability, 3),          # 0-1, historical composite
            "avg_lead_time_days": int(np.clip(np.random.normal(14, 6), 2, 60)),
            "on_time_rate": round(np.clip(reliability + np.random.normal(0, 0.05), 0, 1), 3),
            "onboarded_date": random_date(datetime(2015, 1, 1), datetime(2023, 1, 1)).date(),
            "is_active": random.random() > 0.05,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 4. Supplier <-> SKU mapping (which suppliers can supply which SKUs)
# ---------------------------------------------------------------------------
def generate_supplier_skus(suppliers_df, skus_df, avg_skus_per_supplier=25):
    rows = []
    sku_ids = skus_df["sku_id"].tolist()
    link_id = 1
    for sup_id in suppliers_df["supplier_id"]:
        k = max(1, int(np.random.poisson(avg_skus_per_supplier)))
        chosen = random.sample(sku_ids, min(k, len(sku_ids)))
        for sku_id in chosen:
            rows.append({
                "link_id": link_id,
                "supplier_id": sup_id,
                "sku_id": sku_id,
                "supplier_unit_cost": round(np.random.uniform(0.8, 1.1) *
                                             skus_df.loc[skus_df.sku_id == sku_id, "unit_cost"].values[0], 2),
            })
            link_id += 1
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 5. Orders (drives everything: forecasting target = order quantity by day/sku/warehouse)
# ---------------------------------------------------------------------------
def generate_orders(n, warehouses_df, skus_df, supplier_skus_df):
    warehouse_ids = warehouses_df["warehouse_id"].tolist()
    active_skus = skus_df[skus_df.is_active]["sku_id"].tolist()

    # map sku -> list of eligible suppliers (fallback to random supplier if sku has none mapped)
    sku_to_suppliers = supplier_skus_df.groupby("sku_id")["supplier_id"].apply(list).to_dict()
    all_supplier_ids = supplier_skus_df["supplier_id"].unique().tolist()

    # give some SKUs seasonal / trending demand multipliers for realistic forecasting signal later
    sku_base_demand = {sku: np.random.lognormal(mean=1.5, sigma=0.9) for sku in active_skus}

    rows = []
    total_days = (ORDER_DATE_END - ORDER_DATE_START).days

    for i in range(1, n + 1):
        sku_id = random.choice(active_skus)
        warehouse_id = random.choice(warehouse_ids)
        suppliers_for_sku = sku_to_suppliers.get(sku_id, all_supplier_ids)
        supplier_id = random.choice(suppliers_for_sku)

        # seasonality: bump demand near month-end and Nov-Dec (holiday season)
        day_offset = random.randint(0, total_days)
        order_date = ORDER_DATE_START + timedelta(days=day_offset)
        seasonal_factor = 1.4 if order_date.month in (11, 12) else 1.0

        base_qty = sku_base_demand[sku_id] * seasonal_factor
        quantity = max(1, int(np.random.poisson(max(base_qty, 1))))

        sku_price = skus_df.loc[skus_df.sku_id == sku_id, "unit_price"].values[0]
        status = np.random.choice(ORDER_STATUSES, p=ORDER_STATUS_WEIGHTS)
        expected_delivery = order_date + timedelta(days=random.randint(2, 21))

        rows.append({
            "order_id": i,
            "order_date": order_date.date(),
            "warehouse_id": warehouse_id,
            "sku_id": sku_id,
            "supplier_id": supplier_id,
            "quantity": quantity,
            "unit_price": sku_price,
            "total_value": round(quantity * sku_price, 2),
            "order_status": status,
            "expected_delivery_date": expected_delivery.date(),
        })

        if i % 25_000 == 0:
            print(f"  ...generated {i:,}/{n:,} orders")

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 6. Shipments (one per non-cancelled/pending order, links delay behaviour to supplier reliability)
# ---------------------------------------------------------------------------
def generate_shipments(orders_df, suppliers_df):
    supplier_reliability = suppliers_df.set_index("supplier_id")["reliability_score"].to_dict()
    supplier_lead_time = suppliers_df.set_index("supplier_id")["avg_lead_time_days"].to_dict()

    shippable = orders_df[~orders_df.order_status.isin(["cancelled", "pending"])].copy()

    rows = []
    for idx, order in enumerate(shippable.itertuples(), start=1):
        reliability = supplier_reliability.get(order.supplier_id, 0.7)
        lead_time = supplier_lead_time.get(order.supplier_id, 14)

        shipped_date = pd.Timestamp(order.order_date) + timedelta(days=random.randint(1, 4))

        # lower reliability -> higher chance & magnitude of delay
        delay_prob = 1 - reliability
        is_delayed = random.random() < delay_prob
        planned_transit = max(1, int(np.random.normal(lead_time, lead_time * 0.2)))
        delay_days = int(np.random.exponential(scale=lead_time * 0.5)) if is_delayed else 0

        actual_delivery = shipped_date + timedelta(days=planned_transit + delay_days)

        shipment_status = "delivered" if order.order_status == "delivered" else \
                           ("in_transit" if order.order_status == "in_transit" else "delayed")

        rows.append({
            "shipment_id": idx,
            "order_id": order.order_id,
            "carrier": random.choice(CARRIERS),
            "shipped_date": shipped_date.date(),
            "planned_transit_days": planned_transit,
            "actual_delivery_date": actual_delivery.date() if shipment_status != "in_transit" else None,
            "delay_days": delay_days,
            "shipment_status": shipment_status,
        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("Generating warehouses...")
    warehouses_df = generate_warehouses()

    print("Generating SKUs...")
    skus_df = generate_skus()

    print("Generating suppliers...")
    suppliers_df = generate_suppliers()

    print("Generating supplier-SKU mapping...")
    supplier_skus_df = generate_supplier_skus(suppliers_df, skus_df)

    print(f"Generating {N_ORDERS:,} orders...")
    orders_df = generate_orders(N_ORDERS, warehouses_df, skus_df, supplier_skus_df)

    print("Generating shipments...")
    shipments_df = generate_shipments(orders_df, suppliers_df)

    print("\nWriting CSVs to", os.path.abspath(OUT_DIR))
    warehouses_df.to_csv(os.path.join(OUT_DIR, "warehouses.csv"), index=False)
    skus_df.to_csv(os.path.join(OUT_DIR, "skus.csv"), index=False)
    suppliers_df.to_csv(os.path.join(OUT_DIR, "suppliers.csv"), index=False)
    supplier_skus_df.to_csv(os.path.join(OUT_DIR, "supplier_skus.csv"), index=False)
    orders_df.to_csv(os.path.join(OUT_DIR, "orders.csv"), index=False)
    shipments_df.to_csv(os.path.join(OUT_DIR, "shipments.csv"), index=False)

    print("\nDone. Row counts:")
    print(f"  warehouses     : {len(warehouses_df):,}")
    print(f"  skus           : {len(skus_df):,}")
    print(f"  suppliers      : {len(suppliers_df):,}")
    print(f"  supplier_skus  : {len(supplier_skus_df):,}")
    print(f"  orders         : {len(orders_df):,}")
    print(f"  shipments      : {len(shipments_df):,}")


if __name__ == "__main__":
    main()
