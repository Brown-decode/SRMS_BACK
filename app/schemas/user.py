from pydantic import BaseModel


class UserCreate(BaseModel):
    full_name: str
    matricule: str
    class_id: int
    date_of_birth: str
    gender: str


class LoginRequest(BaseModel):
    matricule: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    loginid: str
    role: str