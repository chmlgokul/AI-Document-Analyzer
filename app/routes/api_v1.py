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


# =========================================================
# API V1 BLUEPRINT
# =========================================================

api_v1 = Blueprint(
    "api_v1",
    __name__,
    url_prefix="/api/v1"
)


# =========================================================
# ALLOWED FILE EXTENSIONS
# =========================================================

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
# TEST API V1
# =========================================================

@api_v1.route(
    "/test",
    methods=["GET"]
)
def test_api_v1():

    return jsonify({
        "success": True,
        "message": "AI Document Analyzer API v1 is working!"
    })


# =========================================================
# HEALTH CHECK V1
# =========================================================

@api_v1.route(
    "/health",
    methods=["GET"]
)
def health_check_v1():

    return jsonify({
        "success": True,
        "status": "healthy",
        "service": "AI Document Analyzer API",
        "version": "v1"
    })


# =========================================================
# GET USER DOCUMENTS
# =========================================================

@api_v1.route(
    "/documents",
    methods=["GET"]
)
@login_required
def get_documents_v1():

    documents = Document.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Document.uploaded_at.desc()
    ).all()

    document_list = []

    for document in documents:

        document_list.append({
            "id": document.id,
            "filename": document.filename,
            "uploaded_at": (
                document.uploaded_at.isoformat()
                if document.uploaded_at
                else None
            )
        })

    return jsonify({
        "success": True,
        "version": "v1",
        "count": len(document_list),
        "documents": document_list
    })


# =========================================================
# GET SINGLE DOCUMENT
# =========================================================

@api_v1.route(
    "/documents/<int:document_id>",
    methods=["GET"]
)
@login_required
def get_document_v1(document_id):

    document = Document.query.filter_by(
        id=document_id,
        user_id=current_user.id
    ).first()

    if not document:

        return jsonify({
            "success": False,
            "message": "Document not found"
        }), 404

    return jsonify({
        "success": True,
        "version": "v1",
        "document": {
            "id": document.id,
            "filename": document.filename,
            "filepath": document.filepath,
            "extracted_text": document.extracted_text,
            "uploaded_at": (
                document.uploaded_at.isoformat()
                if document.uploaded_at
                else None
            )
        }
    })


# =========================================================
# UPLOAD DOCUMENT
# =========================================================

