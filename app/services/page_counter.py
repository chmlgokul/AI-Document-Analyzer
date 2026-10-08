# ============================================================
# PAGE COUNTER SERVICE
# ============================================================
#
# PDF:
#   Exact page count using PyMuPDF.
#
# DOCX:
#   1. Microsoft Word COM on Windows (exact)
#   2. LibreOffice if available
#   3. DOCX internal metadata (Vercel/Linux friendly)
#   4. Rendered page-break fallback
#
# TXT:
#   Line-based estimate.
#
# IMAGE:
#   One image = one page.
#
# ============================================================

import os
import shutil
import subprocess
import tempfile
import zipfile
import xml.etree.ElementTree as ET

from pathlib import Path


# ============================================================
# FIND LIBREOFFICE
# ============================================================

def find_libreoffice():
    possible_commands = [
        "soffice",
        "libreoffice",
    ]

    for command in possible_commands:
        found = shutil.which(command)

        if found:
            return found

    windows_paths = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ]

    for path in windows_paths:
        if os.path.exists(path):
            return path

    linux_paths = [
        "/usr/bin/soffice",
        "/usr/bin/libreoffice",
        "/snap/bin/libreoffice",
    ]

    for path in linux_paths:
        if os.path.exists(path):
            return path

    return None


# ============================================================
# MICROSOFT WORD PAGE COUNT
# ============================================================

def count_docx_pages_with_word(filepath):
    """
    Get exact DOCX page count using Microsoft Word.

    This works on Windows when Microsoft Word and pywin32
    are available.

    Returns:
        Integer page count
        None if unavailable.
    """

    word = None
    document = None

    try:

        import pythoncom
        import win32com.client

        pythoncom.CoInitialize()

        word = win32com.client.DispatchEx(
            "Word.Application"
        )

        word.Visible = False
        word.DisplayAlerts = 0

        document = word.Documents.Open(
            os.path.abspath(filepath),
            ReadOnly=True,
            AddToRecentFiles=False,
            ConfirmConversions=False,
            Visible=False
        )

        try:
            document.Repaginate()
        except Exception:
            pass

        page_count = document.ComputeStatistics(
            2
        )

        print(
            "MICROSOFT WORD PAGE COUNT:",
            page_count
        )

        try:
            page_count = int(page_count)
        except Exception:
            return None

        if page_count <= 0:
            return None

        return page_count

    except ImportError as e:

        print(
            "PYWIN32 NOT INSTALLED:",
            repr(e)
        )

        return None

    except Exception as e:

        print(
            "MICROSOFT WORD PAGE COUNT ERROR:",
            repr(e)
        )

        return None

    finally:

        if document is not None:

            try:
                document.Close(
                    SaveChanges=False
                )
            except Exception:
                pass

        if word is not None:

            try:
                word.Quit()
            except Exception:
                pass

        try:

            import pythoncom

            pythoncom.CoUninitialize()

        except Exception:
            pass


# ============================================================
# PDF PAGE COUNT
# ============================================================

def count_pdf_pages(filepath):
    """
    Return exact PDF page count using PyMuPDF.
    """

    try:

        import fitz

        document = fitz.open(
            filepath
        )

        page_count = len(
            document
        )

        document.close()

        print(
            "PDF PAGE COUNT:",
            page_count
        )

        return page_count

    except Exception as e:

        print(
            "PDF PAGE COUNT ERROR:",
            repr(e)
        )

        return None


# ============================================================
# DOCX -> PDF USING LIBREOFFICE
# ============================================================

def convert_docx_to_pdf(filepath):
    """
    Convert DOCX to PDF using LibreOffice.

    Returns:
        Temporary PDF path if successful.
        None if conversion fails.
    """

    libreoffice = find_libreoffice()

    if not libreoffice:

        print(
            "LIBREOFFICE NOT FOUND."
        )

        return None

    source_path = Path(
        filepath
    )

    if not source_path.exists():

        print(
            "DOCX FILE NOT FOUND:",
            filepath
        )

        return None

    temp_dir = tempfile.mkdtemp(
        prefix="docx_page_count_"
    )

    try:

        command = [

            libreoffice,

            "--headless",

            "--convert-to",

            "pdf",

            "--outdir",

            temp_dir,

            str(source_path),

        ]

        print(
            "DOCX -> PDF COMMAND:",
            command
        )

        result = subprocess.run(

            command,

            stdout=subprocess.PIPE,

            stderr=subprocess.PIPE,

            text=True,

            timeout=120,

        )

        print(
            "LIBREOFFICE STDOUT:",
            result.stdout
        )

        if result.stderr:

            print(
                "LIBREOFFICE STDERR:",
                result.stderr
            )

        if result.returncode != 0:

            print(
                "LIBREOFFICE CONVERSION FAILED:",
                result.returncode
            )

            return None

        pdf_name = (
            source_path.stem
            + ".pdf"
        )

        pdf_path = (
            Path(temp_dir)
            / pdf_name
        )

        if not pdf_path.exists():

            print(
                "CONVERTED PDF NOT FOUND:",
                pdf_path
            )

            return None

        persistent_temp = tempfile.NamedTemporaryFile(
            suffix=".pdf",
            delete=False
        )

        persistent_temp.close()

        shutil.copy2(
            pdf_path,
            persistent_temp.name
        )

        return persistent_temp.name

    except subprocess.TimeoutExpired:

        print(
            "LIBREOFFICE CONVERSION TIMEOUT."
        )

        return None

    except Exception as e:

        print(
            "DOCX -> PDF ERROR:",
            repr(e)
        )

        return None

    finally:

        shutil.rmtree(
            temp_dir,
            ignore_errors=True
        )


