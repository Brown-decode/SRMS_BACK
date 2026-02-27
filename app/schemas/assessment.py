from pydantic import BaseModel
from app.models.assessment import AssessmentName

class AssessmentCreateRequest(BaseModel):
    name: AssessmentName
    weight: str