import os
import re
import tempfile
import unicodedata

import fitz
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.document import Document as _Document

from app.services.ocr_service import extract_text_from_image


# ============================================================
# GENERAL TEXT CLEANUP
# ============================================================

def clean_text(text):
    """
    Clean extracted/OCR text while preserving meaningful content.

    Handles:
    - Unicode normalization
    - zero-width characters
    - emojis
    - decorative symbols
    - OCR year errors
    - duplicated experience digits
    - excessive whitespace
    """

    if text is None:
        return ""

    text = str(text)

    # --------------------------------------------------------
    # Normalize line endings
    # --------------------------------------------------------

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # --------------------------------------------------------
    # Unicode normalization
    # --------------------------------------------------------

    text = unicodedata.normalize("NFKC", text)

    # --------------------------------------------------------
    # Remove invisible / zero-width characters
    # --------------------------------------------------------

    invisible_chars = [
        "\u200b",
        "\u200c",
        "\u200d",
        "\u2060",
        "\ufeff",
        "\u00a0",
    ]

    for char in invisible_chars:
        text = text.replace(char, " ")

    # --------------------------------------------------------
    # Remove emojis and decorative Unicode symbols
    #
    # Keep normal punctuation, letters and numbers.
    # --------------------------------------------------------

    cleaned_chars = []

    for char in text:

        codepoint = ord(char)
        category = unicodedata.category(char)

        is_emoji_block = (
            0x1F300 <= codepoint <= 0x1FAFF
            or 0x2600 <= codepoint <= 0x27BF
            or 0x2300 <= codepoint <= 0x23FF
            or 0x2B00 <= codepoint <= 0x2BFF
        )

        is_symbol = category in {
            "So",
            "Sk",
        }

        if is_emoji_block or is_symbol:
            cleaned_chars.append(" ")
        else:
            cleaned_chars.append(char)

    text = "".join(cleaned_chars)

    # --------------------------------------------------------
    # OCR YEAR RANGE CORRECTION
    #
    # 20262028 -> 2026-2028
    # 20222024 -> 2022-2024
    # --------------------------------------------------------

    text = re.sub(
        r"\b(20\d{2})(20\d{2})\b",
        r"\1-\2",
        text,
    )

    # --------------------------------------------------------
    # OCR EXPERIENCE CORRECTION
    #
    # 66+ years -> 6+ years
    # 77+ years -> 7+ years
    # 88+ years -> 8+ years
    # --------------------------------------------------------

    text = re.sub(
        r"\b([0-9])\1\+\s*years?\b",
        r"\1+ years",
        text,
        flags=re.IGNORECASE,
    )

    # --------------------------------------------------------
    # Fix common OCR spelling variations
    # --------------------------------------------------------

    text = re.sub(
        r"\bAl\b",
        "AI",
        text,
    )

    # --------------------------------------------------------
    # Clean decorative characters at line beginnings
    # --------------------------------------------------------

    cleaned_lines = []

    for line in text.split("\n"):

        line = line.strip()

        if not line:
            continue

        line = re.sub(
            r"^[\s|•●○◦▪▫◆◇★☆✓✔©®™@€£$]+",
            "",
            line,
        ).strip()

        if not line:
            continue

        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    # --------------------------------------------------------
    # Reduce repeated spaces
    # --------------------------------------------------------

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    # --------------------------------------------------------
    # Reduce excessive blank lines
    # --------------------------------------------------------

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()


# ============================================================
# DOCX HELPERS
# ============================================================

def iter_block_items(parent):
    """
    Return paragraphs and tables from a DOCX document
    in their original order.
    """

    if isinstance(parent, _Document):

        parent_elm = parent.element.body

    elif isinstance(parent, Table):

        parent_elm = parent._tbl

    else:

        raise ValueError(
            "Unsupported DOCX parent type"
        )

    for child in parent_elm.iterchildren():

        if child.tag.endswith("}p"):

            yield Paragraph(
                child,
                parent,
            )

        elif child.tag.endswith("}tbl"):

            yield Table(
                child,
                parent,
            )


# ============================================================
# DOCX TABLE EXTRACTION
# ============================================================

def extract_table_text(table, table_number=None):
    """
    Extract complete DOCX table content.

    Every row and cell is preserved.
    """

    lines = []

    if table_number is not None:

        lines.append(
            f"[TABLE {table_number}]"
        )

    for row in table.rows:

        cells = []

        for cell in row.cells:

            cell_parts = []

            # ------------------------------------------------
            # Paragraphs inside cell
            # ------------------------------------------------

            for paragraph in cell.paragraphs:

                text = clean_text(
                    paragraph.text
                )

                if text:

                    cell_parts.append(
                        text
                    )

            # ------------------------------------------------
            # Nested tables
            # ------------------------------------------------

            for nested_table in cell.tables:

                nested_text = extract_table_text(
                    nested_table
                )

                if nested_text:

                    cell_parts.append(
                        nested_text
                    )

            cell_text = " ".join(
                part.replace("\n", " ")
                for part in cell_parts
                if part
            )

            cells.append(
                cell_text
            )

        row_text = " | ".join(
            cells
        ).strip()

        if row_text:

            lines.append(
                row_text
            )

    return "\n".join(lines)


