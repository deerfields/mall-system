from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from ..models import PermitRequest, User, WorkerPermit
from ..app import get_db
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import shutil
import os
import json

router = APIRouter(prefix="/api/permits", tags=["permits"])

class WorkerPermitIn(BaseModel):
    name: str
    code: Optional[str]
    id_card: Optional[UploadFile] = None
    insurance: Optional[UploadFile] = None

class PermitRequestCreate(BaseModel):
    company_name: str
    job_location: str
    onsite_in_charge: str
    contact_no: str
    tenant_or_contractor: str
    job_date_from: datetime
    job_date_to: datetime
    job_time_from: str
    job_time_to: str
    job_type: str
    job_description: str
    requested_by: str
    workers: Optional[list[WorkerPermitIn]] = []

class PermitRequestResponse(BaseModel):
    id: str
    date: datetime
    company_name: str
    job_location: str
    onsite_in_charge: str
    contact_no: str
    ref: Optional[str]
    tenant_or_contractor: str
    job_date_from: datetime
    job_date_to: datetime
    job_time_from: str
    job_time_to: str
    job_type: str
    job_description: str
    requested_by: str
    signature: Optional[str]
    status: str
    facilities_approved: str
    marketing_approved: str
    operations_approved: str
    class Config:
        orm_mode = True

class PermitRequestEdit(BaseModel):
    company_name: Optional[str] = None
    job_location: Optional[str] = None
    onsite_in_charge: Optional[str] = None
    contact_no: Optional[str] = None
    job_date_from: Optional[datetime] = None
    job_date_to: Optional[datetime] = None
    job_time_from: Optional[str] = None
    job_time_to: Optional[str] = None
    job_type: Optional[str] = None
    job_description: Optional[str] = None
    requested_by: Optional[str] = None

class PermitRequestStatusUpdate(BaseModel):
    status: str  # approved, rejected, incomplete
    note: Optional[str] = None

class PermitRequestCreateFull(BaseModel):
    company_name: str
    job_location: str
    onsite_in_charge: str
    contact_no: str
    tenant_or_contractor: str
    job_date_from: datetime
    job_date_to: datetime
    job_time_from: str
    job_time_to: str
    job_type: str
    job_description: str
    requested_by: str
    risk_assessment: Optional[str] = None
    safety_measures: Optional[str] = None
    attachments: Optional[list[str]] = []
    approval_signature: Optional[str] = None
    equipment_list: Optional[list[str]] = []
    need_power_cut: Optional[str] = None
    need_mall_staff: Optional[str] = None
    extra_notes: Optional[str] = None
    workers: Optional[list[WorkerPermitIn]] = []

# Simulated role check (replace with real auth in production)
def get_current_user_role():
    # In production, extract from JWT or session
    return "facilities_manager"  # or "marketing_manager", "operations_manager"

@router.post("/request")
def create_permit_request(
    data: PermitRequestCreate,
    db: Session = Depends(get_db)
):
    permit = PermitRequest(
        company_name=data.company_name,
        job_location=data.job_location,
        onsite_in_charge=data.onsite_in_charge,
        contact_no=data.contact_no,
        tenant_or_contractor=data.tenant_or_contractor,
        job_date_from=data.job_date_from,
        job_date_to=data.job_date_to,
        job_time_from=data.job_time_from,
        job_time_to=data.job_time_to,
        job_type=data.job_type,
        job_description=data.job_description,
        requested_by=data.requested_by
    )
    db.add(permit)
    db.commit()
    db.refresh(permit)
    # ثبت کارگران
    for w in data.workers:
        worker = WorkerPermit(
            permit_request_id=permit.id,
            name=w.name,
            code=w.code,
            id_card_url=None,  # آپلود فایل در نسخه بعدی
            insurance_url=None
        )
        db.add(worker)
    db.commit()
    return {"id": permit.id, "status": permit.status}

@router.post("/request/full")
def create_permit_request_full(
    data: PermitRequestCreateFull,
    db: Session = Depends(get_db)
):
    permit = PermitRequest(
        company_name=data.company_name,
        job_location=data.job_location,
        onsite_in_charge=data.onsite_in_charge,
        contact_no=data.contact_no,
        tenant_or_contractor=data.tenant_or_contractor,
        job_date_from=data.job_date_from,
        job_date_to=data.job_date_to,
        job_time_from=data.job_time_from,
        job_time_to=data.job_time_to,
        job_type=data.job_type,
        job_description=data.job_description,
        requested_by=data.requested_by,
        risk_assessment=data.risk_assessment,
        safety_measures=data.safety_measures,
        attachments=json.dumps(data.attachments) if data.attachments else None,
        approval_signature=data.approval_signature,
        equipment_list=json.dumps(data.equipment_list) if data.equipment_list else None,
        need_power_cut=data.need_power_cut,
        need_mall_staff=data.need_mall_staff,
        extra_notes=data.extra_notes
    )
    db.add(permit)
    db.commit()
    db.refresh(permit)
    # ثبت کارگران
    for w in data.workers:
        worker = WorkerPermit(
            permit_request_id=permit.id,
            name=w.name,
            code=w.code,
            id_card_url=None,
            insurance_url=None
        )
        db.add(worker)
    db.commit()
    return {"id": permit.id, "status": permit.status}

