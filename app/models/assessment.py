from sqlalchemy import Column, Integer, Enum as SqlAlchemyEnum
from app.db.database import Base
from enum import Enum
from sqlalchemy.orm import relationship
from sqlalchemy import String, ForeignKey, Float, Date
from datetime import date
    
class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    class_subject_id = Column(Integer, ForeignKey("class_subjects.id"), nullable=False)
    term = Column(Integer, nullable=False)
    sequence = Column(Integer, nullable=False)
    max_score = Column(Float, nullable=False)
    date = Column(Date, default= date.today, nullable=False)
    weight_percentage = Column(Float, nullable=False)
    
    class_subject = relationship("ClassSubject", back_populates="assessments")
    scores = relationship("Score", back_populates="assessment", cascade="all, delete")