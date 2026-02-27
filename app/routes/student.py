from fastapi import APIRouter
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate
from app.schemas.student import StudentCreate, StudentResponse
from app.models.student import Student
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from fastapi import HTTPException, Depends
from sqlalchemy.exc import SQLAlchemyError

student_router = APIRouter(prefix="/student", tags=["student"])


@student_router.post("/create")
async def create_student(user: UserCreate,student: StudentCreate, db: Session = Depends(get_db)):
    user_check = db.query(User).filter(User.loginid == user.loginid).first()
    if user_check:
        raise HTTPException(status_code=400, detail="Student already exists")
    new_user = User(
        full_name=user.full_name,
        loginid=user.loginid,
        password_hash=get_password_hash(user.loginid),
        role=UserRole.STUDENT,
    )
    new_student = Student(
        full_name=user.full_name,
        user_id= new_user.id,
        matricule= new_user.loginid,
        class_id=student.class_id | None,
        date_of_birth=student.date_of_birth,
        gender = student.gender,
    )
    
   
    try:
        db.add(new_user)
        db.add(new_student)

        db.commit()

        db.refresh(new_user)
        db.refresh(new_student)

        return {"user": new_user, "student": new_student}
    except Exception:
        db.rollback()
        raise
    



@student_router.get("/all", response_model=list[StudentResponse])
async def get_all_students(db: Session = Depends(get_db)):
    student_row = db.query(Student).all()
    students = [student(**student.__dict__) for student in student_row]
    return [student.dict() for student in students]
