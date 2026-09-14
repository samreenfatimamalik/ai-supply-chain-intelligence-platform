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
        
class ForecastRequest(BaseModel):
    horizon_days: int = 30  # how many days ahead to predict — 7, 14, 30, or 90

class ForecastPoint(BaseModel):
    date: str
    predicted_demand: float
    lower_bound: float
    upper_bound: float

class ForecastResponse(BaseModel):
    horizon_days: int
    forecast: list[ForecastPoint]