# ============================================================
# DOCX EXTRACTION
# ============================================================

def extract_text_from_docx(filepath):
    """
    Extract DOCX text while preserving
    paragraph/table order.
    """

    document = Document(filepath)

    output_parts = []

    table_counter = 0

    for block in iter_block_items(document):

        # ----------------------------------------------------
        # PARAGRAPH
        # ----------------------------------------------------

        if isinstance(block, Paragraph):

            text = clean_text(
                block.text
            )

            if text:

                output_parts.append(
                    text
                )

        # ----------------------------------------------------
        # TABLE
        # ----------------------------------------------------

        elif isinstance(block, Table):

            table_counter += 1

            table_text = extract_table_text(
                block,
                table_number=table_counter,
            )

            if table_text:

                output_parts.append(
                    table_text
                )

    return clean_text(
        "\n\n".join(output_parts)
    )


# ============================================================
# PDF HELPERS
# ============================================================

def _get_page_text(page):
    """
    Extract selectable text from a PDF page.
    """

    try:

        text = page.get_text(
            "text",
            sort=True,
        )

    except Exception:

        try:

            text = page.get_text(
                "text"
            )

        except Exception:

            text = ""

    return clean_text(text)


def _calculate_text_quality(text):
    """
    Estimate quality of selectable PDF text.

    Returns a score between 0 and 1.

    Higher score:
        cleaner extraction

    Lower score:
        likely OCR/image/two-column extraction needed
    """

    if not text:

        return 0.0

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:

        return 0.0

    total_chars = len(text)

    if total_chars == 0:

        return 0.0

    # --------------------------------------------------------
    # Suspicious OCR/decorative characters
    # --------------------------------------------------------

    suspicious_chars = 0

    for char in text:

        if char in {
            "©",
            "®",
            "™",
            "€",
            "¤",
            "§",
            "¶",
            "�",
        }:

            suspicious_chars += 1

    suspicious_ratio = (
        suspicious_chars / total_chars
    )

    # --------------------------------------------------------
    # Very short / fragmented lines
    # --------------------------------------------------------

    short_lines = sum(
        1
        for line in lines
        if len(line) <= 2
    )

    short_ratio = (
        short_lines / len(lines)
        if lines
        else 0
    )

    # --------------------------------------------------------
    # Broken OCR words
    # --------------------------------------------------------

    broken_patterns = [
        r"\b[A-Za-z]{1,2}\s+[A-Za-z]{1,2}\b",
        r"\b[Zz]{2,}[»>]\b",
        r"\b[eE][@]\b",
    ]

    broken_count = 0

    for pattern in broken_patterns:

        broken_count += len(
            re.findall(
                pattern,
                text,
            )
        )

    broken_ratio = min(
        broken_count / max(len(lines), 1),
        1.0,
    )

    # --------------------------------------------------------
    # Score
    # --------------------------------------------------------

    score = 1.0

    score -= suspicious_ratio * 2.5
    score -= short_ratio * 0.8
    score -= broken_ratio * 0.8

    return max(
        0.0,
        min(1.0, score),
    )


def _is_complex_pdf_page(page, text):
    """
    Decide whether a PDF page should be rendered
    and OCR'd instead of trusting selectable text.

    Designed especially for:
    - CVs
    - two-column layouts
    - image-based pages
    - broken PDF text layers
    """

    if not text:

        return True

    quality = _calculate_text_quality(
        text
    )

    # --------------------------------------------------------
    # Very poor text quality
    # --------------------------------------------------------

    if quality < 0.72:

        return True

    # --------------------------------------------------------
    # Detect multi-column layout using text blocks
    # --------------------------------------------------------

    try:

        blocks = page.get_text(
            "blocks"
        )

        text_blocks = [
            block
            for block in blocks
            if len(block) >= 5
            and str(block[4]).strip()
        ]

        if len(text_blocks) >= 4:

            page_width = page.rect.width

            left_blocks = 0
            right_blocks = 0

            for block in text_blocks:

                x0 = float(block[0])
                x1 = float(block[2])

                center = (
                    x0 + x1
                ) / 2

                if center < page_width * 0.46:

                    left_blocks += 1

                elif center > page_width * 0.54:

                    right_blocks += 1

            if (
                left_blocks >= 2
                and right_blocks >= 2
            ):

                return True

    except Exception as e:

        print(
            "PDF COLUMN DETECTION ERROR:",
            repr(e),
        )

    return False


def _render_page_to_temp_image(page):
    """
    Render PDF page to a temporary PNG file.
    """

    matrix = fitz.Matrix(
        3.0,
        3.0,
    )

    pixmap = page.get_pixmap(
        matrix=matrix,
        alpha=False,
    )

    temp_file = tempfile.NamedTemporaryFile(
        suffix=".png",
        delete=False,
    )

    temp_image_path = temp_file.name

    temp_file.close()

    pixmap.save(
        temp_image_path
    )

    return temp_image_path


