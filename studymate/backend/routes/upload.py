from flask import Blueprint, request, jsonify
from database import get_db
from routes.auth import get_current_user
from services.pdf_parser import extract_text_from_pdf
import os
from datetime import datetime

upload_bp = Blueprint("upload", __name__)

ALLOWED_EXTENSIONS = {"pdf"}
BUCKET = os.getenv("SUPABASE_BUCKET", "studymate-pdfs")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route("/pdf", methods=["POST"])
def upload_pdf():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    file_bytes = file.read()

    if len(file_bytes) > 20 * 1024 * 1024:
        return jsonify({"error": "File too large. Maximum size is 20MB"}), 400

    # Extract text from PDF
    extracted_text = extract_text_from_pdf(file_bytes)

    if not extracted_text or len(extracted_text.strip()) < 100:
        return jsonify({"error": "Could not extract enough text from this PDF. Make sure it is not a scanned image."}), 422

    # Upload to Supabase Storage
    db = get_db()
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    safe_name = file.filename.replace(" ", "_").replace("/", "_")
    storage_path = f"{user['user_id']}/{timestamp}_{safe_name}"

    try:
        db.storage.from_(BUCKET).upload(storage_path, file_bytes, {"content-type": "application/pdf"})
        file_url = db.storage.from_(BUCKET).get_public_url(storage_path)
    except Exception:
        # If storage fails, continue without storing URL (text is already extracted)
        file_url = None
        storage_path = None

    # Save document record to database
    doc_result = db.table("documents").insert({
        "user_id": user["user_id"],
        "filename": file.filename,
        "storage_path": storage_path,
        "file_url": file_url,
        "extracted_text": extracted_text[:50000],  # Store first 50k chars
        "char_count": len(extracted_text),
        "created_at": datetime.utcnow().isoformat()
    }).execute()

    doc = doc_result.data[0]

    return jsonify({
        "message": "PDF uploaded and text extracted successfully",
        "document": {
            "id": doc["id"],
            "filename": doc["filename"],
            "char_count": doc["char_count"],
            "preview": extracted_text[:300] + "..."
        }
    }), 201
