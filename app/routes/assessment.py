from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
assessment_router = APIRouter(prefix="/assessment")
from app.schemas.assessment import AssessmentCreateRequest
from app.models.assessment import Assessment

@assessment_router.post("/create", tags=["assessment"])
def create_assessment(assessment:AssessmentCreateRequest, db: Session = Depends(get_db)):
    assessment_dict = db.query(Assessment).filter(Assessment.name == assessment.name).first()
    if assessment_dict: 
        raise HTTPException(status_code=400, detail="Assessment with this name already exists")
    
    new_assessment = Assessment(**assessment.model_dump())
    
    db.add(new_assessment)
    db.commit()
    db.refresh(new_assessment)
    return new_assessment