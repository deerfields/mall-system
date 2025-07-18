from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import Shop, Rental, Base, ShopUpdate
from ..app import get_db
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/shops", tags=["shops"])

class ShopCreate(BaseModel):
    name: str
    location: Optional[str] = None
    size: Optional[str] = None

class ShopResponse(BaseModel):
    id: str
    name: str
    location: Optional[str]
    size: Optional[str]
    class Config:
        orm_mode = True

@router.post("/", response_model=ShopResponse)
def create_shop(shop: ShopCreate, db: Session = Depends(get_db)):
    new_shop = Shop(**shop.dict())
    db.add(new_shop)
    db.commit()
    db.refresh(new_shop)
    return new_shop

@router.get("/", response_model=List[ShopResponse])
def list_shops(db: Session = Depends(get_db)):
    return db.query(Shop).all()

# Rental models and endpoints
class RentalCreate(BaseModel):
    shop_id: str
    tenant: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    amount: Optional[str] = None

class RentalResponse(BaseModel):
    id: str
    shop_id: str
    tenant: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    amount: Optional[str]
    class Config:
        orm_mode = True

@router.post("/rental", response_model=RentalResponse)
def create_rental(rental: RentalCreate, db: Session = Depends(get_db)):
    new_rental = Rental(**rental.dict())
    db.add(new_rental)
    db.commit()
    db.refresh(new_rental)
    return new_rental

@router.get("/rental", response_model=List[RentalResponse])
def list_rentals(db: Session = Depends(get_db)):
    return db.query(Rental).all()

class ShopUpdateCreate(BaseModel):
    shop_id: str
    update_type: str
    details: str
    updated_by: str

class ShopUpdateOut(BaseModel):
    id: str
    shop_id: str
    update_type: str
    details: str
    updated_by: str
    updated_at: datetime
    class Config:
        orm_mode = True

@router.post("/update", response_model=ShopUpdateOut)
def create_shop_update(data: ShopUpdateCreate, db: Session = Depends(get_db)):
    update = ShopUpdate(
        shop_id=data.shop_id,
        update_type=data.update_type,
        details=data.details,
        updated_by=data.updated_by
    )
    db.add(update)
    db.commit()
    db.refresh(update)
    return update

@router.get("/update", response_model=List[ShopUpdateOut])
def list_shop_updates(db: Session = Depends(get_db)):
    updates = db.query(ShopUpdate).all()
    return updates 