from fastapi import APIRouter, Depends, HTTPException   
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.class_model import Class
from app.schemas.class_schema import ClassCreateRequest

class_router = APIRouter(prefix="/class")


@class_router.post("/create")
def create_class(class_: ClassCreateRequest, db: Session = Depends(get_db)):
    class_check = db.query(Class).filter(Class.name == class_.name).first()
    if class_check:
        raise HTTPException(status_code=400, detail="Class already exists")
    _class = Class(**class_.model_dump())
    db.add(_class)
    db.commit()
    db.refresh(_class)
