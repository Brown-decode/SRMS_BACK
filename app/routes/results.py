from fastapi import APIRouter, Depends
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.schemas.student import StudentReportCard
from app.models.class_model import Class
from app.core.dependencies import require_admin
from app.models.user import User
from app.services.result_service import compute_class_results
from sqlalchemy.orm import joinedload
from app.models.student import Student
from app.models.class_subject import ClassSubject
from app.models.score import Score
from app.models.assessment import Assessment


result_router = APIRouter(prefix="/results", tags=["results"])


@result_router.get("/", response_model=list[StudentReportCard])
async def get_results(
    current_user: User = Depends(require_admin), db: Session = Depends(get_db)
):
    # 1. PRE-FETCH STAGE (The "Magic" part)
    # We fetch EVERYTHING for the whole school/class in 3 big queries.
    # We don't even need to assign them to variables; just executing them
    # puts them into the 'db' session's cache.

    db.query(Student).options(joinedload(Student.user)).all()
    db.query(ClassSubject).options(joinedload(ClassSubject.subject)).all()

    # This loads every score for every student into the RAM of your Python app
    db.query(Score).all()
    classes = db.query(Class).all()

    # --- START OF THE NO-PAIN OPTIMIZATION ---
    # We fetch these once to put them in SQLAlchemy's internal Identity Map.
    # Your helper functions will now find these in memory instantly.
    db.query(Student).options(joinedload(Student.user)).all()
    db.query(ClassSubject).options(joinedload(ClassSubject.subject)).all()
    db.query(Assessment).all()
    db.query(Score).all()
    # --- END OF OPTIMIZATION ---

    to_return = []
    for _class in classes:
        to_return.extend(
            compute_class_results(db, _class.id, 1)
            + compute_class_results(db, _class.id, 2)
            + compute_class_results(db, _class.id, 3)
        )
    return to_return
