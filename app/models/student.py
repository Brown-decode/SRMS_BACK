from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum as SqlAlchemyEnum
from app.db.database import Base  
from enum import Enum
from sqlalchemy.orm import relationship

class Gender(str, Enum):
    Male = "Male"
    Female = "Female"
class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    matricule = Column(String, unique=True, index=True, nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(SqlAlchemyEnum(Gender), nullable=False)
    
    class_ = relationship("Class", back_populates="students")
    scores = relationship("Score", back_populates="student")
    user = relationship("User", back_populates="student")  
    
    
    
    