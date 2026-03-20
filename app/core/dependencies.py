from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.schemas.user import TokenData
from app.db.session import get_db
from app.models.user import User, UserRole

from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        loginid: str = payload.get("sub")
        if loginid is None:
            raise credentials_exception
        token_data = TokenData(loginid=loginid, role=payload.get("role"))
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.loginid == token_data.loginid).first()
    if user is None:
        raise credentials_exception
    if user.is_active == False:
        raise HTTPException(status_code=403, detail="Inactive user")
    return user


def require_teacher(current_user: User = Depends(get_current_user)):
    if current_user.is_active == False:
        raise HTTPException(status_code=403, detail="Inactive user")
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=403, detail="Only teachers can perform this operation"
        )
    return current_user


def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.is_active == False:
        raise HTTPException(status_code=403, detail="Inactive user")
    if current_user.role != UserRole.ADMIN and current_user.role != UserRole.SUPERUSER:
        raise HTTPException(
            status_code=403, detail="Only admins can perform this operation"
        )
    return current_user


def require_student(current_user: User = Depends(get_current_user)):

    if current_user.is_active == False:
        raise HTTPException(status_code=403, detail="Inactive user")
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=403, detail="Only students can perform this operation"
        )
    return current_user


def require_superuser(current_user: User = Depends(get_current_user)):
    if current_user.is_active == False:
        raise HTTPException(status_code=403, detail="Inactive user")
    if current_user.role != UserRole.SUPERUSER:
        raise HTTPException(
            status_code=403, detail="Only super users can perform this operation"
        )
    return current_user
