-- ============================================
-- AI Supply Chain Intelligence Platform
-- Database Schema (Day 1)
-- ============================================

-- 1. WAREHOUSES
CREATE TABLE warehouses (
    warehouse_id    SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    region          VARCHAR(50) NOT NULL,
    country         VARCHAR(50) NOT NULL,
    capacity_units  INT NOT NULL,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- 2. SUPPLIERS
CREATE TABLE suppliers (
    supplier_id         SERIAL PRIMARY KEY,
    name                VARCHAR(100) NOT NULL,
    region              VARCHAR(50) NOT NULL,
    country             VARCHAR(50) NOT NULL,
    reliability_score   NUMERIC(4,2) DEFAULT 0.0,   -- 0.00 - 1.00, updated by risk module later
    avg_lead_time_days  INT,
    created_at          TIMESTAMP DEFAULT NOW()
);

-- 3. SKUS (products)
CREATE TABLE skus (
    sku_id          SERIAL PRIMARY KEY,
    sku_code        VARCHAR(30) UNIQUE NOT NULL,
    name            VARCHAR(150) NOT NULL,
    category        VARCHAR(50) NOT NULL,
    unit_cost       NUMERIC(10,2) NOT NULL,
    unit_price      NUMERIC(10,2) NOT NULL,
    supplier_id     INT REFERENCES suppliers(supplier_id),
    created_at      TIMESTAMP DEFAULT NOW()
);

-- 4. INVENTORY (stock levels per warehouse per SKU)
CREATE TABLE inventory (
    inventory_id     SERIAL PRIMARY KEY,
    warehouse_id     INT REFERENCES warehouses(warehouse_id),
    sku_id           INT REFERENCES skus(sku_id),
    stock_qty        INT NOT NULL DEFAULT 0,
    reorder_point    INT NOT NULL DEFAULT 0,
    safety_stock     INT NOT NULL DEFAULT 0,
    last_updated     TIMESTAMP DEFAULT NOW(),
    UNIQUE (warehouse_id, sku_id)
);

-- 5. ORDERS (customer/demand orders)
CREATE TABLE orders (
    order_id        SERIAL PRIMARY KEY,
    sku_id          INT REFERENCES skus(sku_id),
    warehouse_id    INT REFERENCES warehouses(warehouse_id),
    order_date      DATE NOT NULL,
    quantity        INT NOT NULL,
    status          VARCHAR(20) DEFAULT 'pending',  -- pending, fulfilled, cancelled
    created_at      TIMESTAMP DEFAULT NOW()
);

-- 6. SHIPMENTS (supplier -> warehouse replenishment shipments)
CREATE TABLE shipments (
    shipment_id      SERIAL PRIMARY KEY,
    supplier_id      INT REFERENCES suppliers(supplier_id),
    warehouse_id     INT REFERENCES warehouses(warehouse_id),
    sku_id           INT REFERENCES skus(sku_id),
    order_id         INT REFERENCES orders(order_id),
    expected_date    DATE NOT NULL,
    actual_date      DATE,                          -- NULL until delivered
    quantity         INT NOT NULL,
    status           VARCHAR(20) DEFAULT 'in_transit', -- in_transit, delivered, delayed, cancelled
    created_at       TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- Helpful indexes (for forecasting/query speed)
-- ============================================
CREATE INDEX idx_orders_sku_date ON orders(sku_id, order_date);
CREATE INDEX idx_orders_warehouse ON orders(warehouse_id);
CREATE INDEX idx_inventory_sku ON inventory(sku_id);
CREATE INDEX idx_shipments_supplier ON shipments(supplier_id);
CREATE INDEX idx_shipments_status ON shipments(status);