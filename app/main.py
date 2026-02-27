from fastapi import FastAPI
from app.routes.auth import auth_router
from app.routes.student import student_router
from app.routes.class_subject import class_subject_router
from app.routes.assessment import assessment_router
from app.routes.classes import class_router
from app.routes.subject import subject_router
from app.routes.teacher import teacher_router
from app.db.database import engine, Base


app = FastAPI(title="School Results Management System", description="School Results Management System", version="0.0.1")

app.include_router(auth_router)
app.include_router(student_router)
app.include_router(class_subject_router)
app.include_router(assessment_router)
app.include_router(class_router)
app.include_router(subject_router)
app.include_router(teacher_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}