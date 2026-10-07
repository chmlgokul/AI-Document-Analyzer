# ============================================================
# PAGE COUNTER SERVICE
# ============================================================
#
# Purpose:
#   Calculate document page counts.
#
# PDF:
#   Uses PyMuPDF for exact page count.
#
# DOCX on Windows:
#   1. Microsoft Word COM -> exact Word page count
#   2. LibreOffice fallback -> exact PDF page count
#
# TXT:
#   Uses line-based estimation.
#
# IMAGE:
#   One image = one page.
#
# IMPORTANT:
#   For DOCX, Microsoft Word is preferred because the page
#   count should match the page count shown by Microsoft Word.
#
# ============================================================


import os
import shutil
import subprocess
import tempfile

from pathlib import Path


# ============================================================
# FIND LIBREOFFICE
# ============================================================

def find_libreoffice():
    """
    Find LibreOffice / soffice executable.

    Supports common Windows and Linux locations.
    """

    possible_commands = [
        "soffice",
        "libreoffice",
    ]

    # --------------------------------------------------------
    # Check PATH
    # --------------------------------------------------------

    for command in possible_commands:

        found = shutil.which(command)

        if found:
            return found

    # --------------------------------------------------------
    # Common Windows locations
    # --------------------------------------------------------

    windows_paths = [

        r"C:\Program Files\LibreOffice\program\soffice.exe",

        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",

    ]

    for path in windows_paths:

        if os.path.exists(path):
            return path

    # --------------------------------------------------------
    # Linux locations
    # --------------------------------------------------------

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
    Get the exact DOCX page count using Microsoft Word.

    This is the preferred method on Windows because it uses
    the same pagination engine that Microsoft Word uses.

    Returns:
        Integer page count
        None if Microsoft Word / pywin32 is unavailable
    """

    word = None
    document = None

    try:

        # ----------------------------------------------------
        # Microsoft Word COM
        # ----------------------------------------------------

        import pythoncom

        import win32com.client


        pythoncom.CoInitialize()


        # ----------------------------------------------------
        # Start Microsoft Word
        # ----------------------------------------------------

        word = win32com.client.DispatchEx(
            "Word.Application"
        )

        word.Visible = False

        word.DisplayAlerts = 0


        # ----------------------------------------------------
        # Open DOCX
        # ----------------------------------------------------

        document = word.Documents.Open(
            os.path.abspath(filepath),
            ReadOnly=True,
            AddToRecentFiles=False,
            ConfirmConversions=False,
            Visible=False
        )


        # ----------------------------------------------------
        # Force pagination
        # ----------------------------------------------------

        try:

            document.Repaginate()

        except Exception:

            pass


        # ----------------------------------------------------
        # Word WdStatisticPages = 2
        # ----------------------------------------------------

        page_count = document.ComputeStatistics(
            2
        )


        print(
            "MICROSOFT WORD PAGE COUNT:",
            page_count
        )


        # ----------------------------------------------------
        # Validate
        # ----------------------------------------------------

        if page_count is None:
            return None


        try:

            page_count = int(
                page_count
            )

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

        # ----------------------------------------------------
        # Close Word document
        # ----------------------------------------------------

        if document is not None:

            try:

                document.Close(
                    SaveChanges=False
                )

            except Exception:

                pass


        # ----------------------------------------------------
        # Quit Word
        # ----------------------------------------------------

        if word is not None:

            try:

                word.Quit()

            except Exception:

                pass


        # ----------------------------------------------------
        # Uninitialize COM
        # ----------------------------------------------------

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

    This is a fallback method when Microsoft Word
    is not available.

    Returns:
        PDF path if successful
        None if conversion fails
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
# DOCX PAGE COUNT
# ============================================================

def count_docx_pages(filepath):
    """
    Calculate exact DOCX page count.

    Priority:

        1. Microsoft Word
        2. LibreOffice

    Microsoft Word is preferred because its page count
    should match the page count shown by the user's
    Microsoft Word application.

    Returns:
        Integer page count
        None if exact calculation is unavailable
    """

    # ========================================================
    # METHOD 1
    # MICROSOFT WORD
    # ========================================================

    print(
        "TRYING MICROSOFT WORD PAGE COUNT..."
    )


    word_count = count_docx_pages_with_word(
        filepath
    )


    if word_count is not None:

        print(
            "EXACT DOCX PAGE COUNT FROM WORD:",
            word_count
        )

        return word_count


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

        pdf_path = convert_docx_to_pdf(
            filepath
        )


        if pdf_path is None:

            return None


        pdf_count = count_pdf_pages(
            pdf_path
        )


        if pdf_count is not None:

            print(
                "EXACT DOCX PAGE COUNT FROM LIBREOFFICE:",
                pdf_count
            )


        return pdf_count


    finally:

        # ----------------------------------------------------
        # Remove temporary PDF
        # ----------------------------------------------------

        if pdf_path:

            try:

                os.remove(
                    pdf_path
                )

            except Exception:

                pass


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


        # ----------------------------------------------------
        # Conservative estimate
        # ----------------------------------------------------

        LINES_PER_PAGE = 50


        page_count = max(

            1,

            (
                len(lines)
                + LINES_PER_PAGE
                - 1
            )
            // LINES_PER_PAGE

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
    A supported image document represents one page.
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
                "Page count unavailable",

        }


    if not os.path.exists(filepath):

        return {

            "count": None,

            "exact": False,

            "label":
                "File not found",

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

            "exact": count is not None,

            "label": (

                "Actual PDF pages"

                if count is not None

                else
                "Page count unavailable"

            ),

        }


    # ========================================================
    # DOCX
    # ========================================================

    if extension == ".docx":

        count = count_docx_pages(
            filepath
        )


        return {

            "count": count,

            "exact": count is not None,

            "label": (

                "Actual Word pages"

                if count is not None

                else
                "Install Microsoft Word"

            ),

        }


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

            "label": (

                "Estimated text pages"

            ),

        }


    # ========================================================
    # IMAGE
    # ========================================================

    if extension in (

        ".jpg",

        ".jpeg",

        ".png",

    ):

        count = count_image_pages(
            filepath
        )


        return {

            "count": count,

            "exact": count is not None,

            "label": (

                "Image page"

                if count is not None

                else
                "Page count unavailable"

            ),

        }


    # ========================================================
    # UNKNOWN FILE TYPE
    # ========================================================

    return {

        "count": None,

        "exact": False,

        "label":
            "Page count unavailable",

    }