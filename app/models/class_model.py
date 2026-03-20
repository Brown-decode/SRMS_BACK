from sqlalchemy import Column, Integer, String, Enum as SqlAlchemyEnum
from app.db.database import Base
from enum import Enum
from sqlalchemy.orm import relationship


class Cycle(str, Enum):
    FIRST_CYCLE = "First_Cycle"
    SECOND_CYCLE = "Second_Cycle"
    
class Stream(str, Enum):
    ARTS = "ARTS"
    SCIENCE = "SCIENCE"
    COMMERCIAL = "COMMERCIAL"
    NONE = "NONE"

class Class(Base):
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    level = Column(SqlAlchemyEnum(Cycle), index=True)
    stream = Column(SqlAlchemyEnum(Stream), index=True)
    
    students = relationship("Student", back_populates="class_")
    class_subjects = relationship("ClassSubject", back_populates="class_")