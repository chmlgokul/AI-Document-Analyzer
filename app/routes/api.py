import os
import uuid

from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from app.models.document import Document

from app.services.text_extractor import extract_text
from app.services.keyword_extractor import extract_keywords
from app.services.information_extractor import extract_information
from app.services.summarizer import summarize_text
from app.services.cohere_service import generate_ai_analysis


api = Blueprint(
    "api",
    __name__,
    url_prefix="/api"
)


ALLOWED_EXTENSIONS = {
    "pdf",
    "docx",
    "txt",
    "jpg",
    "jpeg",
    "png"
}


def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =========================================================
# API TEST
# =========================================================

@api.route("/test", methods=["GET"])
def test_api():

    return jsonify({
        "success": True,
        "message": "AI Document Analyzer API is working!"
    })

# =========================================================
# API HEALTH CHECK
# =========================================================

@api.route("/health", methods=["GET"])
def health_check():

    return jsonify({
        "success": True,
        "status": "healthy",
        "service": "AI Document Analyzer API"
    })


# =========================================================
# GET USER DOCUMENTS
# =========================================================

@api.route("/documents", methods=["GET"])
@login_required
def get_documents():

    documents = Document.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Document.uploaded_at.desc()
    ).all()

    result = []

    for document in documents:

        result.append({
            "id": document.id,
            "filename": document.filename,
            "uploaded_at": str(document.uploaded_at)
        })

    return jsonify({
        "success": True,
        "count": len(result),
        "documents": result
    })


# =========================================================
# GET SINGLE DOCUMENT
# =========================================================

@api.route("/documents/<int:document_id>", methods=["GET"])
@login_required
def get_document(document_id):

    document = Document.query.filter_by(
        id=document_id,
        user_id=current_user.id
    ).first()

    if not document:

        return jsonify({
            "success": False,
            "message": "Document not found."
        }), 404

    return jsonify({
        "success": True,
        "document": {
            "id": document.id,
            "filename": document.filename,
            "uploaded_at": str(document.uploaded_at),
            "extracted_text": document.extracted_text
        }
    })


# =========================================================
# UPLOAD DOCUMENT API
# =========================================================

@api.route("/upload", methods=["POST"])
@login_required
def upload_document_api():

    # -----------------------------------------------------
    # Check uploaded file
    # -----------------------------------------------------

    file = (
        request.files.get("document")
        or request.files.get("file")
    )

    if file is None:

        return jsonify({
            "success": False,
            "message": "No file uploaded."
        }), 400


    # -----------------------------------------------------
    # Check filename
    # -----------------------------------------------------

    if not file.filename:

        return jsonify({
            "success": False,
            "message": "Please select a file."
        }), 400


    # -----------------------------------------------------
    # Validate extension
    # -----------------------------------------------------

    if not allowed_file(file.filename):

        return jsonify({
            "success": False,
            "message": (
                "Unsupported file type. "
                "Allowed: PDF, DOCX, TXT, JPG, JPEG, PNG."
            )
        }), 400


    # -----------------------------------------------------
    # Secure filename
    # -----------------------------------------------------

    original_filename = secure_filename(
        file.filename
    )

    if not original_filename:

        return jsonify({
            "success": False,
            "message": "Invalid filename."
        }), 400


    # -----------------------------------------------------
    # Create upload folder
    # -----------------------------------------------------

    upload_folder = os.path.join(
        current_app.instance_path,
        "uploads"
    )

    os.makedirs(
        upload_folder,
        exist_ok=True
    )


    # -----------------------------------------------------
    # Prevent filename collision
    # -----------------------------------------------------

    name, extension = os.path.splitext(
        original_filename
    )

    unique_filename = (
        f"{name}_{uuid.uuid4().hex[:8]}"
        f"{extension}"
    )

    filepath = os.path.join(
        upload_folder,
        unique_filename
    )


    # -----------------------------------------------------
    # Save file
    # -----------------------------------------------------

    try:

        file.save(filepath)

    except Exception as e:

        print(
            "API FILE SAVE ERROR:",
            repr(e)
        )

        return jsonify({
            "success": False,
            "message": "Failed to save uploaded file."
        }), 500


    # -----------------------------------------------------
    # Extract text
    # -----------------------------------------------------

    try:

        extracted_text = extract_text(
            filepath
        )

    except Exception as e:

        print(
            "API TEXT EXTRACTION ERROR:",
            repr(e)
        )

        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            pass

        return jsonify({
            "success": False,
            "message": "Text extraction failed."
        }), 500


    # -----------------------------------------------------
    # Check extracted text
    # -----------------------------------------------------

    if not extracted_text or not extracted_text.strip():

        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            pass

        return jsonify({
            "success": False,
            "message": (
                "No readable text could be extracted "
                "from the uploaded document."
            )
        }), 400


    # -----------------------------------------------------
    # Save document in database
    # -----------------------------------------------------

    try:

        document = Document(
            filename=original_filename,
            filepath=filepath,
            extracted_text=extracted_text,
            user_id=current_user.id
        )

        db.session.add(
            document
        )

        db.session.commit()

    except Exception as e:

        db.session.rollback()

        print(
            "API DATABASE ERROR:",
            repr(e)
        )

        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            pass

        return jsonify({
            "success": False,
            "message": "Failed to save document information."
        }), 500


    # -----------------------------------------------------
    # Keyword extraction
    # -----------------------------------------------------

    try:

        keywords = extract_keywords(
            extracted_text
        )

    except Exception as e:

        print(
            "API KEYWORD ERROR:",
            repr(e)
        )

        keywords = []


    # -----------------------------------------------------
    # Information extraction
    # -----------------------------------------------------

    try:

        information = extract_information(
            extracted_text
        )

    except Exception as e:

        print(
            "API INFORMATION EXTRACTION ERROR:",
            repr(e)
        )

        information = {}


    # -----------------------------------------------------
    # Rule-based summary
    # -----------------------------------------------------

    try:

        summary = summarize_text(
            extracted_text
        )

    except Exception as e:

        print(
            "API SUMMARY ERROR:",
            repr(e)
        )

        summary = ""


    # -----------------------------------------------------
    # Cohere AI analysis
    # -----------------------------------------------------

    try:

        ai_analysis = generate_ai_analysis(
            extracted_text
        )

    except Exception as e:

        print(
            "API COHERE ERROR:",
            repr(e)
        )

        ai_analysis = {
            "success": False,
            "summary": "",
            "insights": [],
            "message": "AI analysis failed."
        }


    # -----------------------------------------------------
    # Final JSON response
    # -----------------------------------------------------

    return jsonify({
        "success": True,
        "message": "Document uploaded and analyzed successfully.",

        "document": {
            "id": document.id,
            "filename": document.filename,
            "uploaded_at": str(document.uploaded_at)
        },

        "analysis": {

            "keywords": keywords,

            "information": information,

            "summary": summary,

            "ai_analysis": {
                "success": ai_analysis.get(
                    "success",
                    False
                ),

                "summary": ai_analysis.get(
                    "summary",
                    ""
                ),

                "insights": ai_analysis.get(
                    "insights",
                    []
                ),

                "message": ai_analysis.get(
                    "message",
                    ""
                )
            }
        }
    }), 201