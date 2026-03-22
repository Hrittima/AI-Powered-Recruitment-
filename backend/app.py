import sys
import os
import uuid
import traceback

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

from core.resume_parser import extract_text
from core.scoring_engine import score_resume
from core.ranking_engine import get_rank
from core.recommendation import recommend_skills
from core.database import init_db, save_resume, get_all_resumes
from core.vector_store import store_resume, match_resume

# ── App config ────────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

init_db()

# ── Helpers ───────────────────────────────────────────────────────────────────
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ── Health ────────────────────────────────────────────────────────────────────
@app.route("/")
def home():
    return jsonify({"status": "ok", "message": "Backend running 🚀"})

# ── Analyze ───────────────────────────────────────────────────────────────────
@app.route("/api/analyze", methods=["POST"])
def analyze():
    try:
        file = request.files.get("resume")

        if not file:
            return jsonify({"error": "No file uploaded"}), 400
        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400
        if not allowed_file(file.filename):
            return jsonify({"error": "Only PDF, DOC, DOCX files are supported"}), 400

        # Save file
        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
        file.save(filepath)

        # Extract text
        text = extract_text(filepath)
        if not text.strip():
            return jsonify({"error": "Could not extract text from the file. Is it a scanned PDF?"}), 422

        # Keyword score
        score, matched, missing = score_resume(text)

        # Vector score (graceful — returns 0 if Pinecone not configured)
        try:
            vector_score = match_resume(text) * 100
        except Exception as e:
            print(f"Vector match error: {e}")
            vector_score = 0

        # Final score
        final_score = int((score * 0.6) + (vector_score * 0.4))
        final_score = max(0, min(100, final_score))

        # Store vector (fire-and-forget)
        try:
            store_resume(unique_name, text)
        except Exception as e:
            print(f"Vector store error: {e}")

        # Rank & recommendations
        rank = get_rank(final_score)
        recommendations = recommend_skills(missing)

        # FIX: save_resume now correctly called with 4 args (name, score, matched, rank)
        save_resume(filename, final_score, matched, rank)

        return jsonify({
            "score": final_score,
            "rank": rank,
            "vector_score": round(vector_score, 2),
            "keywords": matched,
            "missing": missing,
            "recommendations": recommendations
        })

    except Exception as e:
        print("ERROR in /api/analyze:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ── History (FIX: was missing — history.html calls this) ─────────────────────
@app.route("/api/history", methods=["GET"])
def history():
    try:
        resumes = get_all_resumes()
        return jsonify(resumes)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)