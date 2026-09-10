from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


class WarehouseOut(BaseModel):
    warehouse_id: int
    name: str
    region: str
    country: str
    capacity_units: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SKUOut(BaseModel):
    sku_id: int
    sku_code: str
    name: str
    category: str
    unit_cost: Decimal
    unit_price: Decimal
    supplier_id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    order_id: int
    sku_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    order_date: date
    quantity: int
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True