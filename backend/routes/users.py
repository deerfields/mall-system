from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .auth import require_roles, get_current_user, get_db
from ..models import User, Role, Department
from pydantic import BaseModel

router = APIRouter(prefix="/api/users", tags=["users"])

class UserCreate(BaseModel):
    username: str
    password: str
    role_id: str
    department_id: str

class UserUpdate(BaseModel):
    password: str = None
    role_id: str = None
    department_id: str = None
    is_active: str = None

@router.get("/")
def list_users(user=Depends(require_roles("superadmin", "manager")), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "role": db.query(Role).filter(Role.id == u.role_id).first().name if u.role_id else None,
            "department": db.query(Department).filter(Department.id == u.department_id).first().name if u.department_id else None,
            "is_active": u.is_active
        } for u in users
    ]

@router.post("/")
def create_user(new_user: UserCreate, user=Depends(require_roles("superadmin")), db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == new_user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    role = db.query(Role).filter(Role.id == new_user.role_id).first()
    department = db.query(Department).filter(Department.id == new_user.department_id).first()
    if not role or not department:
        raise HTTPException(status_code=400, detail="Invalid role or department")
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user_obj = User(
        username=new_user.username,
        password_hash=pwd_context.hash(new_user.password),
        role_id=role.id,
        department_id=department.id
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return {"id": user_obj.id, "username": user_obj.username}

@router.put("/{user_id}")
def update_user(user_id: str, update_data: UserUpdate, user=Depends(require_roles("superadmin")), db: Session = Depends(get_db)):
    user_obj = db.query(User).filter(User.id == user_id).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    if update_data.password:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        user_obj.password_hash = pwd_context.hash(update_data.password)
    if update_data.role_id:
        user_obj.role_id = update_data.role_id
    if update_data.department_id:
        user_obj.department_id = update_data.department_id
    if update_data.is_active is not None:
        user_obj.is_active = update_data.is_active
    db.commit()
    db.refresh(user_obj)
    return {"id": user_obj.id, "username": user_obj.username}

@router.delete("/{user_id}")
def delete_user(user_id: str, user=Depends(require_roles("superadmin")), db: Session = Depends(get_db)):
    user_obj = db.query(User).filter(User.id == user_id).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user_obj)
    db.commit()
    return {"detail": "User deleted"} 