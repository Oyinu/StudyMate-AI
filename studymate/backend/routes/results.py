from flask import Blueprint, request, jsonify
from database import get_db
from routes.auth import get_current_user
from datetime import datetime
import json

results_bp = Blueprint("results", __name__)


@results_bp.route("/submit", methods=["POST"])
def submit_result():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    quiz_id = data.get("quiz_id")
    mcq_answers = data.get("mcq_answers", {})   # { "0": "A", "1": "C", ... }
    theory_answers = data.get("theory_answers", {})  # { "0": "student text..." }
    time_taken = data.get("time_taken", 0)       # seconds

    if not quiz_id:
        return jsonify({"error": "quiz_id is required"}), 400

    db = get_db()

    # Fetch quiz
    quiz_result = db.table("quizzes").select("*").eq("id", quiz_id).execute()
    if not quiz_result.data:
        return jsonify({"error": "Quiz not found"}), 404

    quiz = quiz_result.data[0]
    questions = json.loads(quiz["questions"])
    mcq_questions = questions.get("mcq", [])
    theory_questions = questions.get("theory", [])

    # Auto-mark MCQs
    mcq_score = 0
    mcq_feedback = []
    for i, q in enumerate(mcq_questions):
        student_ans = mcq_answers.get(str(i), "").upper()
        correct_ans = q.get("answer", "").upper()
        is_correct = student_ans == correct_ans
        if is_correct:
            mcq_score += 1
        mcq_feedback.append({
            "question_index": i,
            "question": q["question"],
            "student_answer": student_ans,
            "correct_answer": correct_ans,
            "is_correct": is_correct,
            "options": q.get("options", [])
        })

    # Calculate percentage
    total_mcq = len(mcq_questions)
    mcq_percentage = round((mcq_score / total_mcq * 100) if total_mcq > 0 else 0)

    # Assign grade
    grade = "F"
    if mcq_percentage >= 70:
        grade = "A"
    elif mcq_percentage >= 60:
        grade = "B"
    elif mcq_percentage >= 50:
        grade = "C"
    elif mcq_percentage >= 45:
        grade = "D"
    elif mcq_percentage >= 40:
        grade = "E"

    # Format time taken
    mins = time_taken // 60
    secs = time_taken % 60
    time_display = f"{mins}:{str(secs).zfill(2)}"

    # Save result
    result_data = db.table("results").insert({
        "user_id": user["user_id"],
        "quiz_id": quiz_id,
        "mcq_score": mcq_score,
        "total_mcq": total_mcq,
        "mcq_percentage": mcq_percentage,
        "grade": grade,
        "time_taken_seconds": time_taken,
        "time_display": time_display,
        "theory_answers": json.dumps(theory_answers),
        "mcq_feedback": json.dumps(mcq_feedback),
        "submitted_at": datetime.utcnow().isoformat()
    }).execute()

    saved_result = result_data.data[0]

    return jsonify({
        "message": "Quiz submitted successfully",
        "result": {
            "id": saved_result["id"],
            "mcq_score": mcq_score,
            "total_mcq": total_mcq,
            "mcq_percentage": mcq_percentage,
            "grade": grade,
            "time_display": time_display,
            "theory_submitted": len(theory_answers),
            "total_theory": len(theory_questions),
            "feedback": mcq_feedback
        }
    }), 201


@results_bp.route("/quiz/<quiz_id>", methods=["GET"])
def get_quiz_results(quiz_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    db = get_db()
    result = db.table("results").select(
        "id, mcq_score, total_mcq, mcq_percentage, grade, time_display, submitted_at"
    ).eq("quiz_id", quiz_id).eq("user_id", user["user_id"]).order("submitted_at", desc=False).execute()

    return jsonify({"results": result.data})


@results_bp.route("/stats", methods=["GET"])
def get_stats():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    db = get_db()

    quizzes = db.table("quizzes").select("id").eq("user_id", user["user_id"]).execute()
    results = db.table("results").select("mcq_percentage").eq("user_id", user["user_id"]).execute()

    total_quizzes = len(quizzes.data)
    all_scores = [r["mcq_percentage"] for r in results.data]
    avg_score = round(sum(all_scores) / len(all_scores)) if all_scores else 0
    best_score = max(all_scores) if all_scores else 0
    total_attempts = len(all_scores)

    return jsonify({
        "stats": {
            "total_quizzes": total_quizzes,
            "total_attempts": total_attempts,
            "average_score": avg_score,
            "best_score": best_score
        }
    })
