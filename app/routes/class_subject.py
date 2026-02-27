from fastapi import APIRouter, Depends, HTTPException
from app.models.class_subject import ClassSubject
from app.schemas.class_subject import ClassSubjectCreateRequest
from sqlalchemy.orm import Session
from app.db.session import get_db

class_subject_router = APIRouter(prefix="/class_subject")

@class_subject_router.post("/create")
def create_class_subject(class_subject: ClassSubjectCreateRequest, db: Session = Depends(get_db)):
    class_subject_check = db.query(ClassSubject).filter(ClassSubject.class_id == class_subject.class_id , ClassSubject.subject_id == class_subject.subject_id).first()
    if class_subject_check:
        raise HTTPException(status_code=400, detail="subject already exists for the specified class")
    _class_subject = ClassSubject(**class_subject.model_dump())
    db.add(_class_subject)
    db.commit()
    db.refresh(_class_subject)
    return _class_subject