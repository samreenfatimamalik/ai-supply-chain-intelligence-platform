from sqlalchemy import Column, Integer, String, Numeric, Date, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from api.database import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    warehouse_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    region = Column(String(50), nullable=False)
    country = Column(String(50), nullable=False)
    capacity_units = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    region = Column(String(50), nullable=False)
    country = Column(String(50), nullable=False)
    reliability_score = Column(Numeric(4, 2), default=0.0)
    avg_lead_time_days = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())


class SKU(Base):
    __tablename__ = "skus"

    sku_id = Column(Integer, primary_key=True)
    sku_code = Column(String(30), unique=True, nullable=False)
    name = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False)
    unit_cost = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"))
    created_at = Column(TIMESTAMP, server_default=func.now())


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True)
    sku_id = Column(Integer, ForeignKey("skus.sku_id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.warehouse_id"))
    order_date = Column(Date, nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(String(20), default="pending")
    created_at = Column(TIMESTAMP, server_default=func.now())