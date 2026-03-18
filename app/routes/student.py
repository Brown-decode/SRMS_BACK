from fastapi import APIRouter
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate
from app.schemas.student import StudentCreate, StudentResponse, StudentReportCard
from app.models.student import Student
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from fastapi import HTTPException, Depends
from sqlalchemy.exc import SQLAlchemyError
from app.core.dependencies import get_current_user
from app.models.class_subject import ClassSubject
from app.models.class_model import Class
from app.core.dependencies import require_admin, require_student
from app.services.result_service import compute_class_results
from app.schemas.class_schema import ClassCreateResponse


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
    current_user: User = Depends(require_admin), db: Session = Depends(get_db)
):
    students = db.query(Student).all()
    to_return = []
    for student in students:
        to_return.append({**student.__dict__, "full_name": student.user.full_name})
    return to_return


@student_router.get("/{id}", response_model=StudentResponse)
async def get_student_details(
    id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {**student.__dict__, "full_name": student.user.full_name}


@student_router.get("/me", response_model=StudentResponse)
async def get_my_details(
    current_user: User = Depends(require_student), db: Session = Depends(get_db)
):
    student = current_user.student
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {**student.__dict__, "full_name": student.user.full_name}


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


@student_router.delete("/{id}")
async def delete_student(
    id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)
):
    student = current_user.student
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
