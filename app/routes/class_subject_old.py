from fastapi import APIRouter, Depends, HTTPException, status
from app.models.class_subject import ClassSubject
from app.schemas.class_subject import (
    ClassSubjectCreateRequest,
    ClassSubjectCreateResponse,
)
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User, UserRole
from app.models.teacher import Teacher
from fastapi import Response
from typing import List, Dict, Any
from app.models.student import Student
from app.schemas.student import StudentResponse


class_subject_router = APIRouter(prefix="/class_subject", tags=["class_subject"])


@class_subject_router.post(
    "/", response_model=ClassSubjectCreateResponse, status_code=201
)
async def create_class_subject(
    class_subject: ClassSubjectCreateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    class_subject_check = (
        db.query(ClassSubject)
        .filter(
            ClassSubject.class_id == class_subject.class_id,
            ClassSubject.subject_id == class_subject.subject_id,
        )
        .first()
    )
    if class_subject_check:
        raise HTTPException(
            status_code=400, detail="subject already exists for the specified class"
        )
    _class_subject = ClassSubject(**class_subject.model_dump())
    try:
        db.add(_class_subject)
        db.commit()
        db.refresh(_class_subject)
        return _class_subject
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create class subject")


@class_subject_router.get("/", response_model=list[ClassSubjectCreateResponse])
async def get_class_subjects(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    if current_user.role == UserRole.TEACHER:
        teacher = current_user.teacher
        class_subjects = (
            db.query(ClassSubject).filter(ClassSubject.teacher_id == teacher.id).all()
        )
        return class_subjects
    elif current_user.role == UserRole.ADMIN or current_user.role == UserRole.SUPERUSER:
        class_subjects = db.query(ClassSubject).all()
        return class_subjects
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this operation.",
        )


@class_subject_router.get(
    "/{class_subject_id}", response_model=ClassSubjectCreateResponse
)
async def get_class_subject(
    class_subject_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == UserRole.TEACHER:
        teacher = current_user.teacher
        class_subject = (
            db.query(ClassSubject)
            .filter(
                ClassSubject.teacher_id == teacher.id,
                ClassSubject.id == class_subject_id,
            )
            .first()
        )
        if not class_subject:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not assigned to this class subject.",
            )
        return class_subject
    elif current_user.role == UserRole.ADMIN or current_user.role == UserRole.SUPERUSER:
        class_subject = (
            db.query(ClassSubject).filter(ClassSubject.id == class_subject_id).first()
        )
        if not class_subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Class subject not found."
            )
        return class_subject
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this operation.",
        )
