from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import MaintenanceRequest, MaintenanceWorkflowStep, User, Department
from ..app import get_db
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from fastapi.responses import StreamingResponse
import io
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
from ..services.notification_service import send_email
import json

router = APIRouter(prefix="/api/maintenance", tags=["maintenance"])

class WorkflowStepCreate(BaseModel):
    maintenance_request_id: str
    step: str
    user_id: str
    note: Optional[str] = None

class WorkflowStepOut(BaseModel):
    id: str
    maintenance_request_id: str
    step: str
    user_id: str
    note: Optional[str]
    timestamp: datetime
    class Config:
        orm_mode = True

class MaintenanceRequestCreate(BaseModel):
    tenant_id: str
    description: str
    category: str
    suggested_time: Optional[datetime]
    workers: Optional[list] = []

class MaintenanceRequestOut(BaseModel):
    id: str
    tenant_id: str
    description: str
    category: str
    suggested_time: Optional[datetime]
    workers: Optional[list]
    status: str
    assigned_to: Optional[str]
    created_at: datetime
    resolved_at: Optional[datetime]
    pdf_url: Optional[str]
    qr_code: Optional[str]
    class Config:
        orm_mode = True

@router.post("/workflow", response_model=WorkflowStepOut)
def add_workflow_step(data: WorkflowStepCreate, db: Session = Depends(get_db)):
    req = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == data.maintenance_request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="MaintenanceRequest not found")
    step = MaintenanceWorkflowStep(
        maintenance_request_id=data.maintenance_request_id,
        step=data.step,
        user_id=data.user_id,
        note=data.note
    )
    db.add(step)
    db.commit()
    db.refresh(step)
    return step

@router.get("/workflow/{maintenance_request_id}", response_model=List[WorkflowStepOut])
def get_workflow_steps(maintenance_request_id: str, db: Session = Depends(get_db)):
    steps = db.query(MaintenanceWorkflowStep).filter(MaintenanceWorkflowStep.maintenance_request_id == maintenance_request_id).order_by(MaintenanceWorkflowStep.timestamp).all()
    return steps

@router.post("/request", response_model=MaintenanceRequestOut)
def create_maintenance_request(data: MaintenanceRequestCreate, db: Session = Depends(get_db)):
    req = MaintenanceRequest(
        tenant_id=data.tenant_id,
        description=data.description,
        category=data.category,
        suggested_time=data.suggested_time,
        workers=json.dumps(data.workers) if data.workers else None
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    # اطلاع‌رسانی خودکار به مدیر عملیات و FM
    ops_dept = db.query(Department).filter(Department.name.ilike('%عملیات%')).first()
    fm_dept = db.query(Department).filter(Department.name.ilike('%fm%')).first()
    recipients = []
    if ops_dept:
        recipients += db.query(User).filter(User.department_id == ops_dept.id).all()
    if fm_dept:
        recipients += db.query(User).filter(User.department_id == fm_dept.id).all()
    for user in recipients:
        send_email(user.username, "درخواست تعمیرات جدید", f"شرح: {data.description}\nنوع خرابی: {data.category}\nزمان پیشنهادی: {data.suggested_time}")
    return MaintenanceRequestOut(
        id=req.id,
        tenant_id=req.tenant_id,
        description=req.description,
        category=req.category,
        suggested_time=req.suggested_time,
        workers=json.loads(req.workers) if req.workers else [],
        status=req.status,
        assigned_to=req.assigned_to,
        created_at=req.created_at,
        resolved_at=req.resolved_at,
        pdf_url=req.pdf_url,
        qr_code=req.qr_code
    )

@router.get("/pdf/{maintenance_request_id}")
def generate_maintenance_pdf(maintenance_request_id: str, db: Session = Depends(get_db)):
    req = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == maintenance_request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="MaintenanceRequest not found")
    # فقط برای درخواست تایید شده
    if req.status != "approved":
        raise HTTPException(status_code=400, detail="Request is not approved")
    # تولید QR Code با اطلاعات کامل
    workers_list = json.loads(req.workers) if req.workers else []
    qr_data = json.dumps({
        "id": req.id,
        "tenant_id": req.tenant_id,
        "category": req.category,
        "suggested_time": req.suggested_time.isoformat() if req.suggested_time else None,
        "workers": workers_list
    }, ensure_ascii=False)
    qr_img = qrcode.make(qr_data)
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    # تولید PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont("Helvetica", 14)
    p.drawString(100, 800, f"درخواست تعمیرات شماره: {req.id}")
    p.drawString(100, 780, f"مستاجر: {req.tenant_id}")
    p.drawString(100, 760, f"نوع خرابی: {req.category}")
    p.drawString(100, 740, f"زمان پیشنهادی: {req.suggested_time}")
    p.drawString(100, 720, f"توضیحات: {req.description}")
    p.drawString(100, 700, f"وضعیت: {req.status}")
    p.drawString(100, 680, f"کارگران:")
    y = 660
    for w in workers_list:
        p.drawString(120, y, f"- {w}")
        y -= 20
        if y < 100:
            p.showPage()
            y = 800
    # درج QR Code
    p.drawInlineImage(qr_buffer, 400, 650, width=100, height=100)
    p.showPage()
    p.save()
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=maintenance_{req.id}.pdf"}) 