from flask import Blueprint, request, jsonify
from database import get_db
from routes.auth import get_current_user
from services.ai_service import generate_questions
from datetime import datetime
import json

quiz_bp = Blueprint("quiz", __name__)


@quiz_bp.route("/generate", methods=["POST"])
def generate_quiz():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    document_id = data.get("document_id")
    difficulty = data.get("difficulty", "medium")
    num_mcq = int(data.get("num_mcq", 10))
    num_theory = int(data.get("num_theory", 5))
    question_types = data.get("question_types", ["mcq", "theory"])

    if not document_id:
        return jsonify({"error": "document_id is required"}), 400

    if difficulty not in ["easy", "medium", "hard"]:
        return jsonify({"error": "difficulty must be easy, medium, or hard"}), 400

    num_mcq = max(1, min(num_mcq, 20))
    num_theory = max(1, min(num_theory, 10))

    db = get_db()

    # Fetch document and verify ownership
    doc_result = db.table("documents").select("*").eq("id", document_id).eq("user_id", user["user_id"]).execute()
    if not doc_result.data:
        return jsonify({"error": "Document not found or access denied"}), 404

    doc = doc_result.data[0]
    extracted_text = doc["extracted_text"]

    # Generate questions via AI service
    questions = generate_questions(
        text=extracted_text,
        difficulty=difficulty,
        num_mcq=num_mcq if "mcq" in question_types else 0,
        num_theory=num_theory if "theory" in question_types else 0
    )

    if not questions:
        return jsonify({"error": "Failed to generate questions. Please try again."}), 500

    # Save quiz to database
    quiz_result = db.table("quizzes").insert({
        "user_id": user["user_id"],
        "document_id": document_id,
        "title": doc["filename"].replace(".pdf", "").replace("_", " "),
        "difficulty": difficulty,
        "num_mcq": len(questions.get("mcq", [])),
        "num_theory": len(questions.get("theory", [])),
        "questions": json.dumps(questions),
        "created_at": datetime.utcnow().isoformat()
    }).execute()

    quiz = quiz_result.data[0]

    return jsonify({
        "message": "Quiz generated successfully",
        "quiz": {
            "id": quiz["id"],
            "title": quiz["title"],
            "difficulty": quiz["difficulty"],
            "num_mcq": quiz["num_mcq"],
            "num_theory": quiz["num_theory"],
            "questions": questions
        }
    }), 201


@quiz_bp.route("/", methods=["GET"])
def get_my_quizzes():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    db = get_db()
    result = db.table("quizzes").select(
        "id, title, difficulty, num_mcq, num_theory, created_at"
    ).eq("user_id", user["user_id"]).order("created_at", desc=True).execute()

    return jsonify({"quizzes": result.data})


@quiz_bp.route("/<quiz_id>", methods=["GET"])
def get_quiz(quiz_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    db = get_db()
    result = db.table("quizzes").select("*").eq("id", quiz_id).execute()

    if not result.data:
        return jsonify({"error": "Quiz not found"}), 404

    quiz = result.data[0]

    # Allow access if owner or if shared
    if quiz["user_id"] != user["user_id"] and not quiz.get("is_shared"):
        return jsonify({"error": "Access denied"}), 403

    quiz["questions"] = json.loads(quiz["questions"])
    return jsonify({"quiz": quiz})


@quiz_bp.route("/<quiz_id>/share", methods=["POST"])
def share_quiz(quiz_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    db = get_db()
    result = db.table("quizzes").select("*").eq("id", quiz_id).eq("user_id", user["user_id"]).execute()

    if not result.data:
        return jsonify({"error": "Quiz not found or access denied"}), 404

    db.table("quizzes").update({"is_shared": True}).eq("id", quiz_id).execute()

    share_link = f"http://localhost:3000/shared/{quiz_id}"

    return jsonify({
        "message": "Quiz is now shareable",
        "share_link": share_link,
        "quiz_id": quiz_id
    })


@quiz_bp.route("/shared/<quiz_id>", methods=["GET"])
def get_shared_quiz(quiz_id):
    db = get_db()
    result = db.table("quizzes").select("*").eq("id", quiz_id).eq("is_shared", True).execute()

    if not result.data:
        return jsonify({"error": "Shared quiz not found"}), 404

    quiz = result.data[0]
    quiz["questions"] = json.loads(quiz["questions"])
    # Hide correct answers for shared quizzes
    for q in quiz["questions"].get("mcq", []):
        q.pop("answer", None)

    return jsonify({"quiz": quiz})
