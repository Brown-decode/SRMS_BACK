from fastapi import APIRouter, Depends, HTTPException
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.models.teacher import Teacher
from app.schemas.teacher import TeacherCreateRequest
from app.schemas.user import UserCreate
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from fastapi import HTTPException, Depends
from sqlalchemy.exc import SQLAlchemyError

teacher_router = APIRouter(prefix="/teacher", tags= ["teacher"])


@teacher_router.post("/create")
def create_teacher(user: UserCreate, teacher: TeacherCreateRequest, db: Session = Depends(get_db)):
    user_check = db.query(User).filter(User.loginid == user.loginid).first()
    if user_check:
        raise HTTPException(status_code=400, detail="Teacher already exists")
    new_user = User(
        full_name=user.full_name,
        loginid=user.loginid,
        password_hash=get_password_hash(user.loginid),
        role=UserRole.TEACHER,
    )
    new_teacher = Teacher(
        user_id=new_user.id,
    )
    try:
        db.add(new_user)
        db.add(new_teacher)

        db.commit()

        db.refresh(new_user)
        db.refresh(new_teacher)

        return {"user": new_user, "teacher": new_teacher}
    except Exception:
        db.rollback()
        raise