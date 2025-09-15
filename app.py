from flask import Flask, render_template, request, redirect, url_for, session, send_file
import sqlite3
from fpdf import FPDF
from io import BytesIO
import os
from datetime import datetime

# ---------------- App setup ----------------
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback_secret_key")
DB_NAME = "health.db"

# ---------------- Database init ----------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    email TEXT,
                    password TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS health_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    weight REAL,
                    bp TEXT,
                    heart_rate INTEGER,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    conn.commit()
    conn.close()

init_db()

# ---------------- Jinja filter ----------------
@app.template_filter('datetimeformat')
def datetimeformat(value):
    if not value:
        return ""
    try:
        return datetime.strptime(value, '%Y-%m-%d %H:%M:%S').strftime('%d %b %Y %H:%M')
    except Exception:
        return str(value)

# ---------------- Helper functions ----------------
def get_user_by_credentials(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, username FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    return user

def analyze_health(entries):
    if not entries:
        return "No data to analyze.", [], (
            "General Diet Plan:\n"
            "- Breakfast: Oats/Idli with fruits\n"
            "- Lunch: Brown rice/Chapati + dal + vegetables\n"
            "- Evening snack: Nuts or fruit\n"
            "- Dinner: Light meal (soup/salad)\n"
            "- Hydration: 2-3 liters daily\n"
        )

    weights = [e[2] for e in entries if e[2] is not None]
    bps = [e[3] for e in entries if e[3]]
    hrs = [e[4] for e in entries if e[4] is not None]

    suggestions, risks = [], []

    if weights:
        avg_w = sum(weights) / len(weights)
        if avg_w < 50:
            risks.append("Underweight — possible nutrient deficiency.")
            suggestions.append("Increase calories, add protein-rich foods.")
        elif avg_w > 80:
            risks.append("Overweight — possible metabolic issues.")
            suggestions.append("Cut sugar, increase exercise.")
        else:
            suggestions.append("Weight in healthy range.")

    if bps:
        systolics, diastolics = [], []
        for bp in bps:
            try:
                s, d = bp.split("/")
                systolics.append(int(s))
                diastolics.append(int(d))
            except:
                continue
        if systolics and diastolics:
            avg_s = sum(systolics) / len(systolics)
            avg_d = sum(diastolics) / len(diastolics)
            if avg_s > 140 or avg_d > 90:
                risks.append("High BP — hypertension risk.")
                suggestions.append("Reduce salt, avoid fried foods, do cardio.")
            elif avg_s < 100 or avg_d < 60:
                risks.append("Low BP — dizziness risk.")
                suggestions.append("Stay hydrated, eat balanced meals.")
            else:
                suggestions.append("Blood pressure normal.")

    if hrs:
        avg_hr = sum(hrs) / len(hrs)
        if avg_hr > 100:
            risks.append("High heart rate — tachycardia.")
            suggestions.append("Reduce caffeine, manage stress.")
        elif avg_hr < 60:
            risks.append("Low heart rate — bradycardia.")
            suggestions.append("If dizzy, seek doctor. Otherwise may be fit.")
        else:
            suggestions.append("Heart rate normal.")

    diet_plan = (
        "🍏 Suggested Diet:\n"
        "- Breakfast: Oats/Idli + fruit\n"
        "- Lunch: Brown rice/Chapati + dal + veggies\n"
        "- Snack: Nuts/Greek yogurt\n"
        "- Dinner: Light veg soup/salad\n"
        "- Hydration: 2-3 L water daily\n"
    )

    return "\n".join(suggestions), risks, diet_plan

# ---------------- Routes ----------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            return "Username and password required."

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
            return "Username already exists!"
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = get_user_by_credentials(username, password)
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
            weight = request.form.get("weight", "").strip()
            bp = request.form.get("bp", "").strip()
            heart_rate = request.form.get("heart_rate", "").strip()
            notes = request.form.get("notes", "").strip()

            weight_val = float(weight) if weight else None
            heart_rate_val = int(heart_rate) if heart_rate else None
        except ValueError:
            return "Invalid numeric input."

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(
            "INSERT INTO health_entries (user_id, weight, bp, heart_rate, notes) VALUES (?, ?, ?, ?, ?)",
            (user_id, weight_val, bp if bp else None, heart_rate_val, notes if notes else None)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("health"))

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

    # Table
    pdf.set_font("Arial", "B", 12)
    headers = ["Weight", "BP", "Heart Rate", "Notes", "Date"]
    for h in headers:
        pdf.cell(38, 10, h, 1, 0, "C")
    pdf.ln(10)

    pdf.set_font("Arial", "", 12)
    if entries:
        for e in entries:
            weight = str(e[2]) if e[2] else "-"
            bp = e[3] if e[3] else "-"
            hr = str(e[4]) if e[4] else "-"
            notes = e[5] if e[5] else "-"
            date = e[6] if e[6] else "-"
            pdf.cell(38, 10, weight, 1, 0, "C")
            pdf.cell(38, 10, bp, 1, 0, "C")
            pdf.cell(38, 10, hr, 1, 0, "C")
            pdf.cell(38, 10, notes, 1, 0, "C")
            pdf.cell(38, 10, date, 1, 1, "C")
    else:
        pdf.cell(190, 10, "No entries available.", 1, 1, "C")

    # Analysis
    suggestions, risks, diet_plan = analyze_health(entries)
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Health Analysis", ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, suggestions)

    if risks:
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "⚠️ Possible Risks:", ln=True)
        pdf.set_font("Arial", "", 12)
        for r in risks:
            pdf.multi_cell(0, 10, f"- {r}")

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Diet Plan:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, diet_plan)

    # ✅ FIX for Render crash
    pdf_output = BytesIO()
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_output.write(pdf_bytes)
    pdf_output.seek(0)

    return send_file(pdf_output,
                     as_attachment=True,
                     download_name=f"{session['username']}_health_report.pdf",
                     mimetype="application/pdf")

# ---------------- Run ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
