from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.models.teacher import Teacher
from app.schemas.user import UserCreate
from app.schemas.teacher import TeacherResponse, TeacherUpdate
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from fastapi import HTTPException, Depends
from app.core.dependencies import get_current_user, require_teacher, require_admin
from app.models.class_subject import ClassSubject
from app.schemas.subject import SubjectCreateResponse
from app.models.student import Student
from app.models.class_model import Class
from app.models.subject import Subject

import io
import csv
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from typing import Optional

teacher_router = APIRouter(prefix="/teachers", tags=["teacher"])


@teacher_router.post("/", response_model=TeacherResponse, status_code=201)
async def create_teacher(
    user: UserCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user_check = db.query(User).filter(User.loginid == user.loginid).first()
    if user_check:
        raise HTTPException(status_code=400, detail="Teacher already exists")
    try:
        new_user = User(
            full_name=user.full_name,
            loginid=user.loginid,
            password_hash=get_password_hash(user.loginid),
            role=UserRole.TEACHER,
        )
        db.add(new_user)
        db.flush()
        new_teacher = Teacher(
            user_id=new_user.id,
        )

        db.add(new_teacher)
        db.commit()

        db.refresh(new_user)
        db.refresh(new_teacher)

        return {
            "id": new_teacher.id,
            "user_id": new_teacher.user_id,
            "loginid": new_user.loginid,
            "full_name": new_user.full_name,
        }
    except Exception:
        db.rollback()
        raise


@teacher_router.get("/", response_model=list[TeacherResponse])
async def get_teachers(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search by name or email"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(25, ge=1, le=100, description="Items per page"),
):
    # Build query with filters
    query = db.query(Teacher).options(joinedload(Teacher.user))

    if search:
        query = query.filter(
            (Teacher.user.has(User.loginid.ilike(f"%{search}%")))
            | (Teacher.user.has(User.full_name.ilike(f"%{search}%")))
        )

    # Get total count for pagination
    total = query.count()

    # Apply pagination
    offset = (page - 1) * limit
    teachers = query.offset(offset).limit(limit).all()

    to_return = []

    for teacher in teachers:
        to_return.append(
            {
                "id": teacher.id,
                "user_id": teacher.user_id,
                "loginid": teacher.user.loginid,
                "full_name": teacher.user.full_name,
            }
        )

    return to_return


@teacher_router.get("/me", response_model=TeacherResponse)
async def get_my_details(
    current_user: User = Depends(require_teacher), db: Session = Depends(get_db)
):
    teacher = current_user.teacher
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return {
        "id": teacher.id,
        "user_id": teacher.user_id,
        "loginid": teacher.user.loginid,
        "full_name": teacher.user.full_name,
    }


@teacher_router.get("/{id}", response_model=TeacherResponse)
async def get_teacher_by_id(
    id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)
):
    teacher = db.query(Teacher).filter(Teacher.id == id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    teacher_response = {
        "id": teacher.id,
        "loginid": teacher.user.loginid,
        "user_id": teacher.user_id,
        "full_name": teacher.user.full_name,
    }
    return teacher_response


@teacher_router.get("/me/class/{class_id}/subjects")
async def get_my_subjects(
    class_id: int,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    teacher = current_user.teacher
    _class = db.query(Class).filter(Class.id == class_id).first()
    if not _class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Class not found."
        )
    subjects = [cs.subject for cs in teacher.class_subjects if cs.class_id == class_id]
    if not subjects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You have no subject assigned for this class.",
        )
    return subjects


@teacher_router.get("/me/subjects", response_model=list[SubjectCreateResponse])
async def get_my_subjects(
    current_user: User = Depends(require_teacher), db: Session = Depends(get_db)
):
    teacher = current_user.teacher
    subjects = [cs.subject for cs in teacher.class_subjects]
    if not subjects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You have no subject assigned.",
        )
    return subjects


