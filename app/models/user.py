from app.db.database import Base
from sqlalchemy import Column, Integer, String, Boolean, Enum as SqlAlchemyEnum
from enum import Enum
from sqlalchemy.orm import relationship

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"
    SUPERUSER = "SUPERUSER"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    loginid = Column(String, unique=True, index=True)
    password_hash = Column(String, nullable = False)
    role = Column(SqlAlchemyEnum(UserRole), nullable = False)
    is_active = Column(Boolean, default=True)
    
    student = relationship("Student", back_populates="user")
    teacher = relationship("Teacher", back_populates="user")
    
        
    
    
    