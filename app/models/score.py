from sqlalchemy import Column, Float, Integer, ForeignKey, UniqueConstraint,Index
from app.db.database import Base
from sqlalchemy.orm import relationship 

class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    score = Column(Float, nullable=False)
    
    __table_args__ = (
            UniqueConstraint('student_id', 'assessment_id', name='_student_assessment_uc'),Index("idx_assessment_student", "assessment_id", "student_id")
            )

    student = relationship("Student", back_populates="scores")
    assessment = relationship("Assessment", back_populates="scores")