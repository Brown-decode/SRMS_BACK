from sqlalchemy import Column, Integer, String
from app.db.database import Base
from sqlalchemy.orm import relationship
class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    
    class_subjects = relationship("ClassSubject", back_populates="subject")
    