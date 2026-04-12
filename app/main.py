from fastapi import FastAPI
from app.routes.auth import auth_router
from app.routes.student import student_router
from app.routes.class_subject import class_subject_router
from app.routes.assessment import assessment_router
from app.routes.classes import class_router
from app.routes.subject import subject_router
from app.routes.teacher import teacher_router
from app.routes.results import result_router
from app.routes.results_pdf import results_pdf_router
from app.routes.class_performance import class_performance_router
from app.db.database import engine, Base
from app import models
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="School Results Management System",
    description="School Results Management System",
    version="0.0.1",
)

origins = [
    "http://localhost:5173",  # Your Vite dev server
    "http://127.0.0.1:5173",  # Alternative local address
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specific list of origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

app.include_router(auth_router)
app.include_router(student_router)
app.include_router(class_subject_router)
app.include_router(assessment_router)
app.include_router(class_router)
app.include_router(subject_router)
app.include_router(teacher_router)
app.include_router(results_pdf_router)
app.include_router(result_router)
app.include_router(class_performance_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
