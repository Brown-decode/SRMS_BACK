from fastapi import APIRouter
from app.db.database import Session, get_db
from app.schemas.student import StudentCreate
from app.schemas.user import UserCreate
from app.models.student import Student
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from fastapi import HTTPException, Depends



student_router = APIRouter(prefix="/student")

@student_router.post("/create")
async def create_student(user: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.loginid == user.loginid).first()
    if user is None:
        raise HTTPException(status_code=400, detail="Student already exists")
    new_user = user(
        full_name=user.full_name,
        loginid=user.loginid,
        password_hash=get_password_hash(user.password),
        role=UserRole.STUDENT
    )
    new_student = Student(
        matricule=user.matricule,
        class_id=user.class_id,
        date_of_birth=user.date_of_birth,
        gender=user.gender
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"user": new_user, "student": new_student}

@student_router.get("/all", response_model=list[Student])
async def get_all_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return students