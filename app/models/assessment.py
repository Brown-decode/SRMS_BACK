from sqlalchemy import Column, Integer, Enum as SqlAlchemyEnum
from app.db.database import Base
from enum import Enum

class AssessmentName(str, Enum):
    SEQUENCE1 = "SEQUENCE 1"
    EXAM = "EXAM"
    
    
class Assessment(Base):
    __tablename__ = "assessments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(SqlAlchemyEnum(AssessmentName), unique=True, index=True)
    weight_percentage = Column(Integer, nullable=False)