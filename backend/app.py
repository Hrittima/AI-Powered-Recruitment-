import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from werkzeug.utils import secure_filename

# CORE IMPORTS
from core.resume_parser import extract_text
from core.scoring_engine import score_resume
from core.ranking_engine import get_rank
from core.recommendation import recommend_skills
from core.database import init_db, save_resume, get_all_resumes

# ===============================
# APP CONFIG
# ===============================
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
init_db()

# ===============================
# HELPERS
# ===============================
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ===============================
# ROOT
# ===============================
@app.route("/")
def home():
    return "🚀 AI Resume Analyzer API Running"


# ===============================
# ANALYZE API
# ===============================
@app.route("/api/analyze", methods=["POST"])
def analyze():
    try:
        file = request.files.get("resume")

        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400

        # Save file
        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_name)
        file.save(filepath)

        # Extract text
        text = extract_text(filepath)

        if not text.strip():
            return jsonify({"error": "Text extraction failed"}), 400

        # SCORE ENGINE (FIXED)
        score, matched, missing = score_resume(text)

        # RANK
        rank = get_rank(score)

        # RECOMMENDATIONS (FIXED)
        recommendations = recommend_skills(text)

        # SAVE DB (FIXED SIMPLE VERSION)
        save_resume(filename, score, rank)

        # DEBUG
        print("SCORE:", score)

        return jsonify({
            "score": score,
            "rank": rank,
            "keywords": matched,
            "missing": missing,
            "recommendations": recommendations
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": "Server error"}), 500


# ===============================
# HISTORY API
# ===============================
@app.route("/api/history")
def history():
    return jsonify(get_all_resumes())


# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)