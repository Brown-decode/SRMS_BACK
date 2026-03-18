from sqlalchemy import Column, Float, Integer, ForeignKey
from app.db.database import Base
from sqlalchemy.orm import relationship


class ClassSubject(Base):
    __tablename__ = "class_subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"))
    subject_id = Column(Integer, ForeignKey("subjects.id",ondelete="CASCADE"))
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"))
    coefficient = Column(Float)
    
    class_ = relationship("Class", back_populates="class_subjects")
    subject = relationship("Subject", back_populates="class_subjects")
    teacher = relationship("Teacher", back_populates="class_subjects")
    assessments = relationship("Assessment", back_populates="class_subject")