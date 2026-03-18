from pydantic_settings import BaseSettings
from functools import lru_cache
from app.db.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash
class Settings(BaseSettings):
    ADMIN_PASSWORD: str
    ADMIN_EMAIL: str
  
    class Config:
        env_file = ".env"
        
@lru_cache
def get_admin_settings():
    return Settings()

admin_settings = get_admin_settings()

def seed_superuser():
    db = SessionLocal()

    try:
        existing_superuser = (
            db.query(User)
            .filter(User.role == UserRole.SUPERUSER)
            .first()
        )

        if existing_superuser:
            print("Superuser already exists")
            return

        new_superuser = User(
            full_name="Admin",
            loginid=admin_settings.ADMIN_EMAIL,
            password_hash=get_password_hash(admin_settings.ADMIN_PASSWORD),
            role=UserRole.SUPERUSER
        )

        db.add(new_superuser)
        db.commit()
        db.refresh(new_superuser)
        print("Superuser created successfully")
        
    except Exception as e:
        print(f"Error creating superuser: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_superuser()