from pydantic import BaseModel, EmailStr

class StudentCreate(BaseModel):
    matricule: str
    class_id: int
    date_of_birth: str
    gender: str
    full_name: str


    