from sqlalchemy import Column, String, Enum as SqlEnum, DateTime, ForeignKey, Text, Integer, Float, Table
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from enum import Enum
import uuid
import json

Base = declarative_base()

class StatusEnum(str, Enum):
    red = "red"
    yellow = "yellow"
    green = "green"

class TaskStatusEnum(str, Enum):
    red = "red"
    yellow = "yellow"
    green = "green"
    returned = "returned"
    pending = "pending"

class Task(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(SqlEnum(TaskStatusEnum), default=TaskStatusEnum.pending)
    created_by = Column(String, ForeignKey('users.id'))
    assigned_to = Column(String, ForeignKey('users.id'), nullable=True)
    department_id = Column(String, ForeignKey('departments.id'))
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    workflow = relationship("WorkflowStep", back_populates="task")

class WorkflowStep(Base):
    __tablename__ = "workflow_steps"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, ForeignKey('tasks.id'))
    step = Column(String)
    user_id = Column(String, ForeignKey('users.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)
    note = Column(String, nullable=True)
    task = relationship("Task", back_populates="workflow")

class Complaint(Base):
    __tablename__ = "complaints"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey('tenants.id'))
    description = Column(String, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey('tenants.id'))
    description = Column(String, nullable=False)
    category = Column(String, nullable=True)  # نوع خرابی: برق/آب/تاسیسات
    suggested_time = Column(DateTime, nullable=True)  # زمان پیشنهادی برای تعمیر
    workers = Column(Text, nullable=True)  # لیست کارگران (JSON string)
    status = Column(String, default="pending")
    assigned_to = Column(String, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    pdf_url = Column(String, nullable=True)
    qr_code = Column(String, nullable=True)

class ContractStatusEnum(str, Enum):
    draft = "draft"
    pending_approval = "pending_approval"
    approved = "approved"
    signed = "signed"
    active = "active"
    rejected = "rejected"
    cancelled = "cancelled"

class Contract(Base):
    __tablename__ = "contracts"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey('tenants.id'))
    shop_id = Column(String, ForeignKey('shops.id'), nullable=False)  # ارتباط با مغازه
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(SqlEnum(ContractStatusEnum), default=ContractStatusEnum.draft)
    workflow_steps = relationship("ContractWorkflowStep", back_populates="contract")

class Payment(Base):
    __tablename__ = "payments"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey('tenants.id'))
    contract_id = Column(String, ForeignKey('contracts.id'))
    amount = Column(Float, nullable=False)
    paid_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="paid")

class SecurityLog(Base):
    __tablename__ = "security_logs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    store_id = Column(String, nullable=False)
    check_time = Column(DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False)
    guard_id = Column(String, ForeignKey('users.id'))

class Shop(Base):
    __tablename__ = "shops"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    location = Column(String)
    size = Column(String)

class Rental(Base):
    __tablename__ = "rentals"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    shop_id = Column(String, ForeignKey('shops.id'))
    tenant = Column(String, nullable=False)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    amount = Column(String)
    shop = relationship("Shop")

class UserRoleEnum(str, Enum):
    superadmin = "superadmin"
    manager = "manager"
    employee = "employee"
    tenant = "tenant"

class Role(Base):
    __tablename__ = "roles"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    users = relationship("User", back_populates="role")

class Department(Base):
    __tablename__ = "departments"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    users = relationship("User", back_populates="department")

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role_id = Column(String, ForeignKey('roles.id'))
    department_id = Column(String, ForeignKey('departments.id'))
    tenant_id = Column(String, ForeignKey('tenants.id'), nullable=True)  # برای مستأجران
    is_active = Column(String, default="1")
    mfa_secret = Column(String, nullable=True)
    role = relationship("Role", back_populates="users")
    department = relationship("Department", back_populates="users")
    tenant = relationship("Tenant", foreign_keys=[tenant_id])

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    shop_name = Column(String, nullable=False)
    user_id = Column(String, ForeignKey('users.id'))
    contract_info = Column(String, nullable=True)
    user = relationship("User") 

