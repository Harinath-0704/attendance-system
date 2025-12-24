from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from datetime import date
import os

app = Flask(__name__)
app.secret_key = "attendance_secure_key"

# ✅ Render-safe database path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "attendance.sqlite3")

# ---------- DATABASE ----------
def get_db():
    return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                date TEXT
            )
        """)
        db.commit()

init_db()

# ---------- LOGIN ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect(url_for("dashboard"))

    return render_template("login.html")

# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "admin" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")

# ---------- ADD STUDENT ----------
@app.route("/add_student", methods=["GET", "POST"])
def add_student():
    if "admin" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form.get("name")
        if name:
            with get_db() as db:
                db.execute("INSERT INTO students (name) VALUES (?)", (name,))
                db.commit()
        return redirect(url_for("dashboard"))

    return render_template("add_student.html")

# ---------- ATTENDANCE ----------
@app.route("/attendance")
def attendance():
    if "admin" not in session:
        return redirect(url_for("login"))

    today = str(date.today())

    with get_db() as db:
        students = db.execute("SELECT name FROM students").fetchall()

        for s in students:
            db.execute(
                "INSERT INTO attendance (name, date) VALUES (?, ?)",
                (s[0], today)
            )

        db.commit()
        records = db.execute(
            "SELECT name, date FROM attendance ORDER BY id DESC"
        ).fetchall()

    return render_template("attendance.html", records=records)

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ❌ DO NOT use app.run()
# Gunicorn will handle execution
