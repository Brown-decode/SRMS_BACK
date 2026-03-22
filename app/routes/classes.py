from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.class_model import Class
from app.schemas.class_schema import ClassCreateRequest, ClassCreateResponse
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User, UserRole
from app.models.class_subject import ClassSubject
from sqlalchemy.exc import SQLAlchemyError
from app.services.result_service import compute_class_results
from app.schemas.student import StudentResponse, StudentReportCard

class_router = APIRouter(prefix="/classes", tags=["class"])


@class_router.post("/", status_code=201, response_model=ClassCreateResponse)
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


@class_router.get("/", response_model=list[ClassCreateResponse])
async def get_classes(
    current_user: User = Depends(require_admin), db: Session = Depends(get_db)
):
    classes = db.query(Class).all()
    return classes


@class_router.get("/{class_id}/students", response_model=list[StudentResponse])
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
    elif current_user.role == UserRole.ADMIN or current_user.role == UserRole.SUPERUSER:
        _class = db.query(Class).filter(Class.id == class_id).first()
        if not _class:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Class not found."
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view students in this class.",
        )
    # This part runs for both Admin (after check) and Teacher (if assigned)
    _class = db.query(Class).filter(Class.id == class_id).first()
    if not _class:
        raise HTTPException(status_code=404, detail="Class not found")
    to_return = []
    for student in _class.students:
        to_return.append(
            {
                "id": student.id,
                "matricule": student.matricule,
                "class_id": student.class_id,
                "gender": student.gender,
                "date_of_birth": student.date_of_birth,
                "user_id": student.user_id,
                "full_name": student.user.full_name,
            }
        )

    return to_return


@class_router.get("/{class_id}/results", response_model=list[StudentReportCard])
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
