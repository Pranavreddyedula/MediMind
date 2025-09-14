from flask import Flask, render_template, request, redirect, url_for, session, send_file
import sqlite3
from fpdf import FPDF
from io import BytesIO
import os
from datetime import datetime

# Flask app setup
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback_secret_key")  # Use env var or fallback
DB_NAME = "health.db"

# Initialize database if not exists
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
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# Call init_db at startup
init_db()

# Template filter for formatting datetime
@app.template_filter('datetimeformat')
def datetimeformat(value):
    try:
        return datetime.strptime(value, '%Y-%m-%d %H:%M:%S').strftime('%d %b %Y %H:%M')
    except:
        return value

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
        try:
            weight = float(request.form["weight"])
            bp = request.form["bp"]
            heart_rate = int(request.form["heart_rate"])
            notes = request.form.get("notes", "")
        except ValueError:
            return "Invalid input! Please check your entries."

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO health_entries (user_id, weight, bp, heart_rate, notes) VALUES (?, ?, ?, ?, ?)",
                  (user_id, weight, bp, heart_rate, notes))
        conn.commit()
        conn.close()

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM health_entries WHERE user_id=? ORDER BY created_at DESC", (user_id,))
    entries = c.fetchall()
    conn.close()

    return render_template("health.html", entries=entries)

@app.route("/download_pdf")
def download_pdf():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    # Fetch health entries
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM health_entries WHERE user_id=? ORDER BY created_at ASC", (user_id,))
    entries = c.fetchall()
    conn.close()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"{session['username']}'s Health Report", ln=True, align="C")
    pdf.ln(10)

    # Table header
    pdf.set_font("Arial", "B", 12)
    pdf.cell(30, 10, "Weight", 1, 0, "C")
    pdf.cell(30, 10, "BP", 1, 0, "C")
    pdf.cell(30, 10, "Heart Rate", 1, 0, "C")
    pdf.cell(50, 10, "Notes", 1, 0, "C")
    pdf.cell(50, 10, "Date", 1, 1, "C")

    # Table rows safely
    pdf.set_font("Arial", "", 12)
    if entries:
        for entry in entries:
            weight = str(entry[2]) if entry[2] is not None else "-"
            bp = entry[3] if entry[3] else "-"
            heart_rate = str(entry[4]) if entry[4] is not None else "-"
            notes = entry[5] if entry[5] else "-"
            created_at = entry[6] if entry[6] else "-"
            pdf.cell(30, 10, weight, 1, 0, "C")
            pdf.cell(30, 10, bp, 1, 0, "C")
            pdf.cell(30, 10, heart_rate, 1, 0, "C")
            pdf.cell(50, 10, notes, 1, 0, "C")
            pdf.cell(50, 10, created_at, 1, 1, "C")
    else:
        pdf.cell(190, 10, "No health entries available.", 1, 1, "C")

    # Draw Weight Trend Graph if available
    weights = [entry[2] for entry in entries if entry[2] is not None]
    if weights:
        max_weight = max(weights) + 5
        pdf.ln(10)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Weight Trend", ln=True)
        start_x = 20
        start_y = pdf.get_y() + 10
        bar_width = 10
        spacing = 5
        for i, w in enumerate(weights):
            bar_height = (w / max_weight) * 50
            pdf.rect(start_x + i*(bar_width+spacing), start_y + 50 - bar_height, bar_width, bar_height, 'F')
        pdf.ln(60)

    # Draw Heart Rate Trend Graph if available
    heart_rates = [entry[4] for entry in entries if entry[4] is not None]
    if heart_rates:
        max_hr = max(heart_rates) + 10
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Heart Rate Trend", ln=True)
        start_x = 20
        start_y = pdf.get_y() + 10
        bar_width = 10
        spacing = 5
        for i, hr in enumerate(heart_rates):
            bar_height = (hr / max_hr) * 50
            pdf.rect(start_x + i*(bar_width+spacing), start_y + 50 - bar_height, bar_width, bar_height, 'F')
        pdf.ln(60)

    # Output PDF safely
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return send_file(pdf_output, download_name=f"{session['username']}_health_report.pdf", as_attachment=True)

# Render-ready app runner
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
