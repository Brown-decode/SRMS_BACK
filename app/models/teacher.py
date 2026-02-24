from sqlalchemy import Column, Integer, ForeignKey
from app.db.database import Base



class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))


