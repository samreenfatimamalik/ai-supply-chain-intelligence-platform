from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
from api.models import Warehouse
from api.schemas import WarehouseOut

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])


@router.get("/", response_model=list[WarehouseOut])
def get_warehouses(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Warehouse).offset(skip).limit(limit).all()


@router.get("/{warehouse_id}", response_model=WarehouseOut)
def get_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    wh = db.query(Warehouse).filter(Warehouse.warehouse_id == warehouse_id).first()
    if not wh:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return wh