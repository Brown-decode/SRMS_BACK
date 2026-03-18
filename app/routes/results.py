from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import require_admin, require_student, require_teacher, get_current_user
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.models.subject import Subject
from app.models.class_subject import ClassSubject
from app.models.assessment import Assessment
from app.models.score import Score
from app.models.user import User
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.class_model import Class
from app.models.class_subject import ClassSubject


results_router = APIRouter( tags=["results"])

@results_router.get("/students/me/report")
async def get_my_report(
    term: int,
    sequence: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student),
):
    student = current_user.student

    subjects = (
        db.query(Subject)
        .join(ClassSubject)
        .filter(ClassSubject.class_id == student.class_id)
        .all()
    )

    report = []

    for subject in subjects:

        assessments = (
            db.query(Assessment)
            .join(ClassSubject)
            .filter(
                ClassSubject.subject_id == subject.id,
                ClassSubject.class_id == student.class_id,
                Assessment.term == term,
                Assessment.sequence == sequence,
            )
            .all()
        )

        total_score = 0
        total_max = 0

        for assessment in assessments:
            score = (
                db.query(Score)
                .filter(
                    Score.student_id == student.id,
                    Score.assessment_id == assessment.id,
                )
                .first()
            )

            if score:
                total_score += score.score
                total_max += assessment.max_score

        average = None
        if total_max > 0:
            average = round((total_score / total_max) * 20, 2)

        report.append(
            {
                "subject": subject.name,
                "average": average,
            }
        )

    return {
        "student_id": student.id,
        "term": term,
        "sequence": sequence,
        "results": report,
    }
    
@results_router.get("/class-subjects/{class_subject_id}/results")
async def get_class_results(
    class_subject_id: int,
    term: int,
    sequence: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    class_subject = (
        db.query(ClassSubject)
        .filter(ClassSubject.id == class_subject_id)
        .first()
    )

    if not class_subject:
        raise HTTPException(404, "Class subject not found")

    # Teacher ownership check
    if current_user.role == "teacher":
        teacher = current_user.teacher
        if class_subject.teacher_id != teacher.id:
            raise HTTPException(403, "Not allowed to access this class")

    students = (
        db.query(Student)
        .filter(Student.class_id == class_subject.class_id)
        .all()
    )

    assessments = (
        db.query(Assessment)
        .filter(
            Assessment.class_subject_id == class_subject_id,
            Assessment.term == term,
            Assessment.sequence == sequence,
        )
        .all()
    )

    results = []

    for student in students:

        total_score = 0
        total_max = 0

        for assessment in assessments:

            score = (
                db.query(Score)
                .filter(
                    Score.student_id == student.id,
                    Score.assessment_id == assessment.id,
                )
                .first()
            )

            if score:
                total_score += score.score
                total_max += assessment.max_score

        average = None
        if total_max > 0:
            average = round((total_score / total_max) * 20, 2)

        results.append(
            {
                "student_id": student.id,
                "student_name": student.user.full_name,
                "average": average,
            }
        )

    return results

@results_router.get("/class-subjects/{class_subject_id}/ranking")
async def get_class_ranking(
    class_subject_id: int,
    term: int,
    sequence: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    results = await get_class_results(
        class_subject_id=class_subject_id,
        term=term,
        sequence=sequence,
        db=db,
        current_user=current_user,
    )

    ranked = sorted(
        results,
        key=lambda x: x["average"] if x["average"] else 0,
        reverse=True,
    )

    for i, student in enumerate(ranked, start=1):
        student["position"] = i

    return ranked

@results_router.get("/students/{student_id}/subjects/{subject_id}/results")
async def get_student_subject_results(
    student_id: int,
    subject_id: int,
    term: int,
    sequence: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    if current_user.role == "student":
        if current_user.student.id != student_id:
            raise HTTPException(403, "Not allowed")

    assessments = (
        db.query(Assessment)
        .join(ClassSubject)
        .filter(
            ClassSubject.subject_id == subject_id,
            Assessment.term == term,
            Assessment.sequence == sequence,
        )
        .all()
    )

    results = []
    total_score = 0
    total_max = 0

    for assessment in assessments:

        score = (
            db.query(Score)
            .filter(
                Score.student_id == student_id,
                Score.assessment_id == assessment.id,
            )
            .first()
        )

        student_score = score.score if score else None

        if score:
            total_score += score.score
            total_max += assessment.max_score

        results.append(
            {
                "assessment": assessment.title,
                "score": student_score,
                "max_score": assessment.max_score,
            }
        )

    average = None
    if total_max > 0:
        average = round((total_score / total_max) * 20, 2)

    return {
        "student_id": student_id,
        "subject_id": subject_id,
        "average": average,
        "assessments": results,
    }