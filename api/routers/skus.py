from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import get_db
from api.models import SKU
from api.schemas import SKUOut

router = APIRouter(prefix="/skus", tags=["SKUs"])


@router.get("/", response_model=list[SKUOut])
def get_skus(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(SKU).offset(skip).limit(limit).all()


@router.get("/{sku_id}", response_model=SKUOut)
def get_sku(sku_id: int, db: Session = Depends(get_db)):
    sku = db.query(SKU).filter(SKU.sku_id == sku_id).first()
    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")
    return sku