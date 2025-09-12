from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from fpdf import FPDF
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class HealthEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float, nullable=False)
    blood_pressure = db.Column(db.String(20), nullable=False)
    heart_rate = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

# Ensure database is created inside app context
with app.app_context():
    db.create_all()

# Home Route
@app.route('/')
def index():
    return render_template('index.html')

# About Page
@app.route('/about')
def about():
    return render_template('about.html')

# Health Entry Form & List
@app.route('/health', methods=['GET', 'POST'])
def health():
    if request.method == 'POST':
        weight = request.form['weight']
        blood_pressure = request.form['blood_pressure']
        heart_rate = request.form['heart_rate']
        notes = request.form['notes']

        new_entry = HealthEntry(
            weight=weight,
            blood_pressure=blood_pressure,
            heart_rate=heart_rate,
            notes=notes
        )
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('health'))

    entries = HealthEntry.query.all()
    return render_template('health.html', entries=entries)

# PDF Download
@app.route('/download_pdf')
def download_pdf():
    entries = HealthEntry.query.all()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="MediMind Health Report", ln=True, align="C")
    pdf.ln(10)

    for e in entries:
        pdf.cell(200, 10, txt=f"Weight: {e.weight} kg, BP: {e.blood_pressure}, Heart Rate: {e.heart_rate}, Notes: {e.notes}", ln=True)

    pdf_file = "health_report.pdf"
    pdf.output(pdf_file)
    return send_file(pdf_file, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
