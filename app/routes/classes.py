from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.class_model import Class
from app.schemas.class_schema import ClassCreateRequest
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User, UserRole
from app.models.teacher import Teacher
from app.models.class_subject import ClassSubject
from app.models.student import Student
from sqlalchemy.exc import SQLAlchemyError
from app.services.result_service import compute_class_results

class_router = APIRouter(prefix="/classes", tags=["class"])


@class_router.post("/")
async def create_class(
    class_: ClassCreateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    class_check = db.query(Class).filter(Class.name == class_.name).first()
    if class_check:
        raise HTTPException(status_code=400, detail="Class already exists")
    _class = Class(**class_.model_dump())
    try:
        db.add(_class)
        db.commit()
        db.refresh(_class)
        return _class
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create class")


@class_router.get("/")
async def get_classes(
    current_user: User = Depends(require_admin), db: Session = Depends(get_db)
):
    classes = db.query(Class).all()
    return classes


@class_router.get("/{class_id}/students")
async def get_class_students(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == UserRole.TEACHER:
        teacher = current_user.teacher
        # Check if the teacher is assigned to any subject in this class
        is_assigned = (
            db.query(ClassSubject)
            .filter(
                ClassSubject.teacher_id == teacher.id, ClassSubject.class_id == class_id
            )
            .first()
        )
        if not is_assigned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not assigned to this class.",
            )
    elif current_user.role == UserRole.ADMIN:
        _class = db.query(Class).filter(Class.id == class_id).first()
        if not _class:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Class not found."
            )
        return _class.students
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view students in this class.",
        )
    # This part runs for both Admin (after check) and Teacher (if assigned)
    _class = db.query(Class).filter(Class.id == class_id).first()
    if not _class:
        raise HTTPException(status_code=404, detail="Class not found")
    return _class.students


@class_router.get("/{class_id}/results")
async def get_class_results(
    class_id: int,
    term: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. Permission Check
    if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
        raise HTTPException(status_code=403, detail="Not authorized")

    return compute_class_results(db, class_id, term)
