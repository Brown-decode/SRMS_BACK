from fastapi import APIRouter, Depends, HTTPException
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.models.subject import Subject
from app.schemas.subject import SubjectCreateRequest


subject_router = APIRouter(prefix="/subject")

@subject_router.post("/all")
def create_subject(subject: SubjectCreateRequest, db: Session = Depends(get_db)):
    subject_check = db.query(Subject).filter(Subject.name == subject.name).first()
    if subject_check:
        raise HTTPException(status_code=400, detail="Subject already exists")
        
    _subject = Subject(**subject.model_dump())
    db.add(_subject)
    db.commit()
    db.refresh(_subject)
    return _subject