@teacher_router.get("/me/class-subjects")
async def get_my_class_subjects(
    current_user: User = Depends(require_teacher), db: Session = Depends(get_db)
):
    teacher = current_user.teacher
    class_subjects = []

    for cs in teacher.class_subjects:
        class_subjects.append(
            {
                "id": cs.id,
                "class_id": cs.class_id,
                "subject_id": cs.subject_id,
                "subject_name": cs.subject.name,
                "class_name": cs.class_.name if cs.class_ else f"Class {cs.class_id}",
                "coefficient": cs.coefficient,
            }
        )

    # Return empty array instead of 404 when no subjects assigned
    return class_subjects


@teacher_router.put("/{id}", response_model=TeacherResponse)
async def update_teacher(
    id: int,
    teacher_data: TeacherUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    teacher = (
        db.query(Teacher)
        .options(joinedload(Teacher.user))
        .filter(Teacher.id == id)
        .first()
    )
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    try:
        # Update user fields
        if teacher_data.full_name is not None:
            teacher.user.full_name = teacher_data.full_name
        if teacher_data.loginid is not None:
            # Check if new loginid is already taken
            existing_user = (
                db.query(User)
                .filter(
                    User.loginid == teacher_data.loginid, User.id != teacher.user.id
                )
                .first()
            )
            if existing_user:
                raise HTTPException(
                    status_code=400, detail="Email/username already exists"
                )
            teacher.user.loginid = teacher_data.loginid

        db.commit()
        db.refresh(teacher)

        return {
            "id": teacher.id,
            "user_id": teacher.user_id,
            "loginid": teacher.user.loginid,
            "full_name": teacher.user.full_name,
        }
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update teacher")


@teacher_router.delete("/{id}")
async def delete_teacher(
    id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)
):
    teacher = (
        db.query(Teacher).filter(Teacher.id == id).first()
    )  # Fixed: use id parameter, not current_user
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    user = db.query(User).filter(User.id == teacher.user_id).first()
    try:
        db.delete(teacher)
        db.delete(user)
        db.commit()
        return {"detail": "Teacher deleted successfully"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete teacher")


@teacher_router.get("/me/export/csv")
async def export_my_classes_csv(
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    # Get teacher's class subjects - same data as the table
    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()

    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    # Get class subjects with basic info
    class_subjects = []
    for cs in teacher.class_subjects:
        # Get class name
        class_obj = db.query(Class).filter(Class.id == cs.class_id).first()
        class_name = class_obj.name if class_obj else f"Class {cs.class_id}"

        # Get subject name
        subject_obj = db.query(Subject).filter(Subject.id == cs.subject_id).first()
        subject_name = subject_obj.name if subject_obj else f"Subject {cs.subject_id}"

        # Get student count
        students = db.query(Student).filter(Student.class_id == cs.class_id).all()

        class_subjects.append(
            {
                "class_id": cs.class_id,
                "class_name": class_name,
                "subject_id": cs.subject_id,
                "subject_name": subject_name,
                "coefficient": cs.coefficient or 0,
                "student_count": len(students),
                "class_average": 0,  # Will be computed in frontend
            }
        )

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header - same as table columns
    writer.writerow(
        ["Class Name", "Subject", "Coefficient", "Students", "Class Average"]
    )

    # Write data
    for cs in class_subjects:
        writer.writerow(
            [
                cs.get("class_name", ""),
                cs.get("subject_name", ""),
                cs.get("coefficient", 0),
                cs.get("student_count", 0),
                "N/A",  # Class average computed in frontend
            ]
        )

    # Create response
    output.seek(0)

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=my_classes.csv"},
    )


@teacher_router.get("/export/csv")
async def export_teachers_csv(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search by name or email"),
):
    # Build query with same filters as get_teachers
    query = db.query(Teacher).options(joinedload(Teacher.user))

    if search:
        query = query.filter(
            (Teacher.user.has(User.loginid.ilike(f"%{search}%")))
            | (Teacher.user.has(User.full_name.ilike(f"%{search}%")))
        )

    teachers = query.all()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(["ID", "Full Name", "Email/Username"])

    # Write data
    for teacher in teachers:
        writer.writerow([teacher.id, teacher.user.full_name, teacher.user.loginid])

    output.seek(0)

    # Create response
    response = StreamingResponse(
        io.StringIO(output.getvalue()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=teachers_export.csv"},
    )

    return response
