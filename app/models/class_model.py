from sqlalchemy import Column, Integer, String, Enum as SqlAlchemyEnum
from app.db.database import Base
from enum import Enum

class ClassName(Enum): 
    FORM_1 = "Form 1"
    FORM_2 = "Form 2"
    FORM_3 = "Form 3"
    FORM_4 = "Form 4"
    FORM_5 = "Form 5"
    LOWER_SIXTH = "Lower Sixth"
    UPPER_SIXTH = "Upper Sixth"

class Cycle(Enum):
    FIRST_CYCLE = "First Cycle"
    SECOND_CYCLE = "Second Cycle"
    
class Stream(Enum):
    ARTS = "Arts"
    SCIENCE = "Science"
    COMMERCIAL = "Commercial"

class Class(Base):
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(SqlAlchemyEnum(ClassName), unique=True, index=True)
    level = Column(SqlAlchemyEnum(Cycle), index=True)
    stream = Column(SqlAlchemyEnum(Stream), index=True)