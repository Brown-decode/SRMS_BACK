from fastapi import APIRouter, Depends, HTTPException, Query, Response
from app.db.session import get_db
from sqlalchemy.orm import Session, joinedload
from app.models.user import User
from app.models.student import Student, Gender
from app.schemas.student import (
    StudentResponse,
    StudentCreate,
    StudentUpdate,
    StudentReportCard,
)
from app.core.dependencies import require_admin, require_student
from datetime import datetime
from typing import Optional, List
from app.core.security import get_password_hash
from fastapi import HTTPException, Depends
from sqlalchemy.exc import SQLAlchemyError
from app.core.dependencies import get_current_user
from app.models.class_subject import ClassSubject
from app.models.class_model import Class
from app.core.dependencies import require_admin, require_student
from app.services.result_service import compute_class_results
from app.schemas.class_schema import ClassCreateResponse
from sqlalchemy.orm import joinedload
from typing import Optional
from fastapi.responses import StreamingResponse
import csv
import io


student_router = APIRouter(prefix="/students", tags=["student"])


@student_router.post("/", response_model=StudentResponse, status_code=201)
async def create_student(
    student_data: StudentCreate,  # Use a single schema for input
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):

    # Assuming matricule is the loginid
    user_check = db.query(User).filter(User.loginid == student_data.matricule).first()
    if user_check:
        raise HTTPException(status_code=400, detail="Student already exists")

    try:
        new_user = User(
            full_name=student_data.full_name,
            loginid=student_data.matricule,
            password_hash=get_password_hash(
                student_data.matricule
            ),  # Default password is matricule
            role=UserRole.STUDENT,
        )

        db.add(new_user)
        db.flush()

        new_student = Student(
            # full_name is now in the User model
            user_id=new_user.id,
            matricule=student_data.matricule,
            class_id=student_data.class_id,
            date_of_birth=student_data.date_of_birth,
            gender=student_data.gender,
        )

        db.add(new_student)
        db.commit()
        db.refresh(new_user)
        db.refresh(new_student)

        return {**new_student.__dict__, "full_name": new_user.full_name}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@student_router.get("/", response_model=list[StudentResponse])
async def get_all_students(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search by name or matricule"),
    class_id: Optional[int] = Query(None, description="Filter by class ID"),
    gender: Optional[str] = Query(None, description="Filter by gender"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(25, ge=1, le=100, description="Items per page"),
):
    # Build query with filters
    query = db.query(Student).options(joinedload(Student.user))

    if search:
        query = query.filter(
            (Student.matricule.ilike(f"%{search}%"))
            | (Student.user.has(User.full_name.ilike(f"%{search}%")))
        )

    if class_id:
        query = query.filter(Student.class_id == class_id)

    if gender:
        query = query.filter(Student.gender == gender)

    # Get total count for pagination
    total = query.count()

    # Apply pagination
    offset = (page - 1) * limit
    students = query.offset(offset).limit(limit).all()

    to_return = []
    for student in students:
        to_return.append(
            {
                "id": student.id,
                "matricule": student.matricule,
                "class_id": student.class_id,
                "gender": student.gender,
                "date_of_birth": student.date_of_birth,
                "user_id": student.user_id,
                "full_name": student.user.full_name,  # Fixed: use student's user, not current_user
            }
        )

    # Return response with pagination metadata in headers
    return to_return


@student_router.get("/me", response_model=StudentResponse)
async def get_my_details(
    current_user: User = Depends(require_student), db: Session = Depends(get_db)
):
    student = current_user.student
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {
        "id": student.id,
        "matricule": student.matricule,
        "class_id": student.class_id,
        "gender": student.gender,
        "date_of_birth": student.date_of_birth,
        "user_id": student.user_id,
        "full_name": current_user.full_name,
    }


@student_router.get("/{id}", response_model=StudentResponse)
async def get_student_details(
    id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {
        "id": student.id,
        "matricule": student.matricule,
        "class_id": student.class_id,
        "gender": student.gender,
        "date_of_birth": student.date_of_birth,
        "user_id": student.user_id,
        "full_name": student.user.full_name,
    }


@student_router.get("/me/class", response_model=ClassCreateResponse)
async def get_my_class(
    current_user: User = Depends(require_student), db: Session = Depends(get_db)
):
    student = current_user.student
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    _class = db.query(Class).filter(Class.id == student.class_id).first()
    if not _class:
        raise HTTPException(status_code=404, detail="Class not found")
    return _class


@student_router.get("/me/results", response_model=StudentReportCard)
async def get_my_results(
    term: int,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    student = current_user.student
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # We need to find the rank, so we compute all results first
    all_results = compute_class_results(db, student.class_id, term)

    # Find the current student's result in the ranked list
    student_report = next(
        (res for res in all_results if res["matricule"] == student.matricule), None
    )

    if not student_report:
        raise HTTPException(
            status_code=404, detail=f"No results found for you in term {term}."
        )

    return student_report


@student_router.put("/{id}", response_model=StudentResponse)
async def update_student(
    id: int,
    student_data: StudentUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    student = (
        db.query(Student)
        .options(joinedload(Student.user))
        .filter(Student.id == id)
        .first()
    )
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    try:
        # Update student fields
        if student_data.class_id is not None:
            student.class_id = student_data.class_id
        if student_data.date_of_birth is not None:
            student.date_of_birth = student_data.date_of_birth
        if student_data.gender is not None:
            student.gender = student_data.gender

        # Update user fields
        if student_data.full_name is not None:
            student.user.full_name = student_data.full_name

        db.commit()
        db.refresh(student)

        return {
            "id": student.id,
            "matricule": student.matricule,
            "class_id": student.class_id,
            "gender": student.gender,
            "date_of_birth": student.date_of_birth,
            "user_id": student.user_id,
            "full_name": student.user.full_name,
        }
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update student")


@student_router.delete("/{id}")
async def delete_student(
    id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)
):
    student = (
        db.query(Student).filter(Student.id == id).first()
    )  # Fixed: use id parameter, not current_user
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    user = db.query(User).filter(User.id == student.user_id).first()
    try:
        db.delete(student)
        db.delete(user)
        db.commit()
        return {"detail": "Student deleted successfully"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete student")


@student_router.get("/export/csv")
async def export_students_csv(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search by name or matricule"),
    class_id: Optional[int] = Query(None, description="Filter by class ID"),
    gender: Optional[str] = Query(None, description="Filter by gender"),
):
    # Build query with same filters as get_all_students
    query = db.query(Student).options(joinedload(Student.user))

    if search:
        query = query.filter(
            (Student.matricule.ilike(f"%{search}%"))
            | (Student.user.has(User.full_name.ilike(f"%{search}%")))
        )

    if class_id:
        query = query.filter(Student.class_id == class_id)

    if gender:
        query = query.filter(Student.gender == gender)

    students = query.all()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(
        ["ID", "Matricule", "Full Name", "Gender", "Date of Birth", "Class ID"]
    )

    # Write data
    for student in students:
        writer.writerow(
            [
                student.id,
                student.matricule,
                student.user.full_name,
                student.gender,
                (
                    student.date_of_birth.strftime("%Y-%m-%d")
                    if student.date_of_birth
                    else ""
                ),
                student.class_id or "",
            ]
        )

    output.seek(0)

    # Create response
    response = StreamingResponse(
        io.StringIO(output.getvalue()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=students_export.csv"},
    )

    return response
