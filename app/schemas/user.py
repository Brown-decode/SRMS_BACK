from pydantic import BaseModel, EmailStr


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


class LoginRequest(BaseModel):
    loginid: str
    password: str
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    
    class Config:
        from_attributes = True

class TokenData(BaseModel):
    loginid: str
    role: str
    
    class Config:
        from_attributes = True