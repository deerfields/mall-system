from fastapi import FastAPI, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from .models import Base, Task, StatusEnum, User, Contract, Payment, Shop, SecurityLog
from datetime import datetime
from .routes import shops, reports, cctv
from .routes import contracts
from .routes import permits
from prometheus_fastapi_instrumentator import Instrumentator

DATABASE_URL = "sqlite:///../database/mall.db"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mall System", version="1.0.0")
app.include_router(shops.router)
app.include_router(reports.router)
app.include_router(cctv.router)
app.include_router(contracts.router)
app.include_router(permits.router)
Instrumentator().instrument(app).expose(app)

class TaskCreate(BaseModel):
    title: str

class TaskResponse(BaseModel):
    id: str
    title: str
    status: StatusEnum

    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    new_task = Task(title=task.title)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.get("/api/tasks", response_model=list[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return tasks

@app.get("/api/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    active_users = db.query(User).filter(User.is_active == "1").count()
    active_contracts = db.query(Contract).filter(Contract.status == "active").count()
    open_tasks = db.query(Task).filter(Task.status != "green").count()
    security_events = db.query(SecurityLog).count()
    return {
        "active_users": active_users,
        "active_contracts": active_contracts,
        "open_tasks": open_tasks,
        "security_events": security_events
    } 