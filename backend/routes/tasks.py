from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .auth import require_roles, get_current_user, get_db
from ..models import Task, WorkflowStep, TaskStatusEnum, User, Department
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    department_id: str
    due_date: Optional[datetime] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    department_id: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[TaskStatusEnum] = None

class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: TaskStatusEnum
    created_by: str
    assigned_to: Optional[str]
    department_id: str
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True

class WorkflowStepCreate(BaseModel):
    step: str
    note: Optional[str] = None

class WorkflowStepResponse(BaseModel):
    id: str
    step: str
    user_id: str
    timestamp: datetime
    note: Optional[str]
    class Config:
        orm_mode = True

class TaskDepartmentCreate(BaseModel):
    title: str
    description: str
    department_ids: List[str]
    due_date: Optional[datetime] = None

@router.post("/", response_model=TaskResponse)
def create_task(task: TaskCreate, user=Depends(require_roles("superadmin", "manager", "operations_manager")), db: Session = Depends(get_db)):
    new_task = Task(
        title=task.title,
        description=task.description,
        status=TaskStatusEnum.red,
        created_by=user.id,
        assigned_to=task.assigned_to,
        department_id=task.department_id,
        due_date=task.due_date
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    # ثبت اولین مرحله گردش کار
    step = WorkflowStep(
        task_id=new_task.id,
        step="created",
        user_id=user.id,
        note="ایجاد تسک"
    )
    db.add(step)
    db.commit()
    return new_task

@router.get("/", response_model=List[TaskResponse])
def list_tasks(user=Depends(get_current_user), db: Session = Depends(get_db)):
    # نمایش تسک‌های مرتبط با نقش و دپارتمان کاربر
    if user.role and user.role.name in ["superadmin", "manager"]:
        tasks = db.query(Task).all()
    else:
        tasks = db.query(Task).filter(Task.department_id == user.department_id).all()
    return tasks

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    # فقط نقش مجاز یا دپارتمان مرتبط ببیند
    if user.role and user.role.name not in ["superadmin", "manager"] and task.department_id != user.department_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: str, update: TaskUpdate, user=Depends(require_roles("superadmin", "manager", "operations_manager")), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for field, value in update.dict(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}")
def delete_task(task_id: str, user=Depends(require_roles("superadmin", "manager")), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted"}

@router.post("/department", response_model=List[TaskResponse])
def create_task_for_departments(data: TaskDepartmentCreate, user=Depends(require_roles("superadmin", "manager")), db: Session = Depends(get_db)):
    tasks = []
    for dep_id in data.department_ids:
        task = Task(
            title=data.title,
            description=data.description,
            status=TaskStatusEnum.red,
            created_by=user.id,
            department_id=dep_id,
            due_date=data.due_date
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        tasks.append(task)
    return tasks

@router.get("/department/{department_id}", response_model=List[TaskResponse])
def list_tasks_by_department(department_id: str, db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.department_id == department_id).all()
    return tasks

@router.post("/{task_id}/workflow", response_model=WorkflowStepResponse)
def add_workflow_step(task_id: str, step: WorkflowStepCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    # فقط نقش مجاز یا دپارتمان مرتبط
    if user.role and user.role.name not in ["superadmin", "manager"] and task.department_id != user.department_id:
        raise HTTPException(status_code=403, detail="Access denied")
    workflow_step = WorkflowStep(
        task_id=task.id,
        step=step.step,
        user_id=user.id,
        note=step.note
    )
    db.add(workflow_step)
    # وضعیت تسک را بر اساس مرحله جدید به‌روزرسانی کن
    if step.step in ["completed", "green"]:
        task.status = TaskStatusEnum.green
    elif step.step in ["yellow_warning", "yellow"]:
        task.status = TaskStatusEnum.yellow
    elif step.step in ["returned", "rejected"]:
        task.status = TaskStatusEnum.returned
    else:
        task.status = TaskStatusEnum.red
    db.commit()
    db.refresh(workflow_step)
    return workflow_step

@router.get("/{task_id}/workflow", response_model=List[WorkflowStepResponse])
def get_workflow_steps(task_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if user.role and user.role.name not in ["superadmin", "manager"] and task.department_id != user.department_id:
        raise HTTPException(status_code=403, detail="Access denied")
    steps = db.query(WorkflowStep).filter(WorkflowStep.task_id == task_id).order_by(WorkflowStep.timestamp).all()
    return steps 