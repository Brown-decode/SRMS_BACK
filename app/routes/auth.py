from fastapi import APIRouter
from app.db.session import get_db
from app.schemas.user import LoginRequest
from sqlalchemy.orm import Session
from app.core.security import authenticate_user
from fastapi import Depends, HTTPException
from app.core.security import create_access_token
from app.models.user import User

auth_router = APIRouter(prefix="/auth")



@auth_router.post("/login")
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    
    user = authenticate_user(db, data.loginid, data.password)
    
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token({"sub": user.loginid}, user.role)
    
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.get("/users")
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users