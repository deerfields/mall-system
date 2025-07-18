from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import Survey, SurveyResponse
from ..app import get_db
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json

router = APIRouter(prefix="/api/reports", tags=["reports"])

class SurveyCreate(BaseModel):
    title: str
    questions: list

class SurveyResponseCreate(BaseModel):
    survey_id: str
    customer_name: Optional[str]
    answers: list

class SurveyOut(BaseModel):
    id: str
    title: str
    questions: list
    created_at: datetime
    class Config:
        orm_mode = True

class SurveyResponseOut(BaseModel):
    id: str
    survey_id: str
    customer_name: Optional[str]
    answers: list
    submitted_at: datetime
    class Config:
        orm_mode = True

@router.post("/survey", response_model=SurveyOut)
def create_survey(data: SurveyCreate, db: Session = Depends(get_db)):
    survey = Survey(title=data.title, questions=json.dumps(data.questions))
    db.add(survey)
    db.commit()
    db.refresh(survey)
    return SurveyOut(id=survey.id, title=survey.title, questions=json.loads(survey.questions), created_at=survey.created_at)

@router.get("/survey", response_model=List[SurveyOut])
def list_surveys(db: Session = Depends(get_db)):
    surveys = db.query(Survey).all()
    return [SurveyOut(id=s.id, title=s.title, questions=json.loads(s.questions), created_at=s.created_at) for s in surveys]

@router.post("/survey/response", response_model=SurveyResponseOut)
def submit_survey_response(data: SurveyResponseCreate, db: Session = Depends(get_db)):
    survey = db.query(Survey).filter(Survey.id == data.survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    response = SurveyResponse(survey_id=data.survey_id, customer_name=data.customer_name, answers=json.dumps(data.answers))
    db.add(response)
    db.commit()
    db.refresh(response)
    return SurveyResponseOut(id=response.id, survey_id=response.survey_id, customer_name=response.customer_name, answers=json.loads(response.answers), submitted_at=response.submitted_at)

@router.get("/survey/{survey_id}/responses", response_model=List[SurveyResponseOut])
def get_survey_responses(survey_id: str, db: Session = Depends(get_db)):
    responses = db.query(SurveyResponse).filter(SurveyResponse.survey_id == survey_id).all()
    return [SurveyResponseOut(id=r.id, survey_id=r.survey_id, customer_name=r.customer_name, answers=json.loads(r.answers), submitted_at=r.submitted_at) for r in responses] 