@api_v1.route(
    "/upload",
    methods=["POST"]
)
@login_required
def upload_document_v1():

    # -----------------------------------------------------
    # GET FILE
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
    # CHECK FILENAME
    # -----------------------------------------------------

    if not file.filename:

        return jsonify({
            "success": False,
            "message": "Please select a file."
        }), 400


    # -----------------------------------------------------
    # CHECK EXTENSION
    # -----------------------------------------------------

    if not allowed_file(file.filename):

        return jsonify({
            "success": False,
            "message": (
                "Unsupported file type. "
                "Allowed formats: PDF, DOCX, TXT, "
                "JPG, JPEG, PNG."
            )
        }), 400


    # -----------------------------------------------------
    # SECURE FILENAME
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
    # UPLOAD DIRECTORY
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
    # UNIQUE FILE NAME
    # -----------------------------------------------------

    unique_filename = (
        str(uuid.uuid4())
        + "_"
        + original_filename
    )

    filepath = os.path.join(
        upload_folder,
        unique_filename
    )


    # -----------------------------------------------------
    # SAVE FILE
    # -----------------------------------------------------

    try:

        file.save(filepath)

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Failed to save uploaded file.",
            "error": str(e)
        }), 500


    # -----------------------------------------------------
    # EXTRACT TEXT
    # -----------------------------------------------------

    try:

        extracted_text = extract_text(
            filepath
        )

    except Exception as e:

        if os.path.exists(filepath):

            os.remove(filepath)

        return jsonify({
            "success": False,
            "message": "Document text extraction failed.",
            "error": str(e)
        }), 500


    # -----------------------------------------------------
    # CHECK EXTRACTED TEXT
    # -----------------------------------------------------

    if not extracted_text or not extracted_text.strip():

        if os.path.exists(filepath):

            os.remove(filepath)

        return jsonify({
            "success": False,
            "message": (
                "No readable text could be extracted "
                "from the document."
            )
        }), 400


    # -----------------------------------------------------
    # CREATE DATABASE RECORD
    # -----------------------------------------------------

    document = Document(
        filename=original_filename,
        filepath=filepath,
        extracted_text=extracted_text,
        user_id=current_user.id
    )

    try:

        db.session.add(document)
        db.session.commit()

    except Exception as e:

        db.session.rollback()

        if os.path.exists(filepath):

            os.remove(filepath)

        return jsonify({
            "success": False,
            "message": "Failed to save document.",
            "error": str(e)
        }), 500


    # -----------------------------------------------------
    # KEYWORDS
    # -----------------------------------------------------

    try:

        keywords = extract_keywords(
            extracted_text
        )

    except Exception:

        keywords = []


    # -----------------------------------------------------
    # INFORMATION
    # -----------------------------------------------------

    try:

        information = extract_information(
            extracted_text
        )

    except Exception:

        information = {}


    # -----------------------------------------------------
    # RULE BASED SUMMARY
    # -----------------------------------------------------

    try:

        summary = summarize_text(
            extracted_text
        )

    except Exception:

        summary = ""


    # -----------------------------------------------------
    # COHERE AI ANALYSIS
    # -----------------------------------------------------

    try:

        ai_analysis = generate_ai_analysis(
            extracted_text
        )

    except Exception as e:

        ai_analysis = {
            "success": False,
            "summary": "",
            "insights": [],
            "message": str(e)
        }


    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return jsonify({

        "success": True,

        "message": (
            "Document uploaded and analyzed successfully."
        ),

        "version": "v1",

        "document": {
            "id": document.id,
            "filename": document.filename,
            "uploaded_at": (
                document.uploaded_at.isoformat()
                if document.uploaded_at
                else None
            )
        },

        "analysis": {

            "keywords": keywords,

            "information": information,

            "summary": summary,

            "ai_analysis": ai_analysis

        }

    }), 201


# =========================================================
# GET DOCUMENT ANALYSIS
# =========================================================

@api_v1.route(
    "/documents/<int:document_id>/analysis",
    methods=["GET"]
)
@login_required
def get_document_analysis_v1(document_id):

    document = Document.query.filter_by(
        id=document_id,
        user_id=current_user.id
    ).first()

    if not document:

        return jsonify({
            "success": False,
            "message": "Document not found"
        }), 404


    # -----------------------------------------------------
    # CHECK TEXT
    # -----------------------------------------------------

    text = document.extracted_text or ""

    if not text.strip():

        return jsonify({
            "success": False,
            "message": "Document has no extracted text"
        }), 400


    # -----------------------------------------------------
    # KEYWORDS
    # -----------------------------------------------------

    try:

        keywords = extract_keywords(
            text
        )

    except Exception:

        keywords = []


    # -----------------------------------------------------
    # INFORMATION
    # -----------------------------------------------------

    try:

        information = extract_information(
            text
        )

    except Exception:

        information = {}


    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    try:

        summary = summarize_text(
            text
        )

    except Exception:

        summary = ""


    # -----------------------------------------------------
    # AI ANALYSIS
    # -----------------------------------------------------

    try:

        ai_analysis = generate_ai_analysis(
            text
        )

    except Exception as e:

        ai_analysis = {
            "success": False,
            "summary": "",
            "insights": [],
            "message": str(e)
        }


    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return jsonify({

        "success": True,

        "version": "v1",

        "document": {
            "id": document.id,
            "filename": document.filename
        },

        "analysis": {

            "keywords": keywords,

            "information": information,

            "summary": summary,

            "ai_analysis": ai_analysis

        }

    })


# =========================================================
# RE-ANALYZE DOCUMENT
# =========================================================

