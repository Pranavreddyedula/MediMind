from flask import Flask, render_template, request, redirect, url_for, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import datetime

app = Flask(__name__)

# Store health logs in memory (later you can connect to DB if needed)
health_logs = []

@app.route("/")
def home():
    return render_template("index.html", logs=health_logs)

@app.route("/add", methods=["POST"])
def add():
    date = request.form.get("date")
    weight = request.form.get("weight")
    bp = request.form.get("bp")
    sugar = request.form.get("sugar")

    health_logs.append({
        "date": date,
        "weight": weight,
        "bp": bp,
        "sugar": sugar
    })

    return redirect(url_for("home"))

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/download")
def download():
    filename = "health_report.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica", 12)
    c.drawString(100, 750, "MediMind - Health Report")
    c.drawString(100, 735, f"Generated on: {datetime.date.today()}")

    y = 700
    for log in health_logs:
        entry = f"Date: {log['date']} | Weight: {log['weight']} kg | BP: {log['bp']} | Sugar: {log['sugar']}"
        c.drawString(100, y, entry)
        y -= 20

    c.save()
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)

