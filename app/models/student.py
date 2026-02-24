from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum
from app.db.database import Base  
from enum import Enum

class Gender(str, Enum):
    Male = "Male"
    Female = "Female"
class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    matricule = Column(String, unique=True, index=True, nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"))
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    