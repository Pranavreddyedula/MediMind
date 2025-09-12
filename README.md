# MediMind - Health Tracking Web App

MediMind is a simple and intuitive health tracking web application that allows users to log their health metrics such as weight, blood pressure, heart rate, and notes. Users can also download their health data as a PDF report.

## Features

- User Registration and Login
- Health Entry Form (Weight, Blood Pressure, Heart Rate, Notes)
- Persistent Data Storage using SQLite
- PDF Report Generation
- Secure User Sessions

## Folder Structure

MediMind/
├── app.py
├── health.db
├── requirements.txt
├── static/
│ └── style.css
└── templates/
├── index.html
├── about.html
├── login.html
├── register.html
└── health.html


## Installation

1. Clone the repository:

git clone https://github.com/pranavreddyedula/MediMind.git
cd MediMind

2.Create a virtual environment and activate it:

python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

3.Install dependencies:
pip install -r requirements.txt

4.Run the app locally:
python app.py
Open your browser and visit http://127.0.0.1:5000.

Deployment on Render
1.Push your code to GitHub.

2.Create a new Web Service on Render.

3.Connect your GitHub repository.

4.Set Build Command: pip install -r requirements.txt

5.Set Start Command: gunicorn app:app

6.Deploy your app.
Your app will be available at the Render URL provided (e.g., https://medimind-1-hgh0.onrender.com).

Technologies Used
1.Python 3

2.Flask

3.SQLite

4.FPDF (PDF Report Generation)

5.HTML, CSS
