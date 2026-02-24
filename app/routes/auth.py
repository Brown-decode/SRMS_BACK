from fastapi import APIRouter
from app.db.database import Session, get_db
from app.schemas.user import LoginRequest
from app.core.security import authenticate_user

auth_router = APIRouter(prefix="/auth")



@auth_router.post("/login")
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    
    user = authenticate_user(db, data.loginid, data.password)
    
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token({"sub": user.loginid}, user.role)
    
    return {"access_token": access_token, "token_type": "bearer"}