@router.put("/request/{permit_id}/status")
def update_permit_status(permit_id: str, data: PermitRequestStatusUpdate, db: Session = Depends(get_db)):
    permit = db.query(PermitRequest).filter(PermitRequest.id == permit_id).first()
    if not permit:
        raise HTTPException(status_code=404, detail="PermitRequest not found")
    permit.status = data.status
    db.commit()
    return {"id": permit.id, "status": permit.status}

@router.put("/request/{permit_id}/edit")
def edit_permit_request(
    permit_id: str,
    data: PermitRequestCreateFull,
    db: Session = Depends(get_db)
):
    permit = db.query(PermitRequest).filter(PermitRequest.id == permit_id).first()
    if not permit:
        raise HTTPException(status_code=404, detail="PermitRequest not found")
    if permit.status not in ["pending", "incomplete"]:
        raise HTTPException(status_code=400, detail="Cannot edit after approval")
    permit.company_name = data.company_name
    permit.job_location = data.job_location
    permit.onsite_in_charge = data.onsite_in_charge
    permit.contact_no = data.contact_no
    permit.tenant_or_contractor = data.tenant_or_contractor
    permit.job_date_from = data.job_date_from
    permit.job_date_to = data.job_date_to
    permit.job_time_from = data.job_time_from
    permit.job_time_to = data.job_time_to
    permit.job_type = data.job_type
    permit.job_description = data.job_description
    permit.requested_by = data.requested_by
    permit.risk_assessment = data.risk_assessment
    permit.safety_measures = data.safety_measures
    permit.attachments = json.dumps(data.attachments) if data.attachments else None
    permit.approval_signature = data.approval_signature
    permit.equipment_list = json.dumps(data.equipment_list) if data.equipment_list else None
    permit.need_power_cut = data.need_power_cut
    permit.need_mall_staff = data.need_mall_staff
    permit.extra_notes = data.extra_notes
    db.commit()
    return {"id": permit.id, "status": permit.status}

@router.post("/", response_model=PermitRequestResponse)
def create_permit(request: PermitRequestCreate, db: Session = Depends(get_db)):
    permit = PermitRequest(**request.dict())
    db.add(permit)
    db.commit()
    db.refresh(permit)
    return permit

@router.get("/", response_model=List[PermitRequestResponse])
def list_permits(db: Session = Depends(get_db)):
    return db.query(PermitRequest).all()

@router.get("/pending/{department}", response_model=List[PermitRequestResponse])
def list_pending_permits_for_department(department: str, db: Session = Depends(get_db)):
    filter_field = f"{department}_approved"
    return db.query(PermitRequest).filter(getattr(PermitRequest, filter_field) == "pending").all()

@router.put("/{permit_id}/edit/{department}", response_model=PermitRequestResponse)
def edit_permit_by_department(permit_id: str, department: str, update: PermitRequestEdit, db: Session = Depends(get_db)):
    # Simulate role check
    user_role = get_current_user_role()
    if not user_role.startswith(department):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this department")
    permit = db.query(PermitRequest).filter(PermitRequest.id == permit_id).first()
    if not permit:
        raise HTTPException(status_code=404, detail="Permit request not found")
    for field, value in update.dict(exclude_unset=True).items():
        setattr(permit, field, value)
    db.commit()
    db.refresh(permit)
    return permit

@router.post("/{permit_id}/approve/{department}")
def approve_permit(permit_id: str, department: str, db: Session = Depends(get_db)):
    # Simulate role check
    user_role = get_current_user_role()
    if not user_role.startswith(department):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this department")
    permit = db.query(PermitRequest).filter(PermitRequest.id == permit_id).first()
    if not permit:
        raise HTTPException(status_code=404, detail="Permit request not found")
    now = datetime.utcnow()
    if department == "facilities":
        permit.facilities_approved = "approved"
        permit.facilities_approved_date = now
    elif department == "marketing":
        permit.marketing_approved = "approved"
        permit.marketing_approved_date = now
    elif department == "operations":
        permit.operations_approved = "approved"
        permit.operations_approved_date = now
    else:
        raise HTTPException(status_code=400, detail="Invalid department")
    # If all approved, set status to approved
    if (permit.facilities_approved == "approved" and
        permit.marketing_approved == "approved" and
        permit.operations_approved == "approved"):
        permit.status = "approved"
    db.commit()
    db.refresh(permit)
    return {"detail": f"Permit approved by {department}"}

