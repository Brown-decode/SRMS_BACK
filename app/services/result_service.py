from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
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
        # Normalize weights to sum to 1.0 (100%)
        total_weight = sum(a.weight_percentage for a in term_assessments)
        if total_weight == 0:
            continue  # Avoid division by zero

        subject_avg = sum(
            (score_map.get(a.id, 0) / a.max_score * 20)
            * (a.weight_percentage / total_weight)
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
        "student_name": student.user.full_name,
        "matricule": student.matricule,
        "average": round(overall_average, 2),
        "subjects": student_subjects,
        "promotion_status": "PROMOTED" if overall_average >= 10 else "REPEAT",
    }


def compute_class_results(db: Session, class_id: int, term: int):
    """
    Computes and ranks results for the entire class.
    """
    # 1. Fetch all students in the class with User info
    students = (
        db.query(Student)
        .options(joinedload(Student.user))
        .filter(Student.class_id == class_id)
        .all()
    )

    if not students:
        return []

    # 2. Fetch all subjects assigned to this class
    class_subjects = (
        db.query(ClassSubject)
        .options(joinedload(ClassSubject.subject))
        .filter(ClassSubject.class_id == class_id)
        .all()
    )

    if not class_subjects:
        return []

    # 3. Fetch all assessments for this class's subjects in this term
    cs_ids = [cs.id for cs in class_subjects]
    assessments = (
        db.query(Assessment)
        .filter(Assessment.class_subject_id.in_(cs_ids), Assessment.term == term)
        .all()
    )

    # Organize assessments by class_subject_id
    assessments_by_cs = {}
    for a in assessments:
        assessments_by_cs.setdefault(a.class_subject_id, []).append(a)

    # 4. Fetch all scores for these students and assessments
    student_ids = [s.id for s in students]
    assessment_ids = [a.id for a in assessments]

    scores = []
    if assessment_ids:
        scores = (
            db.query(Score)
            .filter(
                Score.student_id.in_(student_ids),
                Score.assessment_id.in_(assessment_ids),
            )
            .all()
        )

    # Organize scores: student_id -> assessment_id -> score
    score_map = {}
    for s in scores:
        if s.student_id not in score_map:
            score_map[s.student_id] = {}
        score_map[s.student_id][s.assessment_id] = s.score

    class_results = []

    for student in students:
        total_weighted_score = 0
        total_coefficients = 0
        student_subjects = []

        student_scores = score_map.get(student.id, {})

        for cs in class_subjects:
            subj_assessments = assessments_by_cs.get(cs.id, [])
            if not subj_assessments:
                continue

            # Calculate Subject Average
            subject_avg = 0
            if subj_assessments:
                # Normalize weights to sum to 1.0 (100%)
                total_weight = sum(a.weight_percentage for a in subj_assessments)
                if total_weight > 0:
                    for a in subj_assessments:
                        val = student_scores.get(a.id, 0)
                        # Formula: (score / max * 20) * (weight / total_weight)
                        if a.max_score > 0:
                            subject_avg += (val / a.max_score * 20) * (
                                a.weight_percentage / total_weight
                            )

            total_weighted_score += subject_avg * cs.coefficient
            total_coefficients += cs.coefficient

            # Assign Grade
            if subject_avg >= 16:
                grade = "A"
            elif subject_avg >= 14:
                grade = "B"
            elif subject_avg >= 12:
                grade = "C"
            elif subject_avg >= 10:
                grade = "D"
            else:
                grade = "F"

            student_subjects.append(
                {
                    "subject_name": cs.subject.name,
                    "average": round(subject_avg, 2),
                    "coefficient": cs.coefficient,
                    "grade": grade,
                }
            )

        overall_average = 0
        if total_coefficients > 0:
            overall_average = total_weighted_score / total_coefficients

        class_results.append(
            {
                "student_name": student.user.full_name,
                "matricule": student.matricule,
                "average": round(overall_average, 2),
                "subjects": student_subjects,
                "promotion_status": "PROMOTED" if overall_average >= 10 else "REPEAT",
            }
        )

    class_results.sort(key=lambda x: x["average"], reverse=True)
    for index, result in enumerate(class_results):
        result["position"] = index + 1

    return class_results
