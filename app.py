from flask import Flask, render_template
import os

app = Flask(__name__)

# Home page
@app.route("/")
def home():
    return render_template("index.html")

# About page
@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    # Only for local testing
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
