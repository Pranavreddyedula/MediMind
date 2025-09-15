from flask import Flask, render_template, request, redirect, url_for, session, send_file
import sqlite3
from fpdf import FPDF
from io import BytesIO
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"
DB_NAME = "health.db"

# ---------- Database Setup ----------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    email TEXT,
                    password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS health (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    weight REAL,
                    bp TEXT,
                    heart_rate INTEGER,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id))''')
    conn.commit()
    conn.close()

init_db()

# ---------- Helpers ----------
def get_user_id(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return user[0] if user else None

def analyze_health(entries):
    """Analyze health data and return suggestions, risks, and diet tips."""
    if not entries:
        return "No data available to analyze.", [], "Please add health entries first."

    weights = [e[2] for e in entries if e[2] is not None]
    bps = [e[3] for e in entries if e[3]]
    hrs = [e[4] for e in entries if e[4] is not None]

    suggestions = []
    risks = []

    # Weight check
    if weights:
        avg_weight = sum(weights) / len(weights)
        if avg_weight < 50:
            risks.append("Underweight detected – Possible risk of nutrient deficiency.")
            suggestions.append("Increase protein and calorie intake.")
        elif avg_weight > 80:
            risks.append("Overweight detected – Possible risk of diabetes or heart disease.")
            suggestions.append("Try regular exercise and balanced diet.")
        else:
            suggestions.append("Your weight is in a healthy range.")

    # BP check
    if bps:
        systolic = []
        diastolic = []
        for bp in bps:
            try:
                s, d = bp.split("/")
                systolic.append(int(s))
                diastolic.append(int(d))
            except:
                continue
        if systolic and diastolic:
            avg_sys = sum(systolic) / len(systolic)
            avg_dia = sum(diastolic) / len(diastolic)
            if avg_sys > 140 or avg_dia > 90:
                risks.append("High Blood Pressure – Risk of hypertension.")
                suggestions.append("Reduce salt, avoid fried foods, and exercise daily.")
            elif avg_sys < 100 or avg_dia < 60:
                risks.append("Low Blood Pressure – Risk of dizziness or fatigue.")
                suggestions.append("Stay hydrated and include more salt in diet.")
            else:
                suggestions.append("Your blood pressure is normal.")

    # Heart rate check
    if hrs:
        avg_hr = sum(hrs) / len(hrs)
        if avg_hr > 100:
            risks.append("High Heart Rate – Possible tachycardia.")
            suggestions.append("Practice stress management and consult a doctor.")
        elif avg_hr < 60:
            risks.append("Low Heart Rate – Possible bradycardia.")
            suggestions.append("Check thyroid and maintain healthy activity levels.")
        else:
            suggestions.append("Your heart rate is normal.")

    # Diet Plan
    diet_plan = """
🍏 Suggested Diet Plan:
- Breakfast: Oats/Idli with fruits
- Lunch: Brown rice / Chapati with dal and vegetables
- Evening Snack: Nuts / Green tea
- Dinner: Light meals like soup or salad
- Hydration: At least 2–3 liters of water per day
"""
    return "\n".join(suggestions), risks, diet_plan

# ---------- Routes ----------
@app.route("/")
def home():
    return render_template("index.html")

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
            conn.close()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            conn.close()
            return "Username already exists. Try another."

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
            session["username"] = username
            return redirect(url_for("health"))
        else:
            return "Invalid credentials."

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))

@app.route("/health", methods=["GET", "POST"])
def health():
    if "username" not in session:
        return redirect(url_for("login"))

    user_id = get_user_id(session["username"])

    if request.method == "POST":
        weight = request.form["weight"]
        bp = request.form["bp"]
        heart_rate = request.form["heart_rate"]
        notes = request.form["notes"]

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO health (user_id, weight, bp, heart_rate, notes) VALUES (?, ?, ?, ?, ?)",
                  (user_id, weight, bp, heart_rate, notes))
        conn.commit()
        conn.close()

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM health WHERE user_id=? ORDER BY created_at DESC", (user_id,))
    entries = c.fetchall()
    conn.close()

    return render_template("health.html", entries=entries)

@app.route("/download_pdf")
def download_pdf():
    if "username" not in session:
        return redirect(url_for("login"))

    user_id = get_user_id(session["username"])
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM health WHERE user_id=? ORDER BY created_at ASC", (user_id,))
    entries = c.fetchall()
    conn.close()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, f"Health Report for {session['username']}", ln=True, align="C")

    # Table
    pdf.set_font("Arial", "B", 12)
    headers = ["Weight", "BP", "Heart Rate", "Notes", "Date"]
    for h in headers:
        pdf.cell(38, 10, h, 1, 0, "C")
    pdf.ln()

    pdf.set_font("Arial", "", 12)
    if entries:
        for entry in entries:
            weight = str(entry[2]) if entry[2] else "-"
            bp = entry[3] if entry[3] else "-"
            heart_rate = str(entry[4]) if entry[4] else "-"
            notes = entry[5] if entry[5] else "-"
            created_at = entry[6] if entry[6] else "-"
            pdf.cell(38, 10, weight, 1, 0, "C")
            pdf.cell(38, 10, bp, 1, 0, "C")
            pdf.cell(38, 10, heart_rate, 1, 0, "C")
            pdf.cell(38, 10, notes, 1, 0, "C")
            pdf.cell(38, 10, created_at, 1, 1, "C")
    else:
        pdf.cell(190, 10, "No health entries available.", 1, 1, "C")

    # Trend Graphs
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "Health Trends", ln=True, align="L")

    # Weight Trend
    weights = [e[2] for e in entries if e[2] is not None]
    if weights:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, "Weight Trend", ln=True, align="L")
        start_x, start_y = 10, pdf.get_y() + 5
        bar_width = 10
        spacing = 5
        max_weight = max(weights) + 5
        for i, w in enumerate(weights):
            bar_height = (w / max_weight) * 50
            pdf.rect(start_x + i*(bar_width+spacing), start_y + 50 - bar_height, bar_width, bar_height, 'F')
        pdf.ln(60)

    # Heart Rate Trend
    heart_rates = [e[4] for e in entries if e[4] is not None]
    if heart_rates:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, "Heart Rate Trend", ln=True, align="L")
        start_x, start_y = 10, pdf.get_y() + 5
        bar_width = 10
        spacing = 5
        max_hr = max(heart_rates) + 10
        for i, hr in enumerate(heart_rates):
            bar_height = (hr / max_hr) * 50
            pdf.rect(start_x + i*(bar_width+spacing), start_y + 50 - bar_height, bar_width, bar_height, 'F')
        pdf.ln(60)

    # Health Analysis
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "Health Analysis & Suggestions", ln=True, align="L")

    suggestions, risks, diet_plan = analyze_health(entries)

    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, f"Suggestions:\n{suggestions}")
    if risks:
        pdf.multi_cell(0, 8, f"Risks Detected:\n- " + "\n- ".join(risks))
    pdf.multi_cell(0, 8, f"Diet Plan:\n{diet_plan}")

    # Output safely
    pdf_output = BytesIO()
    pdf_output.write(pdf.output(dest='S').encode('latin1'))
    pdf_output.seek(0)
    return send_file(pdf_output, download_name=f"{session['username']}_health_report.pdf", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
