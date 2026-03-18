from fastapi import APIRouter
from app.db.session import get_db
from app.schemas.user import LoginRequest
from sqlalchemy.orm import Session
from app.core.security import authenticate_user
from fastapi import Depends, HTTPException
from app.core.security import create_access_token
from app.models.user import User, UserRole
from app.schemas.user import AdminCreate
from app.core.security import get_password_hash
from fastapi.security import OAuth2PasswordRequestForm

auth_router = APIRouter(prefix="/auth", tags=["auth"])



@auth_router.post("/login")
async def login(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    user = authenticate_user(db, data.username, data.password)
    
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token({"sub": user.loginid}, user.role)
    
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.get("/users")
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@auth_router.post("/Admin")
async def create_admin(user: AdminCreate, db: Session = Depends(get_db)):
    new_user = User(full_name=user.full_name, 
                    loginid=user.email, 
                    password_hash= get_password_hash(user.password),
                    role= UserRole.ADMIN)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"user": new_user}