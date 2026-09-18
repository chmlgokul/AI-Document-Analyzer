import os
from io import BytesIO

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
    send_file
)

from sqlalchemy import or_

from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app import db
from app.models.document import Document
from app.services.text_extractor import extract_text
from app.services.keyword_extractor import extract_keywords
from app.services.information_extractor import extract_information
from app.services.summarizer import summarize_text


documents = Blueprint("documents", __name__)


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
# UPLOAD DOCUMENT
# =========================================================

@documents.route(
    "/upload",
    methods=["GET", "POST"]
)
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
                url_for(
                    "documents.upload_document"
                )
            )


        if file.filename == "":

            flash("Please select a file.")

            return redirect(
                url_for(
                    "documents.upload_document"
                )
            )


        if not allowed_file(file.filename):

            flash(
                "Only PDF, DOCX, TXT, JPG, JPEG, "
                "and PNG files are allowed."
            )

            return redirect(
                url_for(
                    "documents.upload_document"
                )
            )


        filename = secure_filename(
            file.filename
        )


        upload_folder = os.path.join(
            current_app.instance_path,
            "uploads"
        )


        os.makedirs(
            upload_folder,
            exist_ok=True
        )


        filepath = os.path.join(
            upload_folder,
            filename
        )


        file.save(filepath)


        try:

            extracted_text = extract_text(
                filepath
            )

        except Exception as e:

            extracted_text = ""

            print(
                "TEXT EXTRACTION ERROR:",
                repr(e)
            )


        document = Document(
            filename=filename,
            filepath=filepath,
            extracted_text=extracted_text,
            user_id=current_user.id
        )


        db.session.add(document)

        db.session.commit()


        flash(
            "Document uploaded successfully!"
        )


        return redirect(
            url_for(
                "documents.list_documents"
            )
        )


    return render_template(
        "upload.html"
    )


# =========================================================
# DOCUMENT HISTORY / SEARCH
# =========================================================

@documents.route("/documents")
@login_required
def list_documents():

    search_query = request.args.get(
        "q",
        ""
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
                )
            )
        )

    user_documents = query.order_by(
        Document.uploaded_at.desc()
    ).all()

    return render_template(
        "documents.html",
        documents=user_documents,
        search_query=search_query
    )


# =========================================================
# ANALYZE DOCUMENT
# =========================================================

