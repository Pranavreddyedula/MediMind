# MediMind
A health tracking web app designed for students and individuals to monitor their daily health activities, symptoms, and mental well-being. Users can add, edit, and delete entries, manage their personal profiles, and track health progress over time. Built with simplicity and usability in mind, this project is free to use 
MediMind is a **personal health tracking web app** built with **Flask**. It allows users to track their health, monitor progress, and stay informed about their wellness.

---

## Features

- **Home Page**: Welcome message and overview.
- **About Page**: Information about the MediMind app.
- **Responsive Design**: Works on desktop and mobile.
- **Favicon and CSS Styling**: Clean and polished look.
- **Production-ready**: Deployable on Render using Gunicorn.

---

## Folder Structure

MediMind/
├── app.py
├── requirements.txt
├── templates/
│ ├── index.html
│ └── about.html
└── static/
├── style.css
└── favicon.ico

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/pranavreddyedula/MediMind.git
cd MediMind
2.Install dependencies:

pip install -r requirements.txt
3.Run the app locally:

python app.py

4.Open your browser and go to:

http://127.0.0.1:5000/
Deployment on Render

1.Connect your GitHub repo to Render.

2.Set Build Command:

pip install -r requirements.txt


3.Set Start Command:

gunicorn app:app


4.Optional: Add environment variable FLASK_ENV=production.

5.Deploy. Your app will be live at the Render URL.

Contributing

Feel free to fork, make changes, and submit a pull request.

License

This project is free to use for educational purposes.

GitHub Username: pranavreddyedula















