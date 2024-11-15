from flask import Flask, render_template, request, redirect, url_for, session
from quiz_data import quiz
import random

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session management

# --- ROUTES --- #


@app.route("/")
def home():
    """
    Initialize the quiz: reset session variables and shuffle question indices.
    Redirect to the first question.
    """
    session["correct_answers"] = 0
    session["answered_questions"] = 0
    session["quiz_indices"] = random.sample(
        range(len(quiz)), len(quiz)
    )  # Shuffle indices
    return redirect(url_for("question", qid=0))


@app.route("/question/<int:qid>")
def question(qid):
    """
    Display the current question based on the shuffled order.
    Redirect to the finish page if the question ID is invalid.
    """
    quiz_indices = session.get("quiz_indices", [])

    if not (0 <= qid < len(quiz_indices)):
        return redirect(url_for("finish"))

    # Retrieve the current question using the shuffled index
    question_index = quiz_indices[qid]
    current_question = quiz[question_index]

    return render_template(
        "quiz.html",
        quiz=current_question,
        qid=qid,
        total=len(quiz_indices),
        correct=session.get("correct_answers", 0),
        question_number=qid + 1,  # Display question number starting from 1
        question_id=question_index,  # Original question ID from the quiz list
    )


@app.route("/submit/<int:qid>", methods=["POST"])
def submit(qid):
    """
    Process the user's answer, update the session, and display the result page.
    Redirect to the finish page if the question ID is invalid.
    """
    quiz_indices = session.get("quiz_indices", [])

    if not (0 <= qid < len(quiz_indices)):
        return redirect(url_for("finish"))

    # Retrieve the current question
    question_index = quiz_indices[qid]
    current_question = quiz[question_index]
    user_answer = request.form.get("answer")

    # Redirect to the same question if no answer is provided
    if not user_answer:
        return redirect(url_for("question", qid=qid))

    # Update session stats
    session["answered_questions"] += 1
    if user_answer == current_question["answer"]:
        session["correct_answers"] += 1

    # Prepare data for the result page
    next_qid = qid + 1
    user_answer_text = current_question["options"].get(
        user_answer, "No answer selected"
    )
    correct_answer_text = current_question["options"][current_question["answer"]]

    return render_template(
        "result.html",
        correct=(user_answer == current_question["answer"]),
        quiz=current_question,
        user_answer=user_answer,
        user_answer_text=user_answer_text,
        correct_answer_text=correct_answer_text,
        next_qid=next_qid,
        is_last=(next_qid >= len(quiz_indices)),
        correct_count=session["correct_answers"],
        total=len(quiz_indices),
    )


@app.route("/finish")
def finish():
    """
    Display the final results, including the total score and percentage.
    """
    correct_answers = session.get("correct_answers", 0)
    answered_questions = session.get("answered_questions", 0)

    # Calculate the score percentage, avoiding division by zero
    score_percentage = (
        round((correct_answers / answered_questions) * 100, 0)
        if answered_questions
        else 0
    )

    return render_template(
        "finish.html",
        answered=answered_questions,
        correct=correct_answers,
        percentage=score_percentage,
    )


# --- MAIN --- #

if __name__ == "__main__":
    app.run(debug=True)
