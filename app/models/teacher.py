from sqlalchemy import Column, Integer, ForeignKey
from app.db.database import Base
from sqlalchemy.orm import relationship


class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    class_subjects = relationship(
        "ClassSubject", back_populates="teacher", cascade="all, delete"
    )
    user = relationship("User", back_populates="teacher")
