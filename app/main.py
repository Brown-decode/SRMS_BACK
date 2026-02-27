from fastapi import FastAPI
from app.routes.auth import auth_router
from app.routes.student import student_router
from app.db.database import engine, Base
from app.models.user import User
from app.models.student import Student
from app.models.class_model import Class
from app.models.subject import Subject
from app.models.teacher import Teacher
from app.models.class_subject import ClassSubject
from app.models.assessment import Assessment
from app.models.score import Score

app = FastAPI(title="School Results Management System", description="School Results Management System", version="0.0.1")

app.include_router(auth_router)
app.include_router(student_router)

Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Hello World"}