import os
import random

import bcrypt
from flask import Flask, redirect, render_template, request, session, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from quiz_data import quiz
from users import users  # Import users dictionary

# Flask App Configuration
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))  # Use secure secret key

# Cookie Security Settings
app.config.update(
    SESSION_COOKIE_SECURE=True,  # Only allow cookies over HTTPS
    SESSION_COOKIE_HTTPONLY=True,  # Prevent client-side access to cookies
    SESSION_COOKIE_SAMESITE="Lax"  # Prevent cross-site request forgery
)

# Rate Limiting Configuration
limiter = Limiter(get_remote_address, app=app)


# Utility Functions
def is_logged_in():
    """Check if the user is logged in."""
    return "user" in session


def redirect_to_login():
    """Redirect to the login page if the user is not logged in."""
    if not is_logged_in():
        return redirect(url_for("login"))


# Routes
@app.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")  # Limit to 10 login attempts per minute
def login():
    """Handle user login."""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password").encode('utf-8')  # Encode to bytes
        if email in users and bcrypt.checkpw(password, users[email]):  # Validate credentials
            session["user"] = email  # Store user session
            return redirect(url_for("home"))
        return "Invalid email or password. Please try again."
    return render_template("login.html")


@app.route("/logout")
def logout():
    """Handle user logout."""
    session.pop("user", None)  # Remove user session
    return redirect(url_for("login"))


@app.route("/")
def home():
    """Redirect to the first question after initializing quiz state."""
    if not is_logged_in():
        return redirect_to_login()
    session.update(
        correct_answers=0,
        answered_questions=0,
        quiz_indices=random.sample(range(len(quiz)), len(quiz))
    )
    return redirect(url_for("question", qid=0))


@app.route("/question/<int:qid>")
def question(qid):
    """Display the quiz question."""
    if not is_logged_in():
        return redirect_to_login()
    quiz_indices = session.get("quiz_indices", [])
    if not (0 <= qid < len(quiz_indices)):
        return redirect(url_for("finish"))
    question_index = quiz_indices[qid]
    current_question = quiz[question_index]
    return render_template(
        "quiz.html",
        quiz=current_question,
        qid=qid,
        total=len(quiz_indices),
        correct=session.get("correct_answers", 0),
        question_number=qid + 1,
        question_id=question_index,
    )


@app.route("/submit/<int:qid>", methods=["POST"])
def submit(qid):
    """Handle the answer submission."""
    if not is_logged_in():
        return redirect_to_login()
    quiz_indices = session.get("quiz_indices", [])
    if not (0 <= qid < len(quiz_indices)):
        return redirect(url_for("finish"))
    question_index = quiz_indices[qid]
    current_question = quiz[question_index]
    user_answer = request.form.get("answer")
    if not user_answer:
        return redirect(url_for("question", qid=qid))
    session["answered_questions"] += 1
    if user_answer == current_question["answer"]:
        session["correct_answers"] += 1
    user_answer_text = current_question["options"].get(user_answer, "No answer selected")
    correct_answer_text = current_question["options"][current_question["answer"]]
    return render_template(
        "result.html",
        correct=(user_answer == current_question["answer"]),
        quiz=current_question,
        user_answer=user_answer,
        user_answer_text=user_answer_text,
        correct_answer_text=correct_answer_text,
        next_qid=qid + 1,
        is_last=(qid + 1 >= len(quiz_indices)),
        correct_count=session["correct_answers"],
        total=len(quiz_indices),
    )


@app.route("/finish")
def finish():
    """Display the quiz completion summary."""
    if not is_logged_in():
        return redirect_to_login()
    correct_answers = session.get("correct_answers", 0)
    answered_questions = session.get("answered_questions", 0)
    score_percentage = round((correct_answers / answered_questions) * 100, 0) if answered_questions else 0
    return render_template(
        "finish.html",
        answered=answered_questions,
        correct=correct_answers,
        percentage=score_percentage,
    )


# Run Application
if __name__ == "__main__":
    app.run(debug=True)