# ============================================================
# PDF EXTRACTION
# ============================================================

def extract_text_from_pdf(filepath):
    """
    Extract text from PDF page-by-page.

    Strategy:

    1. Try normal selectable text extraction.
    2. Evaluate text quality.
    3. Detect complex/two-column pages.
    4. Render poor/complex pages to images.
    5. Use the existing OCR service.
    6. Clean the final result.
    """

    output_parts = []

    pdf = None

    try:

        pdf = fitz.open(
            filepath
        )

        total_pages = pdf.page_count

        print(
            "PDF PAGES:",
            total_pages,
        )

        for page_number, page in enumerate(
            pdf,
            start=1,
        ):

            page_parts = []

            # ------------------------------------------------
            # PAGE MARKER
            # ------------------------------------------------

            page_parts.append(
                f"--- Page {page_number} ---"
            )

            # ------------------------------------------------
            # NORMAL TEXT EXTRACTION
            # ------------------------------------------------

            page_text = _get_page_text(
                page
            )

            # ------------------------------------------------
            # DETERMINE EXTRACTION QUALITY
            # ------------------------------------------------

            use_ocr = _is_complex_pdf_page(
                page,
                page_text,
            )

            print(
                f"PDF PAGE {page_number}:",
                "OCR" if use_ocr else "TEXT",
            )

            # ------------------------------------------------
            # OCR FOR COMPLEX / BROKEN PAGES
            # ------------------------------------------------

            if use_ocr:

                temp_image_path = None

                try:

                    temp_image_path = (
                        _render_page_to_temp_image(
                            page
                        )
                    )

                    ocr_text = (
                        extract_text_from_image(
                            temp_image_path
                        )
                    )

                    ocr_text = clean_text(
                        ocr_text
                    )

                    if ocr_text:

                        page_parts.append(
                            ocr_text
                        )

                    elif page_text:

                        print(
                            f"PDF PAGE {page_number}: "
                            "OCR empty, using selectable text"
                        )

                        page_parts.append(
                            page_text
                        )

                    else:

                        page_parts.append(
                            "[No text detected on this page]"
                        )

                except Exception as ocr_error:

                    print(
                        f"PDF OCR failed on page "
                        f"{page_number}: "
                        f"{ocr_error}"
                    )

                    if page_text:

                        page_parts.append(
                            page_text
                        )

                    else:

                        page_parts.append(
                            "[OCR failed - no text could be extracted]"
                        )

                finally:

                    if (
                        temp_image_path
                        and os.path.exists(
                            temp_image_path
                        )
                    ):

                        try:

                            os.remove(
                                temp_image_path
                            )

                        except Exception:

                            pass

            # ------------------------------------------------
            # NORMAL SELECTABLE TEXT
            # ------------------------------------------------

            elif page_text:

                page_parts.append(
                    page_text
                )

            # ------------------------------------------------
            # NOTHING FOUND
            # ------------------------------------------------

            else:

                page_parts.append(
                    "[No text detected on this page]"
                )

            # ------------------------------------------------
            # SAVE PAGE
            # ------------------------------------------------

            output_parts.append(
                "\n".join(page_parts)
            )

        # ----------------------------------------------------
        # FINAL CLEANUP
        # ----------------------------------------------------

        final_text = "\n\n".join(
            output_parts
        )

        return clean_text(
            final_text
        )

    finally:

        if pdf is not None:

            pdf.close()


# ============================================================
# TXT EXTRACTION
# ============================================================

def extract_text_from_txt(filepath):
    """
    Extract UTF-8 TXT content.
    """

    with open(
        filepath,
        "r",
        encoding="utf-8",
        errors="replace",
    ) as file:

        text = file.read()

    return clean_text(
        text
    )


# ============================================================
# IMAGE OCR
# ============================================================

def extract_text_from_image_file(filepath):
    """
    Extract text from JPG/JPEG/PNG using OCR.
    """

    text = extract_text_from_image(
        filepath
    )

    return clean_text(
        text
    )


# ============================================================
# MAIN EXTRACTOR
# ============================================================

def extract_text(filepath):
    """
    Detect uploaded file type and use
    the appropriate extraction method.
    """

    extension = os.path.splitext(
        filepath
    )[1].lower()

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    if extension == ".pdf":

        return extract_text_from_pdf(
            filepath
        )

    # --------------------------------------------------------
    # DOCX
    # --------------------------------------------------------

    elif extension == ".docx":

        return extract_text_from_docx(
            filepath
        )

    # --------------------------------------------------------
    # TXT
    # --------------------------------------------------------

    elif extension == ".txt":

        return extract_text_from_txt(
            filepath
        )

    # --------------------------------------------------------
    # IMAGE
    # --------------------------------------------------------

    elif extension in {
        ".jpg",
        ".jpeg",
        ".png",
    }:

        return extract_text_from_image_file(
            filepath
        )

    # --------------------------------------------------------
    # UNSUPPORTED
    # --------------------------------------------------------

    else:

        raise ValueError(
            "Unsupported file format"
        )