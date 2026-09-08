-- ============================================================
-- AI Supply Chain Intelligence Platform (SC-001)
-- Day 2 - PostgreSQL Schema (aligned with synthetic dataset)
-- ============================================================

DROP TABLE IF EXISTS shipments CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS supplier_skus CASCADE;
DROP TABLE IF EXISTS suppliers CASCADE;
DROP TABLE IF EXISTS skus CASCADE;
DROP TABLE IF EXISTS warehouses CASCADE;

CREATE TABLE warehouses (
    warehouse_id     INTEGER PRIMARY KEY,
    warehouse_code   VARCHAR(20) UNIQUE NOT NULL,
    name             VARCHAR(150) NOT NULL,
    city             VARCHAR(100),
    region           VARCHAR(50),
    country          VARCHAR(100),
    latitude         DOUBLE PRECISION,
    longitude        DOUBLE PRECISION,
    capacity_units   INTEGER,
    opened_date      DATE,
    is_active        BOOLEAN DEFAULT TRUE
);

CREATE TABLE skus (
    sku_id           INTEGER PRIMARY KEY,
    sku_code         VARCHAR(20) UNIQUE NOT NULL,
    product_name     VARCHAR(200),
    category         VARCHAR(100),
    subcategory      VARCHAR(100),
    unit_cost        NUMERIC(12,2),
    unit_price       NUMERIC(12,2),
    weight_kg        NUMERIC(10,2),
    shelf_life_days  INTEGER,
    reorder_point    INTEGER,
    is_active        BOOLEAN DEFAULT TRUE
);

CREATE TABLE suppliers (
    supplier_id        INTEGER PRIMARY KEY,
    supplier_code      VARCHAR(20) UNIQUE NOT NULL,
    supplier_name      VARCHAR(200),
    country            VARCHAR(100),
    region             VARCHAR(50),
    reliability_score  NUMERIC(5,3),
    avg_lead_time_days INTEGER,
    on_time_rate       NUMERIC(5,3),
    onboarded_date     DATE,
    is_active          BOOLEAN DEFAULT TRUE
);

CREATE TABLE supplier_skus (
    link_id             INTEGER PRIMARY KEY,
    supplier_id         INTEGER NOT NULL REFERENCES suppliers(supplier_id),
    sku_id              INTEGER NOT NULL REFERENCES skus(sku_id),
    supplier_unit_cost  NUMERIC(12,2)
);

CREATE TABLE orders (
    order_id               INTEGER PRIMARY KEY,
    order_date             DATE NOT NULL,
    warehouse_id           INTEGER NOT NULL REFERENCES warehouses(warehouse_id),
    sku_id                 INTEGER NOT NULL REFERENCES skus(sku_id),
    supplier_id            INTEGER NOT NULL REFERENCES suppliers(supplier_id),
    quantity               INTEGER NOT NULL,
    unit_price             NUMERIC(12,2),
    total_value            NUMERIC(14,2),
    order_status           VARCHAR(20),
    expected_delivery_date DATE
);

CREATE TABLE shipments (
    shipment_id            INTEGER PRIMARY KEY,
    order_id               INTEGER NOT NULL REFERENCES orders(order_id),
    carrier                VARCHAR(100),
    shipped_date           DATE,
    planned_transit_days   INTEGER,
    actual_delivery_date   DATE,
    delay_days             INTEGER,
    shipment_status        VARCHAR(20)
);

-- Indexes for common query/forecasting patterns
CREATE INDEX idx_orders_sku_date        ON orders(sku_id, order_date);
CREATE INDEX idx_orders_warehouse_date  ON orders(warehouse_id, order_date);
CREATE INDEX idx_orders_supplier        ON orders(supplier_id);
CREATE INDEX idx_shipments_order        ON shipments(order_id);
CREATE INDEX idx_shipments_status       ON shipments(shipment_status);
CREATE INDEX idx_supplier_skus_supplier ON supplier_skus(supplier_id);
CREATE INDEX idx_supplier_skus_sku      ON supplier_skus(sku_id);
