from pydantic import BaseModel
from app.models.user import UserRole

class UserCreate(BaseModel):
    full_name: str
    loginid: str
    
    


class LoginRequest(BaseModel):
    matricule: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    loginid: str
    role: str