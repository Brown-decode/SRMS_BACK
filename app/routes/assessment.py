from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.assessment import (
    AssessmentCreateRequest,
    AssessmentCreateResponse,
    AssessmentScoresResponse,
)
from app.models.assessment import Assessment
from app.core.dependencies import get_current_user, require_admin, require_teacher
from app.models.user import User, UserRole
from sqlalchemy.exc import SQLAlchemyError
from app.models.teacher import Teacher
from app.models.class_subject import ClassSubject
from app.schemas.score import ScoreBulkCreate, ScoreBulkCreateResponse
from app.models.score import Score
from app.models.student import Student


assessment_router = APIRouter(prefix="/assessment", tags=["assessment"])


@assessment_router.post("/", response_model=AssessmentCreateResponse, status_code=201)
async def create_assessment(
    assessment: AssessmentCreateRequest,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    assessment_check = (
        db.query(Assessment)
        .filter(
            Assessment.title == assessment.title,
            Assessment.class_subject_id == assessment.class_subject_id,
            Assessment.sequence == assessment.sequence,
        )
        .first()
    )
    if assessment_check:
        raise HTTPException(
            status_code=400, detail="Assessment already exists for this sequence"
        )
    new_assessment = Assessment(**assessment.model_dump())
    try:
        db.add(new_assessment)
        db.commit()
        db.refresh(new_assessment)
        return new_assessment
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create assessment")


@assessment_router.get("/", response_model=list[AssessmentCreateResponse])
async def get_assessments(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    if current_user.role == UserRole.ADMIN or current_user.role == UserRole.SUPERUSER:
        assessments = db.query(Assessment).all()
        return assessments
    if current_user.role == UserRole.TEACHER:
        teacher = current_user.teacher
        assessments = [
            assessment for cs in teacher.class_subjects for assessment in cs.assessments
        ]

    return assessments


@assessment_router.get("/{assessment_id}", response_model=AssessmentCreateResponse)
async def get_assessment(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == UserRole.ADMIN or current_user.role == UserRole.SUPERUSER:
        assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        return assessment
    elif current_user.role == UserRole.TEACHER:
        teacher = current_user.teacher
        assessment = (
            db.query(Assessment)
            .join(ClassSubject)
            .join(Teacher)
            .filter(Assessment.id == assessment_id, Teacher.id == teacher.id)
            .first()
        )
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        return assessment


@assessment_router.delete("/{assessment_id}")
async def delete_assessment(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == UserRole.ADMIN or current_user.role == UserRole.SUPERUSER:
        assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        try:
            db.delete(assessment)
            db.commit()
            return {"detail": "Assessment deleted successfully"}
        except SQLAlchemyError:
            db.rollback()
            raise HTTPException(status_code=500, detail="Failed to delete assessment")
    elif current_user.role == UserRole.TEACHER:
        teacher = current_user.teacher
        assessment = (
            db.query(Assessment)
            .join(ClassSubject)
            .join(Teacher)
            .filter(Assessment.id == assessment_id, Teacher.id == teacher.id)
            .first()
        )
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        try:
            db.delete(assessment)
            db.commit()
            return {"detail": "Assessment deleted successfully"}
        except SQLAlchemyError:
            db.rollback()
            raise HTTPException(status_code=500, detail="Failed to delete assessment")


@assessment_router.put("/{assessment_id}", response_model=AssessmentCreateResponse)
async def update_assessment(
    assessment_id: int,
    assessment: AssessmentCreateRequest,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    teacher = current_user.teacher

    assessment_to_update = (
        db.query(Assessment)
        .join(ClassSubject)
        .join(Teacher)
        .filter(Assessment.id == assessment_id, Teacher.id == teacher.id)
        .first()
    )
    if not assessment_to_update:
        raise HTTPException(status_code=404, detail="Assessment not found")
    assessment_check = (
        db.query(Assessment)
        .filter(
            Assessment.title == assessment.title,
            Assessment.class_subject_id == assessment.class_subject_id,
            Assessment.sequence == assessment.sequence,
            Assessment.id != assessment_id,
        )
        .first()
    )
    if assessment_check:
        raise HTTPException(
            status_code=400, detail="Assessment already exists for this sequence"
        )
    update_data = assessment.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(assessment_to_update, key, value)

    try:
        db.commit()
        db.refresh(assessment_to_update)
        return assessment_to_update
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update assessment")


@assessment_router.post(
    "/{assessment_id}/scores", response_model=ScoreBulkCreateResponse, status_code=201
)
async def create_scores(
    assessment_id: int,
    payload: ScoreBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher),
):
    teacher = current_user.teacher

    # Verify the teacher owns this assessment
    assessment = (
        db.query(Assessment)
        .join(ClassSubject)
        .join(Teacher)
        .filter(
            Assessment.id == assessment_id,
            Teacher.id == teacher.id,
        )
        .first()
    )

    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    try:
        # Extract student ids from request
        student_ids = [item.student_id for item in payload.scores]

        # Check students already graded in this assessment
        existing_scores = (
            db.query(Score.student_id)
            .filter(
                Score.assessment_id == assessment_id,
                Score.student_id.in_(student_ids),
            )
            .all()
        )

        existing_student_ids = {row[0] for row in existing_scores}

        if existing_student_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Scores already exist for students: {list(existing_student_ids)}",
            )

        # Validate students belong to the same class
        valid_students = (
            db.query(Student.id)
            .filter(
                Student.class_id == assessment.class_subject.class_id,
                Student.id.in_(student_ids),
            )
            .all()
        )

        valid_student_ids = {row[0] for row in valid_students}

        invalid_students = set(student_ids) - valid_student_ids

        if invalid_students:
            raise HTTPException(
                status_code=400,
                detail=f"Students not in this class: {list(invalid_students)}",
            )

        # Create score objects
        scores_to_create = [
            Score(
                student_id=item.student_id,
                assessment_id=assessment_id,
                score=item.score,
            )
            for item in payload.scores
        ]

        # Bulk insert
        db.add_all(scores_to_create)
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to record scores")

    return {
        "message": "Scores recorded successfully",
        "count": len(scores_to_create),
    }


@assessment_router.get("/{assessment_id}/scores")
async def get_assessment_scores(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher),
):
    teacher = current_user.teacher

    # Verify teacher owns the assessment
    assessment = (
        db.query(Assessment)
        .join(ClassSubject)
        .join(Teacher)
        .filter(
            Assessment.id == assessment_id,
            Teacher.id == teacher.id,
        )
        .first()
    )

    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # Get students in the class
    students = (
        db.query(Student)
        .filter(Student.class_id == assessment.class_subject.class_id)
        .all()
    )

    # Get existing scores for the assessment
    scores = db.query(Score).filter(Score.assessment_id == assessment_id).all()

    # Map student_id -> score
    score_map = {score.student_id: score.score for score in scores}

    # Build response
    results = []
    for student in students:
        results.append(
            {
                "student_id": student.id,
                "student_name": student.user.full_name,
                "score": score_map.get(student.id),  # None if not graded
            }
        )

    return {
        "assessment_id": assessment_id,
        "assessment_title": assessment.title,
        "max_score": assessment.max_score,
        "students": results,
    }
