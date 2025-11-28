from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os 
from dotenv import load_dotenv

# Load environment variables (needed to read the PORT variable from Render)
load_dotenv() 

app = Flask(__name__)

# ------------------------
# DEPLOYMENT & DATABASE SETUP
# ------------------------
# 1. *** IMPORTANT: Set a secret key for session security ***
#    CHANGE THIS TO A LONG, RANDOM, AND COMPLEX STRING BEFORE DEPLOYMENT!
app.config["SECRET_KEY"] = "wisdom@13071998"

# Note: The sqlite:///quiz.db will create a new, empty database on every deploy on Render.
# For persistent data, you would need to use a hosted database like Postgres.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///quiz.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Database table model
class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    score = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Create database tables
with app.app_context():
    db.create_all()

# ------------------------
# QUIZ DATA (Unchanged)
# ------------------------
questions = [
    "What is the capital town of Ghana?",
    "Who was the first president of Ghana?",
    "Who was the vice president for Professor Atta Mills?",
    "Who is the minority leader of NDC in the 8th parliament?",
    "Who is the current finance minister?"
]

options = [
    ["A. Tamale", "B. Sunyani", "C. Cape Coast", "D. Accra"],
    ["A. Atta Mills", "B. Rawlings", "C. Kwame Nkrumah", "D. Kufuor"],
    ["A. Aliu Mahama", "B. John Mahama", "C. Bawumia", "D. Akufo-Addo"],
    ["A. Alban Bagbin", "B. Haruna Idrisu", "C. Ato Forson", "D. Afenyo Markin"],
    ["A. Ken Ofori Atta", "B. Ato Forson", "C. Haruna Idrisu", "D. Abu Jinapor"]
]

answers = ["D", "C", "B", "C", "B"]

# ------------------------
# ROUTES
# ------------------------

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if request.method == "POST":
        username = request.form["username"].title()

        guesses = []
        score = 0

        for i in range(len(questions)):
            user_answer = request.form.get(f"q{i}")
            guesses.append(user_answer)

            if user_answer == answers[i]:
                score += 1

        percentage = int((score / len(questions)) * 100)

        # SAVE RESULT IN DATABASE
        result = QuizResult(name=username, score=percentage)
        db.session.add(result)
        db.session.commit()

        return render_template("result.html",
                               username=username,
                               questions=questions,
                               answers=answers,
                               guesses=guesses,
                               score=percentage)

    return render_template("quiz.html", questions=questions, options=options)

@app.route("/history")
def history():
    # --- LEADERBOARD LOGIC ---
    # Fetch top 10 results: order by score (desc), then by timestamp (asc for tie-breaker)
    all_results = QuizResult.query.order_by(
        QuizResult.score.desc(),
        QuizResult.timestamp.asc()
    ).limit(10).all()
    # The template history.html will now act as a leaderboard
    return render_template("history.html", results=all_results)


if __name__ == "__main__":
    # Get the PORT environment variable from Render (default to 5000 if not set)
    port = int(os.environ.get('PORT', 5000)) 
    # Use the Flask development server instead of Gunicorn
    app.run(host='0.0.0.0', port=port, debug=False)