# ============================================================
# DOCX INTERNAL PAGE COUNT
# ============================================================

def count_docx_pages_from_metadata(filepath):
    """
    Read the page count stored inside the DOCX file.

    Microsoft Word commonly stores the last saved page
    count inside:

        docProps/app.xml

    This method works on Linux/Vercel because DOCX is
    internally a ZIP/XML file.

    Returns:
        Integer page count or None.
    """

    try:

        with zipfile.ZipFile(
            filepath,
            "r"
        ) as archive:

            if (
                "docProps/app.xml"
                not in archive.namelist()
            ):

                return None

            xml_data = archive.read(
                "docProps/app.xml"
            )

        root = ET.fromstring(
            xml_data
        )

        pages = None

        for element in root.iter():

            tag = element.tag.split(
                "}"
            )[-1]

            if tag.lower() == "pages":

                pages = element.text

                break

        if not pages:

            return None

        page_count = int(
            str(pages).strip()
        )

        if page_count <= 0:

            return None

        print(
            "DOCX PAGE COUNT FROM METADATA:",
            page_count
        )

        return page_count

    except Exception as e:

        print(
            "DOCX METADATA PAGE COUNT ERROR:",
            repr(e)
        )

        return None


# ============================================================
# DOCX RENDERED PAGE BREAK FALLBACK
# ============================================================

def count_docx_pages_from_rendered_breaks(filepath):
    """
    Fallback for DOCX files without saved <Pages>
    metadata.

    Word may store rendered page breaks as:

        w:lastRenderedPageBreak

    This represents the last saved pagination and can
    provide an estimated page count on Vercel/Linux.

    Returns:
        Estimated page count or None.
    """

    try:

        with zipfile.ZipFile(
            filepath,
            "r"
        ) as archive:

            if (
                "word/document.xml"
                not in archive.namelist()
            ):

                return None

            xml_data = archive.read(
                "word/document.xml"
            )

        root = ET.fromstring(
            xml_data
        )

        rendered_breaks = 0

        explicit_breaks = 0

        for element in root.iter():

            tag = element.tag.split(
                "}"
            )[-1]

            if tag == "lastRenderedPageBreak":

                rendered_breaks += 1

            elif tag == "br":

                break_type = None

                for key, value in element.attrib.items():

                    if (
                        key.split("}")[-1]
                        == "type"
                    ):

                        break_type = value

                if break_type == "page":

                    explicit_breaks += 1

        total_breaks = max(
            rendered_breaks,
            explicit_breaks
        )

        if total_breaks <= 0:

            return None

        page_count = (
            total_breaks + 1
        )

        print(
            "DOCX PAGE COUNT FROM RENDERED BREAKS:",
            page_count
        )

        return page_count

    except Exception as e:

        print(
            "DOCX RENDERED BREAK PAGE COUNT ERROR:",
            repr(e)
        )

        return None


# ============================================================
# DOCX PAGE COUNT
# ============================================================

