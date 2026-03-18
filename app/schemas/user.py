from pydantic import BaseModel, EmailStr
from app.models.user import UserRole

class UserCreate(BaseModel):
    full_name: str
    loginid: str
    
    class Config:
        from_attributes = True

class AdminCreate(BaseModel):   
    full_name: str
    email: EmailStr
    password: str
    
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    full_name: str
    loginid: str
    role: UserRole
    is_active: bool
    
    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    
    class Config:
        from_attributes = True

class TokenData(BaseModel):
    loginid: str
    role: str
    
    class Config:
        from_attributes = True