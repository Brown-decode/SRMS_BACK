from fastapi import APIRouter
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.core.security import authenticate_user
from fastapi import Depends, HTTPException
from app.core.security import create_access_token
from app.models.user import User, UserRole
from app.schemas.user import AdminCreate, LoginResponse, UserResponse
from fastapi.security import OAuth2PasswordRequestForm
from app.core.dependencies import require_superuser,require_admin, get_current_user
from app.core.security import get_password_hash


auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/login", response_model=LoginResponse)
async def login(
    data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):

    user = authenticate_user(db, data.username, data.password)

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token({"sub": user.loginid}, user.role)

    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    return current_user

@auth_router.get("/users", response_model=list[UserResponse])
async def get_users(
    current_user: User = Depends(require_admin), db: Session = Depends(get_db)
):
    users = db.query(User).all()
    return users


@auth_router.post("/admin", response_model=UserResponse, status_code=201)
async def create_admin(
    admin: AdminCreate,
    current_user: User = Depends(require_superuser),
    db: Session = Depends(get_db),
):

    check = db.query(User).filter(User.loginid == admin.email).first()
    if check:
        raise HTTPException(status_code=400, detail="User already exists")

    try:
        user = User(
            full_name=admin.full_name,
            loginid=admin.email,
            password_hash=get_password_hash(admin.password),
            role=UserRole.ADMIN,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user info including role"""
    return current_user
