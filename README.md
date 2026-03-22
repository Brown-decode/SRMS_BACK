# SRMS_BACK

School results management system backend

file structure:
backend/
│
├── app/
│ │
│ ├── main.py
│ │
│ ├── core/
│ │ ├── config.py
│ │ ├── security.py
│ │ └── dependencies.py
│ │
│ ├── db/
│ │ ├── database.py
│ │ └── base.py
│ │
│ ├── models/
│ │ ├── **init**.py
│ │ ├── user.py
│ │ ├── class_model.py
│ │ ├── subject.py
│ │ ├── teacher.py
│ │ ├── student.py
│ │ ├── class_subject.py
│ │ ├── assessment.py
│ │ └── score.py
│ │
│ ├── schemas/
│ │ ├── user.py
│ │ ├── class_schema.py
│ │ ├── subject.py
│ │ ├── teacher.py
│ │ ├── student.py
│ │ ├── class_subject.py
│ │ ├── assessment.py
│ │ └── score.py
│ │
│ ├── services/
│ │ ├── auth_service.py
│ │ ├── student_service.py
│ │ ├── teacher_service.py
│ │ ├── class_service.py
│ │ ├── score_service.py
│ │ └── result_service.py
│ │
│ ├── routers/
│ │ ├── auth.py
│ │ ├── students.py
│ │ ├── teachers.py
│ │ ├── classes.py
│ │ ├── subjects.py
│ │ └── scores.py
│ │
│ └── utils/
│ └── grade_utils.py
│
├── .env
├── requirements.txt
└── README.md
