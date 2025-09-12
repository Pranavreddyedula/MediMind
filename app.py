from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from fpdf import FPDF
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# ===== Database Models =====
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class HealthEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    weight = db.Column(db.Float)
    bp = db.Column(db.String(20))
    heart_rate = db.Column(db.Integer)
    notes = db.Column(db.String(200))

db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ===== Routes =====
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return "Username already exists!"
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('health'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('health'))
        return "Invalid credentials!"
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/health', methods=['GET', 'POST'])
@login_required
def health():
    if request.method == 'POST':
        weight = float(request.form['weight'])
        bp = request.form['bp']
        heart_rate = int(request.form['heart_rate'])
        notes = request.form.get('notes', '')

        new_entry = HealthEntry(
            user_id=current_user.id,
            weight=weight,
            bp=bp,
            heart_rate=heart_rate,
            notes=notes
        )
        db.session.add(new_entry)
        db.session.commit()

        # Generate PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"MediMind Health Report for {current_user.username}", ln=True, align='C')
        pdf.ln(10)
        pdf.cell(0, 10, f"Weight: {weight} kg", ln=True)
        pdf.cell(0, 10, f"Blood Pressure: {bp}", ln=True)
        pdf.cell(0, 10, f"Heart Rate: {heart_rate} bpm", ln=True)
        pdf.cell(0, 10, f"Notes: {notes}", ln=True)

        pdf_file = f"{current_user.username}_health_report.pdf"
        pdf.output(pdf_file)
        return send_file(pdf_file, as_attachment=True)

    entries = HealthEntry.query.filter_by(user_id=current_user.id).all()
    return render_template('health.html', entries=entries)

if __name__ == '__main__':
    app.run(debug=True)

