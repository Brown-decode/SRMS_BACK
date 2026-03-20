import random
from datetime import date
from faker import Faker
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.db.session import SessionLocal
from app.models.user import User
from app.models.student import Student
from app.models.class_model import Class
from app.models.subject import Subject
from app.models.score import Score
from app.models.assessment import Assessment
from app.models.class_subject import ClassSubject
from app.models.teacher import Teacher
from app.models.user import UserRole
from app.models.class_model import Cycle, Stream
from app.models.student import Gender

# 1. SETUP PASSWORD HASHING
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
COMMON_PASSWORD = "password123"
HASHED_PASSWORD = pwd_context.hash(COMMON_PASSWORD)

fake = Faker()


def seed():
    db: Session = SessionLocal()

    try:
        print("Cleaning database...")
        for model in [
            Score,
            Assessment,
            ClassSubject,
            Student,
            Teacher,
            Subject,
            Class,
            User,
        ]:
            db.query(model).delete()
        db.commit()

        # 1. SEED ADMINS
        print("Seeding admins...")
        admin = User(
            full_name="System Admin",
            loginid="admin",
            password_hash=HASHED_PASSWORD,
            role=UserRole.ADMIN,
        )
        db.add(admin)
        db.flush()

        # 2. SEED CLASSES
        print("Seeding classes...")
        classes = []
        for i in range(1, 6):
            c = Class(
                name=f"Class {i}",
                level=random.choice(list(Cycle)),
                stream=random.choice(list(Stream)),
            )
            db.add(c)
            classes.append(c)
        db.flush()

        # 3. SEED SUBJECTS
        print("Seeding subjects...")
        subject_names = ["Maths", "English", "French", "History", "Physics"]
        subjects = [Subject(name=n) for n in subject_names]
        db.add_all(subjects)
        db.flush()

        # 4. SEED TEACHERS
        print("Seeding and assigning teachers...")
        teachers = []
        for i in range(5):
            u = User(
                full_name=fake.name(),
                loginid=f"teacher{i+1}",
                password_hash=HASHED_PASSWORD,
                role=UserRole.TEACHER,
            )
            db.add(u)
            db.flush()
            t = Teacher(user_id=u.id)
            db.add(t)
            teachers.append(t)
        db.flush()

        # 5. LINK CLASSES TO SUBJECTS (Ensuring every teacher has work)
        cs_list = []
        for c in classes:
            # Assign all subjects to each class, rotating through our teachers
            for idx, s in enumerate(subjects):
                cs = ClassSubject(
                    class_id=c.id,
                    subject_id=s.id,
                    teacher_id=teachers[idx % len(teachers)].id,  # Rotates 0,1,2,3,4
                    coefficient=random.randint(1, 5),
                )
                db.add(cs)
                cs_list.append(cs)
        db.flush()

        # 6. SEED STUDENTS (Nested inside classes to ensure assignment)
        print("Seeding assigned students...")
        all_students = []
        for c in classes:
            for i in range(10):  # 10 students per class
                u = User(
                    full_name=fake.name(),
                    loginid=f"std_{c.name.replace(' ', '')}_{i}",
                    password_hash=HASHED_PASSWORD,
                    role=UserRole.STUDENT,
                )
                db.add(u)
                db.flush()

                s = Student(
                    user_id=u.id,
                    matricule=f"MAT-{c.id}-{i}-{random.randint(100, 999)}",
                    class_id=c.id,  # Explicitly linked to current class
                    gender=random.choice(list(Gender)),
                    date_of_birth=date(2010, 1, 1),
                )
                db.add(s)
                all_students.append(s)
        db.flush()
        # 7 & 8. SEED ASSESSMENTS & SCORES
        print("Seeding assessments and scores...")
        for cs in cs_list:
            sequence_setup = [{"num": 1, "weight": 0.50}, {"num": 2, "weight": 0.50}]

            for item in sequence_setup:
                # Create the Assessment
                a = Assessment(
                    title=f"Sequence {item['num']}",
                    class_subject_id=cs.id,
                    term=1,
                    sequence=item["num"],
                    max_score=20.0,
                    weight_percentage=item["weight"],
                )
                db.add(a)
                db.flush()  # Flush here so 'a.id' exists for the scores

                # YOUR CODE BLOCK: Assign scores to students for this assessment
                class_students = [s for s in all_students if s.class_id == cs.class_id]
                for s in class_students:
                    # Define a more realistic score distribution
                    dice_roll = random.random()
                    if dice_roll > 0.90:  # 10% chance for "Excellent" students
                        score_val = random.uniform(16, 20)
                    elif dice_roll > 0.40:  # 50% chance for "Average/Good" students
                        score_val = random.uniform(11, 15.9)
                    elif dice_roll > 0.15:  # 25% chance for "Passing/Borderline"
                        score_val = random.uniform(10, 10.9)
                    else:  # 15% chance for "Failing" students
                        score_val = random.uniform(4, 9.9)
                    db.add(
                        Score(
                            student_id=s.id,
                            assessment_id=a.id,
                            score=round(score_val, 2),
                        )
                    )
        db.flush()

        db.commit()
        print("-" * 30)
        print("DATABASE SEEDED SUCCESSFULLY!")
        print(f"Admin Login: admin / {COMMON_PASSWORD}")
        print("-" * 30)

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed()
