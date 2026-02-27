from app.db.database import Base
from sqlalchemy import Column, Integer, String, Boolean, Enum as SqlAlchemyEnum
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    loginid = Column(String, unique=True, index=True)
    password_hash = Column(String, nullable = False)
    role = Column(SqlAlchemyEnum(UserRole), nullable = False)
    is_active = Column(Boolean, default=True)
    
    class config:
        from_attributes = True