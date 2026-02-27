from pydantic import BaseModel


class ClassSubjectCreateRequest(BaseModel):
    class_id: int
    subject_id: int
    teacher_id: int
    coefficient: float

    class Config:
        from_attributes = True