@router.post("/worker/{worker_id}/upload")
def upload_worker_files(worker_id: str, id_card: UploadFile = File(None), insurance: UploadFile = File(None), db: Session = Depends(get_db)):
    worker = db.query(WorkerPermit).filter(WorkerPermit.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    upload_dir = "static/permits/"
    os.makedirs(upload_dir, exist_ok=True)
    if id_card:
        id_card_path = os.path.join(upload_dir, f"idcard_{worker_id}_{id_card.filename}")
        with open(id_card_path, "wb") as f:
            shutil.copyfileobj(id_card.file, f)
        worker.id_card_url = id_card_path
    if insurance:
        insurance_path = os.path.join(upload_dir, f"insurance_{worker_id}_{insurance.filename}")
        with open(insurance_path, "wb") as f:
            shutil.copyfileobj(insurance.file, f)
        worker.insurance_url = insurance_path
    db.commit()
    return {"id": worker.id, "id_card_url": worker.id_card_url, "insurance_url": worker.insurance_url}

@router.post("/request/{permit_id}/upload_license")
def upload_company_license(permit_id: str, license_file: UploadFile = File(...), db: Session = Depends(get_db)):
    permit = db.query(PermitRequest).filter(PermitRequest.id == permit_id).first()
    if not permit:
        raise HTTPException(status_code=404, detail="PermitRequest not found")
    upload_dir = "static/company_licenses/"
    os.makedirs(upload_dir, exist_ok=True)
    license_path = os.path.join(upload_dir, f"license_{permit_id}_{license_file.filename}")
    with open(license_path, "wb") as f:
        shutil.copyfileobj(license_file.file, f)
    permit.company_license_url = license_path
    db.commit()
    return {"id": permit.id, "company_license_url": permit.company_license_url}

@router.get("/request/{permit_id}")
def get_permit_request(permit_id: str, db: Session = Depends(get_db)):
    permit = db.query(PermitRequest).filter(PermitRequest.id == permit_id).first()
    if not permit:
        raise HTTPException(status_code=404, detail="PermitRequest not found")
    workers = db.query(WorkerPermit).filter(WorkerPermit.permit_request_id == permit.id).all()
    return {
        "id": permit.id,
        "company_name": permit.company_name,
        "job_location": permit.job_location,
        "onsite_in_charge": permit.onsite_in_charge,
        "contact_no": permit.contact_no,
        "tenant_or_contractor": permit.tenant_or_contractor,
        "job_date_from": permit.job_date_from,
        "job_date_to": permit.job_date_to,
        "job_time_from": permit.job_time_from,
        "job_time_to": permit.job_time_to,
        "job_type": permit.job_type,
        "job_description": permit.job_description,
        "requested_by": permit.requested_by,
        "status": permit.status,
        "workers": [
            {
                "id": w.id,
                "name": w.name,
                "code": w.code,
                "id_card_url": w.id_card_url,
                "insurance_url": w.insurance_url
            } for w in workers
        ]
    }

@router.get("/dashboard")
def permit_dashboard(db: Session = Depends(get_db)):
    total = db.query(PermitRequest).count()
    approved = db.query(PermitRequest).filter(PermitRequest.status == "approved").count()
    rejected = db.query(PermitRequest).filter(PermitRequest.status == "rejected").count()
    incomplete = db.query(PermitRequest).filter(PermitRequest.status == "incomplete").count()
    pending = db.query(PermitRequest).filter(PermitRequest.status == "pending").count()
    recent = db.query(PermitRequest).order_by(PermitRequest.date.desc()).limit(10).all()
    incomplete_permits = db.query(PermitRequest).filter(PermitRequest.status == "incomplete").all()
    def permit_brief(p):
        return {
            "id": p.id,
            "company_name": p.company_name,
            "job_location": p.job_location,
            "job_date_from": p.job_date_from,
            "status": p.status
        }
    return {
        "stats": {
            "total": total,
            "approved": approved,
            "rejected": rejected,
            "incomplete": incomplete,
            "pending": pending
        },
        "recent": [permit_brief(p) for p in recent],
        "incomplete": [permit_brief(p) for p in incomplete_permits]
    } 