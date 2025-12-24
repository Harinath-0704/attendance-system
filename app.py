from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = "attendance_secure_key"

DB = "attendance.sqlite3"

# ---------- DATABASE ----------
def get_db():
    return sqlite3.connect(DB)

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

init_db()

# ---------- LOGIN ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin123":
            session["admin"] = True
            return redirect("/dashboard")
    return render_template("login.html")

# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "admin" not in session:
        return redirect("/")
    return render_template("dashboard.html")

# ---------- ADD STUDENT ----------
@app.route("/add_student", methods=["GET", "POST"])
def add_student():
    if "admin" not in session:
        return redirect("/")
    if request.method == "POST":
        name = request.form["name"]
        with get_db() as db:
            db.execute("INSERT INTO students (name) VALUES (?)", (name,))
        return redirect("/dashboard")
    return render_template("add_student.html")

# ---------- ATTENDANCE ----------
@app.route("/attendance")
def attendance():
    if "admin" not in session:
        return redirect("/")
    today = str(date.today())
    with get_db() as db:
        students = db.execute("SELECT name FROM students").fetchall()
        for s in students:
            db.execute("INSERT INTO attendance (name, date) VALUES (?, ?)", (s[0], today))
        records = db.execute("SELECT name, date FROM attendance").fetchall()
    return render_template("attendance.html", records=records)

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# IMPORTANT:
# Do NOT use app.run()
# gunicorn will run the app
