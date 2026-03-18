from pydantic import BaseModel

class ScoreCreate(BaseModel):
    student_id: int
    score: int
    
    class Config:
        from_attributes = True
    
class ScoreBulkCreate(BaseModel):
    scores: list[ScoreCreate]
    
    class Config:
        from_attribtes = True
        
        