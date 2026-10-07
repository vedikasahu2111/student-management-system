# Student Management System

A simple Student Management System built with **Python, Flask, SQLite, HTML, CSS and JavaScript**.

## Project Structure

```text
student-mgmt/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── static/
    └── index.html
```

## Run Locally

1. Install Python 3.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the Flask app:

```bash
python app.py
```

4. Open:

```text
http://127.0.0.1:5000
```

The SQLite database (`students.db`) is created automatically when the app starts and is intentionally ignored by Git.

## API Endpoints

- `GET /api/students?q=` — list/search students
- `POST /api/students` — add a student
- `PUT /api/students/<id>` — update a student
- `DELETE /api/students/<id>` — delete a student
