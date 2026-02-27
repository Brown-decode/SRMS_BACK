from sqlalchemy import Column, Float, Integer, ForeignKey, CheckConstraint
from app.db.database import Base


class Score(Base):
    __tablename__ = "scores"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    score = Column(Float, CheckConstraint("score >= 0 and score <= 20"))
    class_subject_id = Column(Integer, ForeignKey("class_subjects.id"))
    term = Column(Integer, CheckConstraint("term >= 1 and term <= 3"))