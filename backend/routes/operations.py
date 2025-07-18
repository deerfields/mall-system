from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import SecurityLog, Shop, User
from ..app import get_db
from pydantic import BaseModel
from typing import List
from datetime import datetime

router = APIRouter(prefix="/api/operations", tags=["operations"])

class SecurityLogCreate(BaseModel):
    store_id: str
    status: str  # open, close
    guard_id: str
    check_time: datetime = None

class SecurityLogOut(BaseModel):
    id: str
    store_id: str
    status: str
    guard_id: str
    check_time: datetime
    class Config:
        orm_mode = True

@router.post("/securitylog", response_model=SecurityLogOut)
def create_security_log(data: SecurityLogCreate, db: Session = Depends(get_db)):
    log = SecurityLog(
        store_id=data.store_id,
        status=data.status,
        guard_id=data.guard_id,
        check_time=data.check_time or datetime.utcnow()
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

@router.get("/securitylog", response_model=List[SecurityLogOut])
def list_security_logs(db: Session = Depends(get_db)):
    logs = db.query(SecurityLog).order_by(SecurityLog.check_time.desc()).all()
    return logs 