def count_docx_pages(filepath):
    """
    Calculate DOCX page count.

    Priority:

        1. Microsoft Word
        2. LibreOffice
        3. DOCX saved page metadata
        4. Rendered page-break fallback
    """

    # ========================================================
    # METHOD 1
    # MICROSOFT WORD
    # ========================================================

    print(
        "TRYING MICROSOFT WORD PAGE COUNT..."
    )

    word_count = (
        count_docx_pages_with_word(
            filepath
        )
    )

    if word_count is not None:

        print(
            "EXACT DOCX PAGE COUNT FROM WORD:",
            word_count
        )

        return {

            "count": word_count,

            "exact": True,

            "label": "Actual Word pages"

        }


    # ========================================================
    # METHOD 2
    # LIBREOFFICE
    # ========================================================

    print(
        "MICROSOFT WORD PAGE COUNT FAILED."
    )

    print(
        "TRYING LIBREOFFICE..."
    )

    pdf_path = None

    try:

        pdf_path = (
            convert_docx_to_pdf(
                filepath
            )
        )

        if pdf_path is not None:

            pdf_count = (
                count_pdf_pages(
                    pdf_path
                )
            )

            if pdf_count is not None:

                print(
                    "EXACT DOCX PAGE COUNT FROM LIBREOFFICE:",
                    pdf_count
                )

                return {

                    "count": pdf_count,

                    "exact": True,

                    "label":
                        "Actual Word pages"

                }

    finally:

        if pdf_path:

            try:

                os.remove(
                    pdf_path
                )

            except Exception:
                pass


    # ========================================================
    # METHOD 3
    # DOCX INTERNAL METADATA
    # ========================================================

    print(
        "TRYING DOCX INTERNAL PAGE METADATA..."
    )

    metadata_count = (
        count_docx_pages_from_metadata(
            filepath
        )
    )

    if metadata_count is not None:

        return {

            "count": metadata_count,

            "exact": True,

            "label":
                "Saved Word pages"

        }


    # ========================================================
    # METHOD 4
    # RENDERED PAGE BREAK FALLBACK
    # ========================================================

    print(
        "TRYING DOCX RENDERED PAGE BREAK FALLBACK..."
    )

    rendered_count = (
        count_docx_pages_from_rendered_breaks(
            filepath
        )
    )

    if rendered_count is not None:

        return {

            "count": rendered_count,

            "exact": False,

            "label":
                "Estimated Word pages"

        }


    # ========================================================
    # NOTHING AVAILABLE
    # ========================================================

    return {

        "count": None,

        "exact": False,

        "label":
            "Page count unavailable"

    }


# ============================================================
# TXT PAGE COUNT
# ============================================================

def count_txt_pages(filepath):
    """
    TXT files do not have physical pages.

    Therefore use a conservative line-based estimate.
    """

    try:

        with open(
            filepath,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as file:

            text = file.read()

        if not text.strip():

            return 0

        lines = text.splitlines()

        lines_per_page = 50

        page_count = max(

            1,

            (
                len(lines)
                + lines_per_page
                - 1
            )
            // lines_per_page

        )

        return page_count

    except Exception as e:

        print(
            "TXT PAGE COUNT ERROR:",
            repr(e)
        )

        return None


# ============================================================
# IMAGE PAGE COUNT
# ============================================================

def count_image_pages(filepath):
    """
    One supported image = one page.
    """

    if os.path.exists(filepath):

        return 1

    return None


# ============================================================
# MAIN PAGE COUNT FUNCTION
# ============================================================

def get_page_count(filepath):
    """
    Calculate page count according to file type.

    Returns:

        {
            "count": 40,
            "exact": True,
            "label": "Actual DOCX pages"
        }

    or:

        {
            "count": None,
            "exact": False,
            "label": "Page count unavailable"
        }
    """

    # ========================================================
    # VALIDATE FILEPATH
    # ========================================================

    if not filepath:

        return {

            "count": None,

            "exact": False,

            "label":
                "Page count unavailable"

        }


    if not os.path.exists(filepath):

        return {

            "count": None,

            "exact": False,

            "label":
                "File not found"

        }


    # ========================================================
    # FILE EXTENSION
    # ========================================================

    extension = (

        Path(filepath)

        .suffix

        .lower()

    )


    # ========================================================
    # PDF
    # ========================================================

    if extension == ".pdf":

        count = count_pdf_pages(
            filepath
        )

        return {

            "count": count,

            "exact":
                count is not None,

            "label": (

                "Actual PDF pages"

                if count is not None

                else
                "Page count unavailable"

            )

        }


    # ========================================================
    # DOCX
    # ========================================================

    if extension == ".docx":

        return count_docx_pages(
            filepath
        )


    # ========================================================
    # TXT
    # ========================================================

    if extension == ".txt":

        count = count_txt_pages(
            filepath
        )

        return {

            "count": count,

            "exact": False,

            "label":
                "Estimated text pages"

        }


    # ========================================================
    # IMAGE
    # ========================================================

    if extension in (

        ".jpg",

        ".jpeg",

        ".png"

    ):

        count = count_image_pages(
            filepath
        )

        return {

            "count": count,

            "exact":
                count is not None,

            "label": (

                "Image page"

                if count is not None

                else
                "Page count unavailable"

            )

        }


    # ========================================================
    # UNKNOWN FILE TYPE
    # ========================================================

    return {

        "count": None,

        "exact": False,

        "label":
            "Page count unavailable"

    }