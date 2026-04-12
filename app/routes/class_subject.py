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
            status_code=400, detail="subject already exists for specified class"
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


@class_subject_router.get("/check-conflict")
async def check_assignment_conflict(
    teacher_id: int,
    class_id: int,
    subject_id: int,
    exclude_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if assignment already exists (for conflict detection)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required for conflict checking."
        )
    
    # Build query for existing assignment
    query = db.query(ClassSubject).filter(
        ClassSubject.teacher_id == teacher_id,
        ClassSubject.class_id == class_id,
        ClassSubject.subject_id == subject_id
    )
    
    # Exclude specific ID if provided (for updates)
    if exclude_id:
        query = query.filter(ClassSubject.id != exclude_id)
    
    existing = query.first()
    return {"conflict": existing is not None}


@class_subject_router.post("/bulk")
async def bulk_create_assignments(
    assignments: List[ClassSubjectCreateRequest],
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Bulk create multiple class-subject assignments"""
    if not assignments:
        raise HTTPException(
            status_code=400,
            detail="No assignments provided for bulk creation."
        )
    
    created_count = 0
    failed_count = 0
    errors = []
    
    for assignment_data in assignments:
        try:
            # Check for existing assignment
            existing = db.query(ClassSubject).filter(
                ClassSubject.teacher_id == assignment_data.teacher_id,
                ClassSubject.class_id == assignment_data.class_id,
                ClassSubject.subject_id == assignment_data.subject_id
            ).first()
            
            if existing:
                failed_count += 1
                errors.append(f"Assignment already exists for teacher {assignment_data.teacher_id}")
                continue
            
            # Create new assignment
            new_assignment = ClassSubject(**assignment_data.model_dump())
            db.add(new_assignment)
            created_count += 1
            
        except Exception as e:
            failed_count += 1
            errors.append(f"Failed to create assignment: {str(e)}")
    
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to commit bulk assignments."
        )
    
    return {
        "created": created_count,
        "failed": failed_count,
        "errors": errors
    }


@class_subject_router.get("/export/csv")
async def export_assignments_csv(
    teacher_id: int = None,
    class_id: int = None,
    subject_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export class-subject assignments to CSV"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required for export."
        )
    
    # Build query based on filters
    query = db.query(ClassSubject)
    if teacher_id:
        query = query.filter(ClassSubject.teacher_id == teacher_id)
    if class_id:
        query = query.filter(ClassSubject.class_id == class_id)
    if subject_id:
        query = query.filter(ClassSubject.subject_id == subject_id)
    
    assignments = query.all()
    
    if not assignments:
        raise HTTPException(
            status_code=404,
            detail="No assignments found for export."
        )
    
    # Create CSV content
    import io
    import csv
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(["Teacher ID", "Class ID", "Subject ID", "Coefficient"])
    
    # Write data
    for assignment in assignments:
        writer.writerow([
            assignment.teacher_id,
            assignment.class_id,
            assignment.subject_id,
            assignment.coefficient
        ])
    
    # Create response
    output.seek(0)
    from fastapi.responses import StreamingResponse
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=class_subject_assignments.csv"}
    )
