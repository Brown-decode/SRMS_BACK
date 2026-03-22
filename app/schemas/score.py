from pydantic import BaseModel


class ScoreCreate(BaseModel):
    student_id: int
    score: float

    class Config:
        from_attributes = True


class ScoreBulkCreate(BaseModel):
    scores: list[ScoreCreate]

    class Config:
        from_attributes = True


class ScoreBulkCreateResponse(BaseModel):
    message: str
    count: int

    class Config:
        from_attributes = True
