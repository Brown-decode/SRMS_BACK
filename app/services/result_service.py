from sqlalchemy.orm import Session
from app.models.student import Student
from app.models.class_subject import ClassSubject
from app.models.assessment import Assessment
from app.models.score import Score
from sqlalchemy import and_


def compute_student_results(db: Session, student_id: int, class_id: int, term: int):
    """
    Computes the results for a given student, class, and term.
    """

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return None  # Or raise an exception

    class_subjects = (
        db.query(ClassSubject).filter(ClassSubject.class_id == class_id).all()
    )

    total_weighted_score_x_coeff = 0
    total_coefficients = 0
    student_subjects = []

    for cs in class_subjects:
        # Find all assessments for this subject in the given term
        term_assessments = (
            db.query(Assessment)
            .filter(Assessment.class_subject_id == cs.id, Assessment.term == term)
            .all()
        )

        if not term_assessments:
            continue

        # Get all scores for this student for those assessments
        assessment_ids = [a.id for a in term_assessments]
        scores = (
            db.query(Score)
            .filter(
                and_(
                    Score.student_id == student_id,
                    Score.assessment_id.in_(assessment_ids),
                )
            )
            .all()
        )

        score_map = {s.assessment_id: s.score for s in scores}

        # Calculate Subject Average: Sum(Score * Weight / MaxScore)
        # This correctly handles the 20-point scale.
        subject_avg = sum(
            (score_map.get(a.id, 0) / a.max_score * 20) * (a.weight_percentage / 100)
            for a in term_assessments
        )

        total_weighted_score_x_coeff += subject_avg * cs.coefficient
        total_coefficients += cs.coefficient

        student_subjects.append(
            {
                "subject_name": cs.subject.name,
                "average": round(subject_avg, 2),
                "coefficient": cs.coefficient,
                "grade": (
                    "A"
                    if subject_avg >= 16
                    else (
                        "B"
                        if subject_avg >= 14
                        else (
                            "C"
                            if subject_avg >= 12
                            else "D" if subject_avg >= 10 else "F"
                        )
                    )
                ),
            }
        )

    overall_average = (
        total_weighted_score_x_coeff / total_coefficients
        if total_coefficients > 0
        else 0
    )

    return {
        "student_name": student.full_name,
        "matricule": student.matricule,
        "average": round(overall_average, 2),
        "subjects": student_subjects,
        "promotion_status": "PROMOTED" if overall_average >= 10 else "REPEAT",
    }


def compute_class_results(db: Session, class_id: int, term: int):
    """
    Computes and ranks results for the entire class.
    """
    students = db.query(Student).filter(Student.class_id == class_id).all()
    class_results = []

    for student in students:
        result = compute_student_results(db, student.id, class_id, term)
        if result:
            class_results.append(result)

    class_results.sort(key=lambda x: x["average"], reverse=True)
    for index, result in enumerate(class_results):
        result["position"] = index + 1

    return class_results