class ContractWorkflowStep(Base):
    __tablename__ = "contract_workflow_steps"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    contract_id = Column(String, ForeignKey('contracts.id'))
    step = Column(String)  # نام مرحله (مثلاً: ثبت اولیه، تایید مدیر، ...)
    user_id = Column(String, ForeignKey('users.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)
    note = Column(String, nullable=True)
    contract = relationship("Contract", back_populates="workflow_steps")
    user = relationship("User") 

class PermitRequest(Base):
    __tablename__ = "permit_requests"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    date = Column(DateTime, default=datetime.utcnow)
    company_name = Column(String)
    job_location = Column(String)
    onsite_in_charge = Column(String)
    contact_no = Column(String)
    ref = Column(String, nullable=True)
    tenant_or_contractor = Column(String)  # 'tenant' or 'contractor'
    job_date_from = Column(DateTime)
    job_date_to = Column(DateTime)
    job_time_from = Column(String)
    job_time_to = Column(String)
    job_type = Column(String)  # Maintenance, Remedial, New, Trading, Others
    job_description = Column(Text)
    requested_by = Column(String)
    signature = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending, approved, rejected
    facilities_approved = Column(String, default="pending")
    marketing_approved = Column(String, default="pending")
    operations_approved = Column(String, default="pending")
    facilities_approved_by = Column(String, nullable=True)
    marketing_approved_by = Column(String, nullable=True)
    operations_approved_by = Column(String, nullable=True)
    facilities_approved_date = Column(DateTime, nullable=True)
    marketing_approved_date = Column(DateTime, nullable=True)
    operations_approved_date = Column(DateTime, nullable=True)
    # فیلدهای جدید
    risk_assessment = Column(Text, nullable=True)  # ارزیابی ریسک
    safety_measures = Column(Text, nullable=True)  # اقدامات ایمنی
    attachments = Column(Text, nullable=True)  # لیست فایل‌های پیوست (JSON)
    approval_signature = Column(String, nullable=True)  # امضا/نام تاییدکننده
    equipment_list = Column(Text, nullable=True)  # لیست ابزار و تجهیزات (JSON)
    need_power_cut = Column(String, nullable=True)  # نیاز به قطع برق/آب/گاز
    need_mall_staff = Column(String, nullable=True)  # نیاز به همراهی پرسنل مال
    extra_notes = Column(Text, nullable=True)  # توضیحات تکمیلی
    company_license_url = Column(String, nullable=True)  # آدرس فایل مجوز شرکت

class WorkerPermit(Base):
    __tablename__ = "worker_permits"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    permit_request_id = Column(String, ForeignKey('permit_requests.id'))
    name = Column(String, nullable=False)
    code = Column(String, nullable=True)
    id_card_url = Column(String, nullable=True)  # آدرس تصویر کارت شناسایی
    insurance_url = Column(String, nullable=True)  # آدرس فایل بیمه
    permit_request = relationship("PermitRequest", backref="workers")

# جدول واسط برای ارتباط چند به چند Notification و Tenant
notification_tenant = Table(
    'notification_tenant', Base.metadata,
    Column('notification_id', String, ForeignKey('notifications.id')),
    Column('tenant_id', String, ForeignKey('tenants.id'))
)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_by = Column(String, ForeignKey('users.id'))
    email_sent = Column(String, default="pending")  # pending, sent, failed
    recipients = relationship("Tenant", secondary=notification_tenant, backref="notifications")
    sender = relationship("User") 

class Survey(Base):
    __tablename__ = "surveys"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    questions = Column(Text, nullable=False)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    responses = relationship("SurveyResponse", back_populates="survey")

class SurveyResponse(Base):
    __tablename__ = "survey_responses"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    survey_id = Column(String, ForeignKey('surveys.id'))
    customer_name = Column(String, nullable=True)
    answers = Column(Text, nullable=False)  # JSON string
    submitted_at = Column(DateTime, default=datetime.utcnow)
    survey = relationship("Survey", back_populates="responses")

class ShopUpdate(Base):
    __tablename__ = "shop_updates"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    shop_id = Column(String, ForeignKey('shops.id'))
    updated_by = Column(String, ForeignKey('users.id'))
    update_type = Column(String, nullable=False)  # phone, items, etc.
    details = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)
    shop = relationship("Shop")
    user = relationship("User") 

class MaintenanceWorkflowStep(Base):
    __tablename__ = "maintenance_workflow_steps"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    maintenance_request_id = Column(String, ForeignKey('maintenance_requests.id'))
    step = Column(String)  # نام مرحله (مثلاً: ثبت اولیه، تایید مدیر عملیات، ...)
    user_id = Column(String, ForeignKey('users.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)
    note = Column(String, nullable=True)
    maintenance_request = relationship("MaintenanceRequest", backref="workflow_steps")
    user = relationship("User") 