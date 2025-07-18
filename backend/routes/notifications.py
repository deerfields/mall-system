from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..models import Notification, Tenant, User, notification_tenant
from ..app import get_db
from ..services.notification_service import send_email
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

class NotificationCreate(BaseModel):
    title: str
    message: str
    recipient_ids: List[str]
    send_email: Optional[bool] = True

class NotificationResponse(BaseModel):
    id: str
    title: str
    message: str
    created_at: datetime
    sent_by: str
    recipients: List[str]
    email_sent: str
    class Config:
        orm_mode = True

def get_current_user():
    # TODO: Replace with real authentication
    return "admin-user-id"

@router.get("/", response_model=List[NotificationResponse])
def list_notifications(db: Session = Depends(get_db)):
    notifications = db.query(Notification).all()
    return [NotificationResponse(
        id=n.id,
        title=n.title,
        message=n.message,
        created_at=n.created_at,
        sent_by=n.sent_by,
        recipients=[t.id for t in n.recipients],
        email_sent=n.email_sent
    ) for n in notifications]

@router.post("/", response_model=NotificationResponse)
def create_notification(data: NotificationCreate, db: Session = Depends(get_db)):
    current_user_id = get_current_user()
    tenants = db.query(Tenant).filter(Tenant.id.in_(data.recipient_ids)).all()
    if not tenants:
        raise HTTPException(status_code=404, detail="Recipients not found")
    notification = Notification(
        title=data.title,
        message=data.message,
        sent_by=current_user_id,
        recipients=tenants
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    # ارسال ایمیل
    email_status = "pending"
    if data.send_email:
        for tenant in tenants:
            if tenant.user and hasattr(tenant.user, 'username'):
                send_email(tenant.user.username, data.title, data.message)
        email_status = "sent"
        notification.email_sent = email_status
        db.commit()
    return NotificationResponse(
        id=notification.id,
        title=notification.title,
        message=notification.message,
        created_at=notification.created_at,
        sent_by=notification.sent_by,
        recipients=[t.id for t in notification.recipients],
        email_sent=notification.email_sent
    ) 