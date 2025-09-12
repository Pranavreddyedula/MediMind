from flask import Flask, render_template, request, send_file
from fpdf import FPDF
import io

app = Flask(__name__)

# Temporary storage for demo (later you can use a database)
health_data = []

@app.route("/")
def home():
    return render_template("index.html", health_data=health_data)

@app.route("/add", methods=["POST"])
def add():
    entry = {
        "date": request.form["date"],
        "weight": request.form["weight"],
        "bp": request.form["bp"],
        "sugar": request.form["sugar"]
    }
    health_data.append(entry)
    return render_template("index.html", health_data=health_data)

@app.route("/download")
def download_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "MediMind Health Report", ln=True, align="C")

    for entry in health_data:
        pdf.cell(200, 10, f"Date: {entry['date']} | Weight: {entry['weight']} | BP: {entry['bp']} | Sugar: {entry['sugar']}", ln=True)

    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)

    return send_file(pdf_output, as_attachment=True, download_name="health_report.pdf", mimetype="application/pdf")

if __name__ == "__main__":
    app.run(debug=True)
