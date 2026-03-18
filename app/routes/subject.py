from fastapi import APIRouter, Depends, HTTPException
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.models.subject import Subject
from app.schemas.subject import SubjectCreateRequest, SubjectCreateResponse
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User, UserRole
from sqlalchemy.exc import SQLAlchemyError

subject_router = APIRouter(prefix="/subjects", tags=["subject"])

@subject_router.post("/", response_model= SubjectCreateResponse, status_code=201)
async def create_subject(subject: SubjectCreateRequest,current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admin can create a subject")
    subject_check = db.query(Subject).filter(Subject.name == subject.name).first()
    if subject_check:
        raise HTTPException(status_code=400, detail="Subject already exists")
        
    _subject = Subject(**subject.model_dump())
    try:
        db.add(_subject)
        db.commit()
        db.refresh(_subject)
        return _subject
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create subject")
   

@subject_router.get("/", response_model= list[SubjectCreateResponse])
async def get_subjects(current_user: User = Depends(require_admin),db: Session = Depends(get_db)):    
    subjects = db.query(Subject).all()
    return subjects

@subject_router.get("/{subject_id}", response_model= SubjectCreateResponse)
async def get_subject(subject_id: int, current_user: User = Depends(require_admin),db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject

@subject_router.delete("/{id}")
async def delete_subject(id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
     subject = db.query(Subject).filter(Subject.id == id).first()
     if not subject:
         raise HTTPException(status_code=404, detail="Subject not found")
     try:
         db.delete(subject)
         db.commit()
         return {"detail": "Subject deleted successfully"}
     except SQLAlchemyError:
         db.rollback()
         raise HTTPException(status_code=500, detail="Failed to delete subject")
   