from fastapi import FastAPI
from app.routes.auth import auth_router
from app.routes.student import student_router
from app.routes.teacher import teacher_router
app = FastAPI(title="School Results Management System", description="School Results Management System", version="0.0.1")

