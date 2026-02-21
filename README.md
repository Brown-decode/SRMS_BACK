# SRMS_BACK

School results management system backend

file structure:
backend/
│
├── app/
│ ├── main.py
│ ├── core/
│ │ ├── config.py
│ │ ├── security.py
│ │
│ ├── db/
│ │ ├── base.py
│ │ ├── session.py
│ │
│ ├── models/
│ │ ├── user.py
│ │ ├── student.py
│ │ ├── result.py
│ │
│ ├── schemas/
│ │ ├── user.py
│ │ ├── student.py
│ │ ├── result.py
│ │
│ ├── crud/
│ │ ├── user.py
│ │ ├── student.py
│ │ ├── result.py
│ │
│ ├── api/
│ │ ├── deps.py
│ │ ├── routes/
│ │ ├── auth.py
│ │ ├── students.py
│ │ ├── results.py
│
├── alembic/
├── requirements.txt
└── .env
