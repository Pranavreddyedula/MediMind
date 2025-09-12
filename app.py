from flask import Flask, render_template, request, redirect, url_for, session, send_file
import sqlite3
from fpdf import FPDF
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

DB_NAME = "health.db"

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    email TEXT,
                    password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS health_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    weight REAL,
                    bp TEXT,
                    heart_rate INTEGER,
                    notes TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                      (username, email, password))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "Username already exists!"
        conn.close()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["username"] = user[1]
            return redirect(url_for("health"))
        else:
            return "Invalid credentials!"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/health", methods=["GET", "POST"])
def health():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    if request.method == "POST":
        weight = request.form["weight"]
        bp = request.form["bp"]
        heart_rate = request.form["heart_rate"]
        notes = request.form.get("notes", "")

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO health_entries (user_id, weight, bp, heart_rate, notes) VALUES (?, ?, ?, ?, ?)",
                  (user_id, weight, bp, heart_rate, notes))
        conn.commit()
        conn.close()

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM health_entries WHERE user_id=?", (user_id,))
    entries = c.fetchall()
    conn.close()

    return render_template("health.html", entries=entries)

@app.route("/download_pdf")
def download_pdf():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM health_entries WHERE user_id=?", (user_id,))
    entries = c.fetchall()
    conn.close()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"{session['username']}'s Health Report", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(40, 10, "Weight")
    pdf.cell(40, 10, "BP")
    pdf.cell(40, 10, "Heart Rate")
    pdf.cell(70, 10, "Notes", ln=True)

    pdf.set_font("Arial", "", 12)
    for entry in entries:
        pdf.cell(40, 10, str(entry[2]))
        pdf.cell(40, 10, entry[3])
        pdf.cell(40, 10, str(entry[4]))
        pdf.cell(70, 10, entry[5], ln=True)

    pdf_path = f"{session['username']}_health_report.pdf"
    pdf.output(pdf_path)

    return send_file(pdf_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
