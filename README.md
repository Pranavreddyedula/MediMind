# 🧠 MediMind - Health Tracking Web App

MediMind is a simple and intuitive health tracking web application that allows users to log their health metrics such as **weight, blood pressure, heart rate, and notes**.  
Users can also securely download their health data as a **PDF report**.

---

## ✨ Features
- 🔐 User Registration and Login  
- 📝 Health Entry Form (Weight, Blood Pressure, Heart Rate, Notes)  
- 💾 Persistent Data Storage using **SQLite**  
- 📄 PDF Report Generation  
- 🔑 Secure User Sessions  

---

## 📂 Folder Structure
MediMind/
├── app.py
├── health.db
├── requirements.txt
├── Procfile
├── static/
│ └── style.css
└── templates/
├── index.html
├── about.html
├── login.html
├── register.html
└── health.html

yaml
Copy code

---

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/pranavreddyedula/MediMind.git
   cd MediMind
Create and activate a virtual environment

bash
Copy code
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
Install dependencies

bash
Copy code
pip install -r requirements.txt
Run the app locally

bash
Copy code
python app.py
Then open 👉 http://127.0.0.1:5000 in your browser.

🚀 Deployment (Render)
Push your code to GitHub.

Create a new Web Service on Render.

Connect your GitHub repository.

Set Build Command:

bash
Copy code
pip install -r requirements.txt
Set Start Command:

bash
Copy code
gunicorn app:app
Deploy 🎉

Your app will be available at your Render URL (example: https://medimind.onrender.com).

🛠️ Technologies Used
Python 3

Flask

SQLite

FPDF (PDF Report Generation)

HTML, CSS

🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change.
