from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config
from models import db
from db_utils import initialize_db, create_user, get_user_by_email, validate_user
import random
from quiz_data import quiz
from sqlalchemy import inspect
import logging

# Initialize Flask App
app = Flask(__name__)
app.config.from_object(Config)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
app.logger.setLevel(logging.INFO)

# Initialize Extensions
db.init_app(app)
limiter = Limiter(get_remote_address, app=app)


@app.before_request
def make_session_permanent():
    """Ensure sessions are permanent and set a suitable duration."""
    session.permanent = True
    app.permanent_session_lifetime = Config.SESSION_LIFETIME
    app.logger.debug("Session set to permanent.")


# Utility Functions
def is_logged_in():
    """Check if the user is logged in."""
    logged_in = "user" in session
    app.logger.debug(f"User logged in: {logged_in}")
    return logged_in


def redirect_to_login():
    """Redirect to the login page if the user is not logged in."""
    if not is_logged_in():
        app.logger.warning("Unauthorized access attempt. Redirecting to login.")
        return redirect(url_for("login"))


@app.route("/")
def home():
    """Redirect to the first question after initializing quiz state."""
    if not is_logged_in():
        return redirect_to_login()
    app.logger.info("Accessed home route.")
    session["correct_answers"] = session.get("correct_answers", 0)
    session["answered_questions"] = session.get("answered_questions", 0)
    if "quiz_indices" not in session:
        session["quiz_indices"] = random.sample(range(len(quiz)), len(quiz))
        app.logger.debug("Initialized quiz state for session.")
    return redirect(url_for("question", qid=0))


@app.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    """Handle user login."""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        app.logger.info(f"Login attempt for email: {email}")
        try:
            if validate_user(email, password):
                session["user"] = email
                app.logger.info(f"User logged in successfully: {email}")
                return redirect(url_for("home"))
            app.logger.warning(f"Invalid login attempt for email: {email}")
            flash("Invalid email or password. Please try again.", "danger")
        except Exception as e:
            app.logger.error(f"Login error for email {email}: {e}")
            flash("An error occurred during login. Please try again.", "danger")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Handle user registration."""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        app.logger.info(f"Registration attempt for email: {email}")
        try:
            if not email or not password or not confirm_password:
                app.logger.warning("Registration failed: Missing fields.")
                flash("All fields are required. Please try again.", "danger")
                return redirect(url_for("register"))
            if password != confirm_password:
                app.logger.warning("Registration failed: Passwords do not match.")
                flash("Passwords do not match. Please try again.", "danger")
                return redirect(url_for("register"))
            if get_user_by_email(email):
                app.logger.warning(
                    f"Registration failed: Email already registered ({email})."
                )
                flash("Email already registered. Please log in.", "danger")
                return redirect(url_for("login"))

            create_user(email, password)
            app.logger.info(f"User registered successfully: {email}")
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            app.logger.error(f"Registration error for email {email}: {e}")
            flash("An error occurred during registration. Please try again.", "danger")
    return render_template("register.html")


@app.route("/question/<int:qid>")
def question(qid):
    """Display the quiz question."""
    if not is_logged_in():
        return redirect_to_login()

    # Retrieve the quiz indices from the session
    quiz_indices = session.get("quiz_indices", [])
    if not (0 <= qid < len(quiz_indices)):
        # Redirect to the finish page if the question ID is invalid
        return redirect(url_for("finish"))

    question_index = quiz_indices[qid]
    current_question = quiz[question_index]

    # Log debugging information
    app.logger.debug(f"Rendering question {qid}: {current_question}")

    # Render the quiz question
    return render_template(
        "quiz.html",
        quiz=current_question,
        qid=qid,  # Ensure qid is passed to the template
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

    # Retrieve the quiz indices from the session
    quiz_indices = session.get("quiz_indices", [])
    if not (0 <= qid < len(quiz_indices)):
        # Redirect to the finish page if the question ID is invalid
        return redirect(url_for("finish"))

    question_index = quiz_indices[qid]
    current_question = quiz[question_index]

    # Retrieve the user's answer
    user_answer = request.form.get("answer")
    if not user_answer:
        flash("No answer selected. Please try again.", "warning")
        return redirect(url_for("question", qid=qid))

    # Update session data
    session["answered_questions"] += 1
    if user_answer == current_question["answer"]:
        session["correct_answers"] += 1

    # Render the result
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


@app.route("/logout")
def logout():
    """Handle user logout."""
    user = session.pop("user", None)
    app.logger.info(f"User logged out: {user}")
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("login"))


@app.route("/finish")
def finish():
    """Display the quiz completion summary."""
    if not is_logged_in():
        return redirect_to_login()
    correct_answers = session.get("correct_answers", 0)
    answered_questions = session.get("answered_questions", 0)
    score_percentage = (
        round((correct_answers / answered_questions) * 100, 0)
        if answered_questions
        else 0
    )
    app.logger.info(
        f"Quiz finished. Score: {score_percentage}% ({correct_answers}/{answered_questions})"
    )
    return render_template(
        "finish.html",
        answered=answered_questions,
        correct=correct_answers,
        percentage=score_percentage,
    )


# Run Application
if __name__ == "__main__":
    # Initialize the database
    initialize_db(app)
    app.logger.info("Starting the Flask application.")
    app.run(debug=True)
