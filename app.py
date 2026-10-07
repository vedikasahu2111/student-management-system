import re
import sqlite3
import os
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "static"))
DB = os.path.join(BASE_DIR, "students.db")


def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as c:
        c.execute(
            """CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                roll_no TEXT NOT NULL UNIQUE,
                class_name TEXT NOT NULL,
                marks REAL NOT NULL,
                contact TEXT NOT NULL
            )"""
        )


def validate(data):
    """Return (clean_data, error_message)."""
    name = (data.get("name") or "").strip()
    roll = (data.get("roll_no") or "").strip()
    cls = (data.get("class_name") or "").strip()
    contact = (data.get("contact") or "").strip()
    if not name or not roll or not cls or not contact:
        return None, "All fields are required."
    try:
        marks = float(data.get("marks"))
    except (TypeError, ValueError):
        return None, "Marks must be a number."
    if not 0 <= marks <= 100:
        return None, "Marks must be between 0 and 100."
    if not re.fullmatch(r"\d{10}", contact):
        return None, "Contact must be a 10-digit number."
    return {"name": name, "roll_no": roll, "class_name": cls,
            "marks": marks, "contact": contact}, None


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/students", methods=["GET"])
def list_students():
    q = (request.args.get("q") or "").strip()
    sql, params = "SELECT * FROM students", []
    if q:
        sql += " WHERE name LIKE ? OR roll_no LIKE ?"
        params = [f"%{q}%", f"%{q}%"]
    sql += " ORDER BY id DESC"
    with db() as c:
        rows = c.execute(sql, params).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/students", methods=["POST"])
def add_student():
    data, err = validate(request.get_json(silent=True) or {})
    if err:
        return jsonify(error=err), 400
    try:
        with db() as c:
            cur = c.execute(
                "INSERT INTO students (name, roll_no, class_name, marks, contact)"
                " VALUES (?,?,?,?,?)",
                (data["name"], data["roll_no"], data["class_name"],
                 data["marks"], data["contact"]),
            )
        return jsonify(id=cur.lastrowid, **data), 201
    except sqlite3.IntegrityError:
        return jsonify(error="Roll number already exists."), 409


@app.route("/api/students/<int:sid>", methods=["PUT"])
def update_student(sid):
    data, err = validate(request.get_json(silent=True) or {})
    if err:
        return jsonify(error=err), 400
    try:
        with db() as c:
            cur = c.execute(
                "UPDATE students SET name=?, roll_no=?, class_name=?, marks=?,"
                " contact=? WHERE id=?",
                (data["name"], data["roll_no"], data["class_name"],
                 data["marks"], data["contact"], sid),
            )
        if cur.rowcount == 0:
            return jsonify(error="Student not found."), 404
        return jsonify(id=sid, **data)
    except sqlite3.IntegrityError:
        return jsonify(error="Roll number already exists."), 409


@app.route("/api/students/<int:sid>", methods=["DELETE"])
def delete_student(sid):
    with db() as c:
        cur = c.execute("DELETE FROM students WHERE id=?", (sid,))
    if cur.rowcount == 0:
        return jsonify(error="Student not found."), 404
    return jsonify(message="Deleted.")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
