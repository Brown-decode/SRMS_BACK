from fastapi import APIRouter, Depends, HTTPException, status
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.models.teacher import Teacher
from app.schemas.user import UserCreate
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from fastapi import HTTPException, Depends
from app.core.dependencies import get_current_user, require_teacher, require_admin
from app.models.user import User
from app.models.class_subject import ClassSubject
from app.models.student import Student
from app.models.class_model import Class
from app.schemas.teacher import TeacherResponse
from sqlalchemy.exc import SQLAlchemyError

teacher_router = APIRouter(prefix="/teachers", tags= ["teacher"])


@teacher_router.post("/")
async def create_teacher(user: UserCreate, current_user: User = Depends(require_admin),db: Session = Depends(get_db)):
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

        return {"user": new_user, "teacher": new_teacher}
    except Exception:
        db.rollback()
        raise
@teacher_router.get("/")
async def get_teachers(current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    teachers = db.query(Teacher).all()
    return teachers

@teacher_router.get("/{id}", response_model=TeacherResponse)
async def get_teacher_by_id(id:int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    teacher = db.query(Teacher).filter(Teacher.id == id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    username = db.query(User).filter(User.id == teacher.user_id).first()
    teacher_response = Teacher(id=teacher.id, user_id=teacher.user_id, username= username.full_name)
    
    return teacher_response
@teacher_router.get("/me/class/{class_id}/subjects")
async def get_my_subjects(class_id: int, current_user: User = Depends(require_teacher), db: Session = Depends(get_db)):
    teacher = current_user.teacher
    _class = db.query(Class).filter(Class.id == class_id).first()
    if not _class:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found.")
    subjects = [cs.subject for cs in teacher.class_subjects if cs.class_id == class_id]    
    if not subjects:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="You have no subject assigned for this class.")
    return subjects
@teacher_router.get("/me/subjects")
async def get_my_subjects(current_user: User = Depends(require_teacher), db: Session = Depends(get_db)):
    teacher = current_user.teacher
    subjects = [cs.subject for cs in teacher.class_subjects]    
    if not subjects:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="You have no subject assigned.")
    return subjects

@teacher_router.get("/me")
async def get_my_details(current_user: User = Depends(require_teacher), db: Session = Depends(get_db)):
    teacher = current_user.teacher
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher

@teacher_router.delete("/{id}")
async def delete_teacher(id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    teacher = current_user.teacher
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