@api_v1.route(
    "/documents/<int:document_id>/reanalyze",
    methods=["POST"]
)
@login_required
def reanalyze_document_v1(document_id):

    document = Document.query.filter_by(
        id=document_id,
        user_id=current_user.id
    ).first()

    if not document:

        return jsonify({
            "success": False,
            "message": "Document not found"
        }), 404


    # -----------------------------------------------------
    # CHECK ORIGINAL FILE
    # -----------------------------------------------------

    if not document.filepath:

        return jsonify({
            "success": False,
            "message": "Original document file not found"
        }), 404


    if not os.path.exists(
        document.filepath
    ):

        return jsonify({
            "success": False,
            "message": "Original document file not found"
        }), 404


    # -----------------------------------------------------
    # RE-EXTRACT TEXT
    # -----------------------------------------------------

    try:

        extracted_text = extract_text(
            document.filepath
        )

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Document text extraction failed.",
            "error": str(e)
        }), 500


    # -----------------------------------------------------
    # CHECK EXTRACTED TEXT
    # -----------------------------------------------------

    if not extracted_text or not extracted_text.strip():

        return jsonify({
            "success": False,
            "message": (
                "Document text extraction failed "
                "or returned empty text."
            )
        }), 400


    # -----------------------------------------------------
    # UPDATE EXISTING DOCUMENT
    # -----------------------------------------------------

    try:

        document.extracted_text = (
            extracted_text
        )

        db.session.commit()

    except Exception as e:

        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Failed to update document.",
            "error": str(e)
        }), 500


    # -----------------------------------------------------
    # KEYWORDS
    # -----------------------------------------------------

    try:

        keywords = extract_keywords(
            extracted_text
        )

    except Exception:

        keywords = []


    # -----------------------------------------------------
    # INFORMATION
    # -----------------------------------------------------

    try:

        information = extract_information(
            extracted_text
        )

    except Exception:

        information = {}


    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    try:

        summary = summarize_text(
            extracted_text
        )

    except Exception:

        summary = ""


    # -----------------------------------------------------
    # COHERE AI
    # -----------------------------------------------------

    try:

        ai_analysis = generate_ai_analysis(
            extracted_text
        )

    except Exception as e:

        ai_analysis = {
            "success": False,
            "summary": "",
            "insights": [],
            "message": str(e)
        }


    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return jsonify({

        "success": True,

        "version": "v1",

        "message": (
            "Document re-analyzed successfully."
        ),

        "document": {
            "id": document.id,
            "filename": document.filename,
            "uploaded_at": (
                document.uploaded_at.isoformat()
                if document.uploaded_at
                else None
            )
        },

        "analysis": {

            "keywords": keywords,

            "information": information,

            "summary": summary,

            "ai_analysis": ai_analysis

        }

    })


# =========================================================
# DELETE DOCUMENT
# =========================================================

@api_v1.route(
    "/documents/<int:document_id>",
    methods=["DELETE"]
)
@login_required
def delete_document_v1(document_id):

    # -----------------------------------------------------
    # FIND USER-OWNED DOCUMENT
    # -----------------------------------------------------

    document = Document.query.filter_by(
        id=document_id,
        user_id=current_user.id
    ).first()

    if not document:

        return jsonify({
            "success": False,
            "message": "Document not found"
        }), 404


    # -----------------------------------------------------
    # STORE FILEPATH BEFORE DATABASE DELETE
    # -----------------------------------------------------

    filepath = document.filepath


    # -----------------------------------------------------
    # DELETE DATABASE RECORD
    # -----------------------------------------------------

    try:

        db.session.delete(
            document
        )

        db.session.commit()

    except Exception as e:

        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Failed to delete document.",
            "error": str(e)
        }), 500


    # -----------------------------------------------------
    # DELETE PHYSICAL FILE
    # -----------------------------------------------------

    file_deleted = False

    if filepath and os.path.exists(filepath):

        try:

            os.remove(filepath)

            file_deleted = True

        except Exception as e:

            # Database record is already deleted.
            # Report the file deletion issue without
            # restoring the database record.

            return jsonify({

                "success": True,

                "version": "v1",

                "message": (
                    "Document record deleted, "
                    "but the physical file could not be removed."
                ),

                "document": {
                    "id": document_id
                },

                "file_deleted": False,

                "file_error": str(e)

            }), 200


    # -----------------------------------------------------
    # SUCCESS RESPONSE
    # -----------------------------------------------------

    return jsonify({

        "success": True,

        "version": "v1",

        "message": (
            "Document deleted successfully."
        ),

        "document": {
            "id": document_id
        },

        "file_deleted": file_deleted

    }), 200