# SCHOOL RESULTS MANAGEMENT SYSTEM (SRMS)
Internship Project – PEFSCOM SYSTEM
Context: Typical Cameroonian Secondary School (Anglophone System)

---

## 1. PROJECT OVERVIEW

This system is designed for a typical Cameroonian secondary school.

The system must:

- Manage students (Form 1 – Form 5 / Lower & Upper Sixth optional)
- Manage teachers
- Manage subjects
- Manage classes (including streams like Science, Arts, Commercial)
- Allow teachers to enter term-based scores
- Automatically compute term results
- Compute class ranking
- Determine promotion decision
- Enforce strict role-based access control

This is an academic result management system only.

It is NOT:
- A payment system
- An attendance system
- A messaging platform
- A WAEC/GCE integration tool
- A national analytics system

Keep it realistic and focused.

---

## 2. EDUCATIONAL CONTEXT (CAMEROON)

Academic Year:
- 3 Terms (Term 1, Term 2, Term 3)

Assessment Structure (Typical):
- Sequence 1 → 20%
- Sequence 2 → 20%
- Exam → 60%

Grading Scale (Over 20 System):

16 – 20 → A  
14 – 15 → B  
12 – 13 → C  
10 – 11 → D  
0  – 9  → F  

Promotion Rule:
- If average ≥ 10 → PROMOTED
- If average < 10 → REPEAT

Ranking:
- Students ranked by average (descending)
- Position must be displayed (e.g., 3rd out of 25)

---

## 3. TECHNOLOGY STACK

Backend:
- FastAPI
- PostgreSQL
- SQLAlchemy ORM
- JWT Authentication
- Bcrypt password hashing

Frontend:
- React
- Axios
- Role-based routing

Architecture:
- REST API
- Role-based access control
- Server-side result computation

---

## 4. DATABASE DESIGN (FINAL STRUCTURE)

### User
- id
- full_name
- email (unique)
- password_hash
- role (ADMIN | TEACHER | STUDENT)
- is_active

Used strictly for authentication.

---

### Class
Represents academic grouping.

- id
- name (e.g., Form 5 Science)
- level (Form 1–5, Lower Sixth, Upper Sixth)
- stream (Science, Arts, Commercial)
- academic_year

---

### Subject
- id
- name

No coefficient stored here.

---

### Teacher
- id
- user_id (FK → User)

---

### Student
- id
- user_id (FK → User)
- matricule
- class_id (FK → Class)
- date_of_birth

---

### ClassSubject
Defines subject context within a class.

- id
- class_id (FK → Class)
- subject_id (FK → Subject)
- teacher_id (FK → Teacher)
- coefficient

IMPORTANT:
Coefficient belongs here because it depends on the class/stream.

---

### Assessment
Defines evaluation type.

- id
- name (Sequence 1, Sequence 2, Exam)
- weight_percentage

Example:
- Sequence 1 → 20
- Sequence 2 → 20
- Exam → 60

---

### Score
Stores raw marks.

- id
- student_id (FK → Student)
- class_subject_id (FK → ClassSubject)
- assessment_id (FK → Assessment)
- term (1 | 2 | 3)
- score (over 20)

Only raw marks stored here.

---

## 5. RESULT COMPUTATION LOGIC (BACKEND ONLY)

All computation must happen in the backend.

For a specific student, class, and term:

STEP 1 – Compute Subject Total:
sum(score × assessment_weight / 100)

STEP 2 – Apply Coefficient:
subject_total × coefficient

STEP 3 – Compute General Average:
(sum of weighted subject totals) / (sum of coefficients)

STEP 4 – Assign Grade:
16–20 → A  
14–15 → B  
12–13 → C  
10–11 → D  
0–9   → F  

STEP 5 – Determine Promotion:
average ≥ 10 → PROMOTED  
average < 10 → REPEAT  

STEP 6 – Ranking:
Sort all students in class by average (descending)
Assign position.

No result logic must be computed in the frontend.

---

## 6. ROLE-BASED PERMISSIONS

ADMIN can:
- Create classes
- Create subjects
- Create teachers
- Create students
- Assign subject to class
- Set coefficients
- Define assessments

TEACHER can:
- View assigned class subjects
- View students in their classes
- Enter scores per term
- Update scores before result finalization

STUDENT can:
- View only their own results
- View subject breakdown
- View position
- View promotion decision

Strict enforcement required.

---

## 7. REQUIRED API ENDPOINTS

Authentication:
- POST /auth/login

Admin:
- POST /classes
- POST /subjects
- POST /teachers
- POST /students
- POST /class-subjects
- POST /assessments

Teacher:
- GET /my-subjects
- GET /class-subject/{id}/students
- POST /scores
- PUT /scores/{id}

Student:
- GET /my-results?term=1

Class Results:
- GET /classes/{id}/results?term=1

---

## 8. 30-DAY EXECUTION PLAN

### WEEK 1 – Backend Foundation

Day 1:
- Setup FastAPI project
- Connect PostgreSQL
- Configure SQLAlchemy

Day 2:
- Implement User model
- Password hashing
- JWT login
- Protected routes

Day 3:
- Create Class, Subject, Teacher, Student models
- CRUD endpoints

Day 4:
- Implement ClassSubject
- Assign subject to class
- Add coefficient

Day 5:
- Implement Assessment model

Day 6:
- Implement Score model
- Add term field
- Teacher score entry endpoint

Day 7:
- Implement basic result computation (per term)

---

### WEEK 2 – Complete Backend Logic

Day 8:
- Implement grade mapping (20-point system)

Day 9:
- Implement ranking system

Day 10:
- Enforce strict role-based access

Day 11:
- Class result summary endpoint

Day 12:
- Student result endpoint (with position + promotion)

Day 13:
- Manual testing with demo data

Day 14:
- Backend freeze (no schema redesign after this day)

---

### WEEK 3 – Frontend

Day 15:
- Setup React
- Setup routing
- Setup Axios

Day 16:
- Login page
- Role-based redirect

Day 17:
- Admin dashboard (CRUD UI)

Day 18:
- Assign subject to class UI

Day 19:
- Teacher dashboard
- Score entry per term

Day 20:
- Student dashboard
- Display full term result

Day 21:
- Full API integration
- Fix bugs

---

### WEEK 4 – Polish & Defense

Day 22:
- Clean UI

Day 23:
- Seed realistic demo data

Day 24:
- Optional: PDF report card

Day 25:
- Full system testing

Day 26:
- Documentation writing

Day 27:
- Prepare defense explanation

Day 28:
- Practice full demo

Day 29:
- Final fixes

Day 30:
- Final review

---

## 9. AI ASSISTANCE RULES

When requesting help:

- Follow the current day strictly.
- Do NOT redesign the database after Day 14.
- Do NOT introduce features outside scope.
- Keep code clean and minimal.
- Separate models, schemas, routers, services.
- Prioritize logic correctness over UI beauty.

When I say:
"I am on Day X"

Assist only within that day's scope.

Do not jump ahead.
Do not over-engineer.