@documents.route(
    "/analyze/<int:document_id>"
)
@login_required
def analyze_document(document_id):

    document = Document.query.filter_by(
        id=document_id,
        user_id=current_user.id
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

    return render_template(
        "analysis.html",
        document=document,
        keywords=keywords,
        information=information,
        summary=summary
    )


# =========================================================
# DELETE DOCUMENT
# =========================================================

@documents.route(
    "/delete/<int:document_id>",
    methods=["POST"]
)
@login_required
def delete_document(document_id):

    document = Document.query.filter_by(
        id=document_id,
        user_id=current_user.id
    ).first_or_404()

    if (
        document.filepath
        and os.path.exists(document.filepath)
    ):

        os.remove(
            document.filepath
        )

    db.session.delete(
        document
    )

    db.session.commit()

    flash(
        "Document deleted successfully."
    )

    return redirect(
        url_for(
            "documents.list_documents"
        )
    )


# =========================================================
# RE-ANALYZE DOCUMENT
# =========================================================

@documents.route(
    "/reanalyze/<int:document_id>",
    methods=["POST"]
)
@login_required
def reanalyze_document(document_id):

    document = Document.query.filter_by(
        id=document_id,
        user_id=current_user.id
    ).first_or_404()

    if not os.path.exists(
        document.filepath
    ):

        flash(
            "Original document file not found."
        )

        return redirect(
            url_for(
                "documents.list_documents"
            )
        )

    try:

        extracted_text = extract_text(
            document.filepath
        )

        document.extracted_text = (
            extracted_text
        )

        db.session.commit()

        flash(
            "Document re-analyzed successfully."
        )

        return redirect(
            url_for(
                "documents.analyze_document",
                document_id=document.id
            )
        )

    except Exception as e:

        print(
            "RE-ANALYZE ERROR:",
            repr(e)
        )

        flash(
            "Re-analysis failed. "
            "Please check the document."
        )

        return redirect(
            url_for(
                "documents.analyze_document",
                document_id=document.id
            )
        )


# =========================================================
# EXPORT AS TXT
# =========================================================

@documents.route(
    "/export/<int:document_id>/txt"
)
@login_required
def export_txt(document_id):

    document = Document.query.filter_by(
        id=document_id,
        user_id=current_user.id
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

    report = []

    report.append(
        "AI DOCUMENT ANALYZER"
    )

    report.append(
        "=" * 50
    )

    report.append("")

    report.append(
        f"Document: {document.filename}"
    )

    report.append(
        f"Uploaded At: {document.uploaded_at}"
    )

    report.append("")

    report.append(
        "KEYWORDS"
    )

    report.append(
        "-" * 50
    )

    for keyword in keywords:

        report.append(
            f"- {keyword}"
        )

    report.append("")

    report.append(
        "EXTRACTED INFORMATION"
    )

    report.append(
        "-" * 50
    )

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

    report.append(
        "SUMMARY"
    )

    report.append(
        "-" * 50
    )

    report.append(
        summary or
        "No summary available."
    )

    report.append("")

    report.append(
        "EXTRACTED TEXT"
    )

    report.append(
        "-" * 50
    )

    report.append(
        document.extracted_text or
        "No text could be extracted."
    )

    report_text = "\n".join(
        report
    )

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
        mimetype="text/plain"
    )


# =========================================================
# EXPORT AS PDF
# =========================================================

@documents.route(
    "/export/<int:document_id>/pdf"
)
@login_required
def export_pdf(document_id):

    document = Document.query.filter_by(
        id=document_id,
        user_id=current_user.id
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

    buffer = BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=A4
    )

    width, height = A4

    x = 50
    y = height - 50

    def write_line(
        text,
        font="Helvetica",
        size=10
    ):

        nonlocal y

        if y < 50:

            pdf.showPage()

            y = height - 50

        pdf.setFont(
            font,
            size
        )

        pdf.drawString(
            x,
            y,
            str(text)[:110]
        )

        y -= 16

    # Title

    write_line(
        "AI DOCUMENT ANALYZER",
        "Helvetica-Bold",
        16
    )

    y -= 10

    # Document details

    write_line(
        f"Document: {document.filename}",
        "Helvetica-Bold",
        11
    )

    write_line(
        f"Uploaded At: {document.uploaded_at}"
    )

    y -= 10

    # Keywords

    write_line(
        "KEYWORDS",
        "Helvetica-Bold",
        12
    )

    for keyword in keywords:

        write_line(
            f"- {keyword}"
        )

    y -= 10

    # Information

    write_line(
        "EXTRACTED INFORMATION",
        "Helvetica-Bold",
        12
    )

    if information:

        for key, value in information.items():

            write_line(
                f"{key.replace('_', ' ').title()}: {value}"
            )

    else:

        write_line(
            "No structured information found."
        )

    y -= 10

    # Summary

    write_line(
        "SUMMARY",
        "Helvetica-Bold",
        12
    )

    summary_text = (
        summary or
        "No summary available."
    )

    summary_words = (
        summary_text.split()
    )

    current_line = ""

    for word in summary_words:

        if (
            len(current_line)
            + len(word)
            > 95
        ):

            write_line(
                current_line
            )

            current_line = word

        else:

            if current_line:

                current_line += " "

            current_line += word

    if current_line:

        write_line(
            current_line
        )

    y -= 10

    # Extracted Text

    write_line(
        "EXTRACTED TEXT",
        "Helvetica-Bold",
        12
    )

    extracted_text = (
        document.extracted_text or
        "No text could be extracted."
    )

    for raw_line in (
        extracted_text.splitlines()
    ):

        line = raw_line.strip()

        if not line:
            continue

        while len(line) > 95:

            write_line(
                line[:95]
            )

            line = line[95:]

        if line:

            write_line(
                line
            )

    pdf.save()

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=(
    f"{os.path.splitext(document.filename)[0]}_analysis.pdf"
),
        mimetype="application/pdf"
    )