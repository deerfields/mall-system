from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import Contract, ContractStatusEnum, ContractWorkflowStep, Shop, User, Role
from ..app import get_db
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from fastapi.responses import StreamingResponse
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import qrcode
from ..services import notification_service, security_service

router = APIRouter(prefix="/api/contracts", tags=["contracts"])

class ContractCreate(BaseModel):
    tenant_id: str
    shop_id: str
    start_date: datetime
    end_date: datetime
    amount: float

class ContractUpdate(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    amount: Optional[float] = None
    status: Optional[ContractStatusEnum] = None

class ContractResponse(BaseModel):
    id: str
    tenant_id: str
    shop_id: str
    start_date: datetime
    end_date: datetime
    amount: float
    status: ContractStatusEnum
    class Config:
        orm_mode = True

# اعتبارسنجی تداخل رزرو

def check_overlap(db: Session, shop_id: str, start_date: datetime, end_date: datetime, exclude_contract_id: Optional[str] = None):
    q = db.query(Contract).filter(
        Contract.shop_id == shop_id,
        Contract.status.in_([
            ContractStatusEnum.active,
            ContractStatusEnum.signed,
            ContractStatusEnum.approved,
            ContractStatusEnum.pending_approval
        ])
    )
    if exclude_contract_id:
        q = q.filter(Contract.id != exclude_contract_id)
    for c in q:
        if not (end_date <= c.start_date or start_date >= c.end_date):
            return True
    return False

@router.post("/", response_model=ContractResponse)
def create_contract(contract: ContractCreate, db: Session = Depends(get_db)):
    if check_overlap(db, contract.shop_id, contract.start_date, contract.end_date):
        raise HTTPException(status_code=400, detail="تداخل زمانی با قرارداد دیگر وجود دارد.")
    new_contract = Contract(
        tenant_id=contract.tenant_id,
        shop_id=contract.shop_id,
        start_date=contract.start_date,
        end_date=contract.end_date,
        amount=contract.amount,
        status=ContractStatusEnum.draft
    )
    db.add(new_contract)
    db.commit()
    db.refresh(new_contract)
    # ثبت اولین مرحله گردش کار
    step = ContractWorkflowStep(
        contract_id=new_contract.id,
        step="draft",
        user_id=None,
        note="ایجاد اولیه قرارداد"
    )
    db.add(step)
    db.commit()
    return new_contract

@router.put("/{contract_id}", response_model=ContractResponse)
def update_contract(contract_id: str, update: ContractUpdate, db: Session = Depends(get_db)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="قرارداد یافت نشد.")
    if update.start_date or update.end_date:
        start = update.start_date or contract.start_date
        end = update.end_date or contract.end_date
        if check_overlap(db, contract.shop_id, start, end, exclude_contract_id=contract.id):
            raise HTTPException(status_code=400, detail="تداخل زمانی با قرارداد دیگر وجود دارد.")
        contract.start_date = start
        contract.end_date = end
    if update.amount:
        contract.amount = update.amount
    if update.status:
        contract.status = update.status
        # ثبت مرحله جدید گردش کار
        step = ContractWorkflowStep(
            contract_id=contract.id,
            step=update.status.value,
            user_id=None,
            note=f"تغییر وضعیت به {update.status.value}"
        )
        db.add(step)
    db.commit()
    db.refresh(contract)
    return contract

@router.get("/", response_model=List[ContractResponse])
def list_contracts(db: Session = Depends(get_db)):
    contracts = db.query(Contract).all()
    return contracts

@router.get("/{contract_id}", response_model=ContractResponse)
def get_contract(contract_id: str, db: Session = Depends(get_db)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="قرارداد یافت نشد.")
    return contract

@router.get("/{contract_id}/workflow", response_model=List[str])
def get_contract_workflow(contract_id: str, db: Session = Depends(get_db)):
    steps = db.query(ContractWorkflowStep).filter(ContractWorkflowStep.contract_id == contract_id).order_by(ContractWorkflowStep.timestamp).all()
    return [f"{s.timestamp}: {s.step} - {s.note}" for s in steps]

@router.get("/{contract_id}/pdf")
def get_contract_pdf(contract_id: str, db: Session = Depends(get_db)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="قرارداد یافت نشد.")
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont("Helvetica", 14)
    p.drawString(100, 800, f"قرارداد شماره: {contract.id}")
    p.drawString(100, 780, f"مستاجر: {contract.tenant_id}")
    p.drawString(100, 760, f"مغازه: {contract.shop_id}")
    p.drawString(100, 740, f"تاریخ شروع: {contract.start_date}")
    p.drawString(100, 720, f"تاریخ پایان: {contract.end_date}")
    p.drawString(100, 700, f"مبلغ: {contract.amount}")
    p.drawString(100, 680, f"وضعیت: {contract.status.value}")
    # تاریخچه گردش کار
    steps = db.query(ContractWorkflowStep).filter(ContractWorkflowStep.contract_id == contract_id).order_by(ContractWorkflowStep.timestamp).all()
    y = 650
    p.setFont("Helvetica", 10)
    for s in steps:
        p.drawString(100, y, f"{s.timestamp}: {s.step} - {s.note or ''}")
        y -= 20
        if y < 100:
            p.showPage()
            y = 800
    p.showPage()
    p.save()
    buffer.seek(0)
    # Notify security after PDF generation
    security_role = db.query(Role).filter(Role.name == "security").first()
    if security_role:
        security_users = db.query(User).filter(User.role_id == security_role.id).all()
        for sec_user in security_users:
            notification_service.send_sms(sec_user.username, f"قرارداد جدید PDF تولید شد: {contract.id}")
            security_service.log_security_event({"contract_id": contract.id, "event": "pdf_generated", "user_id": sec_user.id})
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=contract_{contract_id}.pdf"})

@router.get("/{contract_id}/qrcode")
def get_contract_qrcode(contract_id: str, db: Session = Depends(get_db)):
    img = qrcode.make(f"Contract ID: {contract_id}")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    # Notify security after QR generation
    security_role = db.query(Role).filter(Role.name == "security").first()
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if security_role and contract:
        security_users = db.query(User).filter(User.role_id == security_role.id).all()
        for sec_user in security_users:
            notification_service.send_sms(sec_user.username, f"QR جدید برای قرارداد: {contract.id}")
            security_service.log_security_event({"contract_id": contract.id, "event": "qr_generated", "user_id": sec_user.id})
    return StreamingResponse(buf, media_type="image/png") 