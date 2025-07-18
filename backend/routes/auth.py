from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.orm import Session
from ..models import User, Role, Department, Base
from ..app import get_db
from pydantic import BaseModel
from typing import Optional
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
import os
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

SECRET_KEY = os.environ.get("SECRET_KEY", "secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

router = APIRouter(prefix="/api/auth", tags=["auth"])

# --- Schemas ---
class RegisterRequest(BaseModel):
    username: str
    password: str
    role_id: str
    department_id: str

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MeResponse(BaseModel):
    id: str
    username: str
    role: str
    department: str
    is_active: str
    class Config:
        orm_mode = True

# --- Utils ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None

def get_current_user(token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Middleware/Dependency برای کنترل نقش
def require_roles(*roles):
    def role_checker(user: User = Depends(get_current_user)):
        if not user or not user.role or user.role.name not in roles:
            raise HTTPException(status_code=403, detail="Access denied")
        return user
    return role_checker

# --- Endpoints ---
@router.post("/register", response_model=MeResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db), current_user: User = Depends(lambda: None)):
    # فقط سوپر ادمین می‌تواند ثبت‌نام کند
    if current_user and current_user.role and current_user.role.name != "superadmin":
        raise HTTPException(status_code=403, detail="Access denied")
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    role = db.query(Role).filter(Role.id == req.role_id).first()
    department = db.query(Department).filter(Department.id == req.department_id).first()
    if not role or not department:
        raise HTTPException(status_code=400, detail="Invalid role or department")
    user = User(
        username=req.username,
        password_hash=get_password_hash(req.password),
        role_id=role.id,
        department_id=department.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return MeResponse(
        id=user.id,
        username=user.username,
        role=role.name,
        department=department.name,
        is_active=user.is_active
    )

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    role = db.query(Role).filter(Role.id == user.role_id).first()
    department = db.query(Department).filter(Department.id == user.department_id).first()
    access_token = create_access_token({
        "sub": user.id,
        "role": role.name if role else None,
        "department": department.name if department else None
    })
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=MeResponse)
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == user.role_id).first()
    department = db.query(Department).filter(Department.id == user.department_id).first()
    return MeResponse(
        id=user.id,
        username=user.username,
        role=role.name if role else None,
        department=department.name if department else None,
        is_active=user.is_active
    ) 