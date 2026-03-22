import random
from datetime import date
from faker import Faker
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.models.student import Student, Gender
from app.models.class_model import Class, Cycle, Stream
from app.models.subject import Subject
from app.models.score import Score
from app.models.assessment import Assessment
from app.models.class_subject import ClassSubject
from app.models.teacher import Teacher

# 1. SETUP
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
COMMON_PASSWORD = "password123"
HASHED_PASSWORD = pwd_context.hash(COMMON_PASSWORD)
fake = Faker()

def seed():
    db: Session = SessionLocal()
    try:
        print("🔥 Purging Database...")
        # Order matters for deletion due to Foreign Key constraints
        for model in [Score, Assessment, ClassSubject, Student, Teacher, Subject, Class, User]:
            db.query(model).delete()
        db.commit()

        # 1. ADMINS
        db.add(User(full_name="System Admin", loginid="admin", password_hash=HASHED_PASSWORD, role=UserRole.ADMIN))
        db.flush()

        # 2. SUBJECTS
        print("📚 Seeding Subjects...")
        subject_names = ["Maths", "English", "French", "History", "Physics", "Chemistry", "Biology", "ICT", "Geography", "Literature"]
        subjects = [Subject(name=n) for n in subject_names]
        db.add_all(subjects)
        db.flush()

        # 3. CLASSES (Fixed: Ensures Unique Names)
        print("🏫 Seeding Unique Randomized Classes...")
        classes = []
        # Create a list of all possible valid Form/Section combos
        potential_combos = [
            (f"Form {f} {s}", f) 
            for f in range(1, 6) 
            for s in ['A', 'B', 'C']
        ] + [
            (f"Lower Sixth {s}", 6) for s in ['Science', 'Arts']
        ] + [
            (f"Upper Sixth {s}", 7) for s in ['Science', 'Arts']
        ]
        
        # Pick 10 unique classes from the list
        selected_configs = random.sample(potential_combos, 10)

        for name, form_level in selected_configs:
            c = Class(
                name=name,
                level=Cycle.FIRST_CYCLE if form_level <= 5 else Cycle.SECOND_CYCLE,
                stream=random.choice(list(Stream)),
            )
            db.add(c)
            classes.append(c)
        db.flush()

        # 4. TEACHERS with Subject Specialties
        print("👨‍🏫 Seeding Overloaded Teachers...")
        teachers = []
        for i in range(8):
            u = User(
                full_name=fake.name(),
                loginid=f"teacher{i+1}",
                password_hash=HASHED_PASSWORD,
                role=UserRole.TEACHER,
            )
            db.add(u)
            db.flush()
            t = Teacher(user_id=u.id)
            # Assign each teacher 1-3 random subjects they "specialize" in
            teacher_specs = random.sample(subjects, random.randint(1, 3))
            # We don't store specialties in DB usually, just use them for seeding logic below
            t._seed_specs = teacher_specs 
            db.add(t)
            teachers.append(t)
        db.flush()

        # 5. LINK CLASSES TO SUBJECTS
        print("🔗 Mapping Class-Subjects...")
        cs_list = []
        for c in classes:
            # Each class gets 5 to 8 subjects
            num_subs = random.randint(5, 8)
            assigned_subjects = random.sample(subjects, num_subs)
            for s in assigned_subjects:
                # Find teachers who 'specialize' in this subject
                eligible = [t for t in teachers if s in t._seed_specs]
                assigned_teacher = random.choice(eligible if eligible else teachers)
                
                cs = ClassSubject(
                    class_id=c.id,
                    subject_id=s.id,
                    teacher_id=assigned_teacher.id,
                    coefficient=random.randint(1, 5),
                )
                db.add(cs)
                cs_list.append(cs)
        db.flush()

        # 6. STUDENTS (Variable Class Sizes)
        print("🎒 Seeding Variable Student Enrollment...")
        all_students = []
        for idx, c in enumerate(classes):
            num_students = random.randint(10, 40) # Randomize size
            for i in range(num_students):
                u = User(
                    full_name=fake.name(),
                    loginid=f"std_{idx}_{i}_{random.randint(100,999)}",
                    password_hash=HASHED_PASSWORD,
                    role=UserRole.STUDENT,
                )
                db.add(u)
                db.flush()
                s = Student(
                    user_id=u.id,
                    matricule=f"MAT-{date.today().year}-{c.id}-{i:02d}{random.randint(10,99)}",
                    class_id=c.id,
                    gender=random.choice(list(Gender)),
                    date_of_birth=date(2008, random.randint(1,12), random.randint(1,28)),
                )
                db.add(s)
                all_students.append(s)
        db.flush()

        # 7. ASSESSMENTS & SCORES (Multi-Term)
        print("📊 Seeding Scores (Term 1 & 2)...")
        for cs in cs_list:
            for term_val in [1, 2]: # Seed two terms to test trends
                for seq_num in [1, 2]:
                    a = Assessment(
                        title=f"T{term_val} Seq {seq_num}",
                        class_subject_id=cs.id,
                        term=term_val,
                        sequence=seq_num,
                        max_score=20.0,
                        weight_percentage=0.50,
                    )
                    db.add(a)
                    db.flush()

                    class_students = [s for s in all_students if s.class_id == cs.class_id]
                    for s in class_students:
                        # 5% chance student was absent
                        if random.random() < 0.05:
                            continue
                            
                        # Realistic score distribution
                        roll = random.random()
                        if roll > 0.90: score_val = random.uniform(15, 20)
                        elif roll > 0.40: score_val = random.uniform(10, 14.9)
                        else: score_val = random.uniform(3, 9.9)
                        
                        db.add(Score(
                            student_id=s.id,
                            assessment_id=a.id,
                            score=round(score_val, 2),
                        ))
        
        db.commit()
        print("\n✅ DATABASE SEEDED SUCCESSFULLY!")
        print(f"Generated {len(all_students)} students across {len(classes)} classes.")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed()