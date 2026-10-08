import os
import re
from io import BytesIO

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
    send_file,
    jsonify,
)
from sqlalchemy import or_
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from app import db
from app.models.document import Document

from app.services.text_extractor import extract_text
from app.services.keyword_extractor import extract_keywords
from app.services.information_extractor import extract_information
from app.services.summarizer import summarize_text
from app.services.cohere_service import generate_ai_analysis
from app.services.page_counter import get_page_count


documents = Blueprint("documents", __name__)


ALLOWED_EXTENSIONS = {
    "pdf",
    "docx",
    "txt",
    "jpg",
    "jpeg",
    "png",
}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def get_stored_page_info(document):
    """
    Return page information stored in the database.

    Important for Vercel:
    after upload, the original file may no longer exist on the
    temporary filesystem. Therefore normal document listing and
    analysis must read page information from PostgreSQL/Neon,
    not recalculate it from document.filepath.
    """
    return {
        "count": document.page_count,
        "exact": bool(document.page_count_exact),
        "label": (
            document.page_count_label
            or (
                "Page count unavailable"
                if document.page_count is None
                else "Stored page count"
            )
        ),
    }


def calculate_and_store_page_info(document):
    """
    Calculate page information while the uploaded file is still
    available, then persist the result in the database.
    """
    try:
        page_info = get_page_count(document.filepath)

        document.page_count = page_info.get("count")
        document.page_count_exact = bool(
            page_info.get("exact", False)
        )
        document.page_count_label = page_info.get("label")

        return page_info

    except Exception as e:
        print("PAGE COUNT ERROR:", repr(e))

        document.page_count = None
        document.page_count_exact = False
        document.page_count_label = "Page count unavailable"

        return {
            "count": None,
            "exact": False,
            "label": "Page count unavailable",
        }


# =========================================================
# UPLOAD DOCUMENT
# =========================================================

@documents.route("/upload", methods=["GET", "POST"])
@login_required
def upload_document():

    if request.method == "POST":

        file = (
            request.files.get("document")
            or request.files.get("file")
        )

        if file is None:
            flash("No file selected.")
            return redirect(
                url_for("documents.upload_document")
            )

        if file.filename == "":
            flash("Please select a file.")
            return redirect(
                url_for("documents.upload_document")
            )

        if not allowed_file(file.filename):
            flash(
                "Only PDF, DOCX, TXT, JPG, JPEG, and PNG files are allowed."
            )
            return redirect(
                url_for("documents.upload_document")
            )

        filename = secure_filename(file.filename)

        upload_folder = os.path.join(
            current_app.instance_path,
            "uploads",
        )

        os.makedirs(upload_folder, exist_ok=True)

        filepath = os.path.join(
            upload_folder,
            filename,
        )

        file.save(filepath)

        try:
            extracted_text = extract_text(filepath)

        except Exception as e:
            extracted_text = ""

            print(
                "TEXT EXTRACTION ERROR:",
                repr(e),
            )

        document = Document(
            filename=filename,
            filepath=filepath,
            extracted_text=extracted_text,
            user_id=current_user.id,
        )

        # IMPORTANT:
        # Calculate page information while the uploaded file is
        # available and save it permanently in PostgreSQL/Neon.
        calculate_and_store_page_info(document)

        db.session.add(document)
        db.session.commit()

        flash("Document uploaded successfully!")

        return redirect(
            url_for("documents.list_documents")
        )

    return render_template("upload.html")


# =========================================================
# DOCUMENT HISTORY / SEARCH
# =========================================================

@documents.route("/documents")
@login_required
def list_documents():

    search_query = request.args.get(
        "q",
        "",
    ).strip()

    query = Document.query.filter_by(
        user_id=current_user.id
    )

    if search_query:
        query = query.filter(
            or_(
                Document.filename.ilike(
                    f"%{search_query}%"
                ),
                Document.extracted_text.ilike(
                    f"%{search_query}%"
                ),
            )
        )

    user_documents = query.order_by(
        Document.uploaded_at.desc()
    ).all()

    # Do NOT calculate page count here.
    # The uploaded file may not exist anymore on Vercel.
    # Page information is already stored in the database.

    return render_template(
        "documents.html",
        documents=user_documents,
        search_query=search_query,
    )


# =========================================================
# ANALYZE DOCUMENT
# =========================================================

@documents.route("/analyze/<int:document_id>")
@login_required
def analyze_document(document_id):

    document = Document.query.filter_by(
        id=document_id,
        user_id=current_user.id,
    ).first_or_404()

    keywords = extract_keywords(
        document.extracted_text or ""
    )

    information = extract_information(
        document.extracted_text or ""
    )

    summary = summarize_text(
        document.extracted_text or ""
    )

    ai_analysis = generate_ai_analysis(
        document.extracted_text or ""
    )

    # IMPORTANT:
    # Read stored page information instead of opening the file again.
    page_info = get_stored_page_info(document)

    return render_template(
        "analysis.html",
        document=document,
        keywords=keywords,
        information=information,
        summary=summary,
        ai_analysis=ai_analysis,
        page_info=page_info,
    )


# =========================================================
# DELETE DOCUMENT
# =========================================================

@documents.route(
    "/delete/<int:document_id>",
    methods=["POST"],
)
@login_required
def delete_document(document_id):

    document = Document.query.filter_by(
        id=document_id,
        user_id=current_user.id,
    ).first_or_404()

    if (
        document.filepath
        and os.path.exists(document.filepath)
    ):
        try:
            os.remove(document.filepath)
        except Exception as e:
            print(
                "FILE DELETE ERROR:",
                repr(e),
            )

    db.session.delete(document)
    db.session.commit()

    flash("Document deleted successfully.")

    return redirect(
        url_for("documents.list_documents")
    )


# =========================================================
# RE-ANALYZE DOCUMENT
# =========================================================

@documents.route(
    "/reanalyze/<int:document_id>",
    methods=["POST"],
)
@login_required
def reanalyze_document(document_id):

    document = Document.query.filter_by(
        id=document_id,
        user_id=current_user.id,
    ).first_or_404()

    if not os.path.exists(document.filepath):
        flash("Original document file not found.")
        return redirect(
            url_for("documents.list_documents")
        )

    try:

        extracted_text = extract_text(
            document.filepath
        )

        document.extracted_text = extracted_text

        # Recalculate and refresh stored page information
        # because the original file is available during re-analysis.
        calculate_and_store_page_info(document)

        db.session.commit()

        flash("Document re-analyzed successfully.")

        return redirect(
            url_for(
                "documents.analyze_document",
                document_id=document.id,
            )
        )

    except Exception as e:

        print(
            "RE-ANALYZE ERROR:",
            repr(e),
        )

        flash(
            "Re-analysis failed. Please check the document."
        )

        return redirect(
            url_for(
                "documents.analyze_document",
                document_id=document.id,
            )
        )


# =========================================================
# EXPORT AS TXT
# =========================================================

@documents.route("/export/<int:document_id>/txt")
@login_required
def export_txt(document_id):

    document = Document.query.filter_by(
        id=document_id,
        user_id=current_user.id,
    ).first_or_404()

    text = document.extracted_text or ""

    keywords = extract_keywords(text)
    information = extract_information(text)
    summary = summarize_text(text)
    ai_analysis = generate_ai_analysis(text)

    report = []

    report.append("AI DOCUMENT ANALYZER")
    report.append("=" * 60)
    report.append("")

    report.append(
        f"Document: {document.filename}"
    )

    report.append(
        f"Uploaded At: {document.uploaded_at}"
    )

    report.append("")

    # AI POWERED ANALYSIS
    report.append("AI-POWERED ANALYSIS")
    report.append("=" * 60)
    report.append("")

    report.append("AI SUMMARY")
    report.append("-" * 60)

    if (
        ai_analysis
        and ai_analysis.get("success")
    ):
        report.append(
            ai_analysis.get(
                "summary",
                "No AI summary available.",
            )
        )
    else:
        report.append(
            ai_analysis.get(
                "message",
                "AI analysis unavailable.",
            )
            if ai_analysis
            else "AI analysis unavailable."
        )

    report.append("")

    # KEY INSIGHTS
    report.append("KEY INSIGHTS")
    report.append("-" * 60)

    if (
        ai_analysis
        and ai_analysis.get("success")
    ):
        insights = ai_analysis.get(
            "insights",
            [],
        )

        if insights:
            for insight in insights:
                report.append(
                    f"- {insight}"
                )
        else:
            report.append(
                "No AI insights available."
            )
    else:
        report.append(
            "No AI insights available."
        )

    report.append("")

    # KEYWORDS
    report.append("KEYWORDS")
    report.append("-" * 60)

    if keywords:
        for keyword in keywords:
            report.append(
                f"- {keyword}"
            )
    else:
        report.append(
            "No keywords found."
        )

    report.append("")

    # EXTRACTED INFORMATION
    report.append("EXTRACTED INFORMATION")
    report.append("-" * 60)

    if information:
        for key, value in information.items():
            report.append(
                f"{key.replace('_', ' ').title()}: {value}"
            )
    else:
        report.append(
            "No structured information found."
        )

    report.append("")

    # RULE-BASED SUMMARY
    report.append("SUMMARY")
    report.append("-" * 60)

    report.append(
        summary or "No summary available."
    )

    report.append("")

    # EXTRACTED TEXT
    report.append("EXTRACTED TEXT")
    report.append("-" * 60)

    report.append(
        document.extracted_text
        or "No text could be extracted."
    )

    report_text = "\n".join(report)

    file_data = BytesIO(
        report_text.encode("utf-8")
    )

    file_data.seek(0)

    return send_file(
        file_data,
        as_attachment=True,
        download_name=(
            f"{document.filename}_analysis.txt"
        ),
        mimetype="text/plain",
    )


# =========================================================
# EXPORT AS PDF
# =========================================================

@documents.route("/export/<int:document_id>/pdf")
@login_required
def export_pdf(document_id):

    document = Document.query.filter_by(
        id=document_id,
        user_id=current_user.id,
    ).first_or_404()

    text = document.extracted_text or ""

    keywords = extract_keywords(text)
    information = extract_information(text)
    summary = summarize_text(text)
    ai_analysis = generate_ai_analysis(text)

    print(
        "PDF INFORMATION:",
        information,
    )

    print(
        "PDF AI SUCCESS:",
        ai_analysis.get("success")
        if ai_analysis
        else None,
    )

    fonts_folder = os.path.abspath(
        os.path.join(
            current_app.root_path,
            "..",
            "fonts",
        )
    )

    preferred_fonts = [
        "NotoSansTamil-Regular.ttf",
        "NotoSansTamil.ttf",
        "Nirmala.ttf",
        "Nirmala UI.ttf",
    ]

    font_path = None

    for preferred_name in preferred_fonts:

        candidate = os.path.join(
            fonts_folder,
            preferred_name,
        )

        if os.path.isfile(candidate):
            font_path = candidate
            break

    if (
        font_path is None
        and os.path.isdir(fonts_folder)
    ):

        for filename in os.listdir(fonts_folder):

            if filename.lower().endswith(".ttf"):

                font_path = os.path.join(
                    fonts_folder,
                    filename,
                )

                break

    if font_path is None:
        raise FileNotFoundError(
            f"No TTF font found in: {fonts_folder}"
        )

    print(
        "FONT USED:",
        font_path,
    )

    if (
        "NotoTamil"
        not in pdfmetrics.getRegisteredFontNames()
    ):

        pdfmetrics.registerFont(
            TTFont(
                "NotoTamil",
                font_path,
            )
        )

    buffer = BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=A4,
    )

    width, height = A4

    x = 50
    y = height - 50

    def new_page_if_needed(
        required_space=20
    ):
        nonlocal y

        if y < 50 + required_space:
            pdf.showPage()
            y = height - 50

    def write_line(
        value,
        font="NotoTamil",
        size=10,
    ):
        nonlocal y

        new_page_if_needed()

        pdf.setFont(
            font,
            size,
        )

        pdf.drawString(
            x,
            y,
            str(value),
        )

        y -= 16

    def write_wrapped_text(
        value,
        max_chars=95,
    ):

        if value is None:
            return

        value = str(value)

        for paragraph in value.splitlines():

            paragraph = paragraph.strip()

            if not paragraph:
                continue

            while len(paragraph) > max_chars:

                write_line(
                    paragraph[:max_chars]
                )

                paragraph = paragraph[
                    max_chars:
                ]

            if paragraph:
                write_line(paragraph)

    def write_section_title(
        title,
        size=12,
    ):
        nonlocal y

        new_page_if_needed(30)

        write_line(
            title,
            "Helvetica-Bold",
            size,
        )

        y -= 4

    write_line(
        "AI DOCUMENT ANALYZER",
        "Helvetica-Bold",
        16,
    )

    y -= 10

    write_line(
        f"Document: {document.filename}",
        "Helvetica-Bold",
        11,
    )

    write_line(
        f"Uploaded At: {document.uploaded_at}"
    )

    y -= 10

    write_section_title(
        "AI-POWERED ANALYSIS",
        13,
    )

    write_section_title(
        "AI SUMMARY",
        11,
    )

    if (
        ai_analysis
        and ai_analysis.get("success")
    ):

        ai_summary = ai_analysis.get(
            "summary",
            "No AI summary available.",
        ) or "No AI summary available."

        ai_summary = re.sub(
            r"^\s*SUMMARY\s*:\s*",
            "",
            ai_summary,
            flags=re.IGNORECASE,
        )

        ai_summary = re.sub(
            r"\s*KEY\s+INSIGHTS\s*:.*$",
            "",
            ai_summary,
            flags=(
                re.IGNORECASE
                | re.DOTALL
            ),
        )

        ai_summary = re.sub(
            r"\s*DOCUMENT\s*:.*$",
            "",
            ai_summary,
            flags=(
                re.IGNORECASE
                | re.DOTALL
            ),
        )

        write_wrapped_text(
            ai_summary
        )

    else:

        write_wrapped_text(
            ai_analysis.get(
                "message",
                "AI analysis unavailable.",
            )
            if ai_analysis
            else "AI analysis unavailable."
        )

    y -= 8

    write_section_title(
        "KEY INSIGHTS",
        11,
    )

    if (
        ai_analysis
        and ai_analysis.get("success")
        and ai_analysis.get("insights")
    ):

        for insight in ai_analysis[
            "insights"
        ]:

            clean_insight = re.sub(
                r"^\s*(SUMMARY|KEY\s+INSIGHTS|DOCUMENT)\s*:? \s*",
                "",
                str(insight),
                flags=re.IGNORECASE,
            ).strip()

            if clean_insight:
                write_wrapped_text(
                    f"- {clean_insight}"
                )

    else:

        write_line(
            "No AI insights available."
        )

    y -= 8

    write_section_title(
        "KEYWORDS",
        12,
    )

    if keywords:

        for keyword in keywords:
            write_line(
                f"- {keyword}"
            )

    else:

        write_line(
            "No keywords found."
        )

    y -= 10

    write_section_title(
        "EXTRACTED INFORMATION",
        12,
    )

    if information:

        for key, value in information.items():

            if isinstance(value, list):

                display_value = ", ".join(
                    str(item)
                    for item in value
                )

            else:

                display_value = str(value)

            write_wrapped_text(
                f"{key.replace('_', ' ').title()}: {display_value}"
            )

    else:

        write_line(
            "No structured information found."
        )

    y -= 10

    write_section_title(
        "SUMMARY",
        12,
    )

    write_wrapped_text(
        summary
        or "No summary available."
    )

    y -= 10

    write_section_title(
        "EXTRACTED TEXT",
        12,
    )

    write_wrapped_text(
        document.extracted_text
        or "No text could be extracted."
    )

    pdf.save()

    buffer.seek(0)

    response = send_file(
        buffer,
        as_attachment=True,
        download_name=(
            f"{os.path.splitext(document.filename)[0]}_analysis.pdf"
        ),
        mimetype="application/pdf",
        max_age=0,
    )

    response.headers["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, max-age=0"
    )

    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


# =========================================================
# INLINE ANALYZE DOCUMENT
# =========================================================

@documents.route(
    "/api/analyze/<int:document_id>",
    methods=["GET"],
)
@login_required
def analyze_document_api(document_id):

    document = Document.query.filter_by(
        id=document_id,
        user_id=current_user.id,
    ).first_or_404()

    try:

        text = document.extracted_text or ""

        keywords = extract_keywords(text)

        information = extract_information(text)

        summary = summarize_text(text)

        ai_analysis = generate_ai_analysis(text)

        # IMPORTANT:
        # Never depend on Vercel temporary file storage here.
        page_info = get_stored_page_info(
            document
        )

        return jsonify(
            {
                "success": True,
                "document": {
                    "id": document.id,
                    "filename": document.filename,
                },
                "page_info": page_info,
                "word_count": len(text.split()),
                "keywords": keywords,
                "information": information,
                "summary": summary,
                "ai_analysis": ai_analysis,
            }
        )

    except Exception as e:

        print(
            "INLINE ANALYSIS ERROR:",
            repr(e),
        )

        return jsonify(
            {
                "success": False,
                "message": "Document analysis failed.",
            }
        ), 500
