import os
import urllib.request

import pytesseract

from PIL import (
    Image,
    ImageEnhance,
    ImageFilter,
    ImageOps
)


# =========================================================
# VERCEL / LOCAL OCR SETUP
# =========================================================

IS_VERCEL = bool(
    os.environ.get("VERCEL")
)


# =========================================================
# VERCEL TESSERACT
# =========================================================

if IS_VERCEL:
    try:
        import tesserocr

        from tesserocr import (
            PyTessBaseAPI,
            PSM
        )

        TESSEROCR_AVAILABLE = True

    except Exception as e:
        TESSEROCR_AVAILABLE = False

        print(
            "TESSEROCR IMPORT ERROR:",
            repr(e)
        )

else:
    TESSEROCR_AVAILABLE = False


# =========================================================
# LOCAL WINDOWS TESSERACT
# =========================================================

if not IS_VERCEL:
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )


# =========================================================
# DOWNLOAD ENGLISH TESSDATA FOR VERCEL
# =========================================================

def prepare_tessdata():

    tessdata_folder = os.path.join(
        "/tmp",
        "ai_document_analyzer",
        "tessdata"
    )

    os.makedirs(
        tessdata_folder,
        exist_ok=True
    )

    languages = {
        "eng": (
            "https://raw.githubusercontent.com/"
            "tesseract-ocr/tessdata_fast/main/"
            "eng.traineddata"
        )
    }

    for language, url in languages.items():

        output_file = os.path.join(
            tessdata_folder,
            f"{language}.traineddata"
        )

        if os.path.exists(output_file):
            continue

        try:

            print(
                f"Downloading Tesseract language: {language}"
            )

            urllib.request.urlretrieve(
                url,
                output_file
            )

            print(
                f"Tesseract language ready: {language}"
            )

        except Exception as e:

            print(
                f"TESSDATA DOWNLOAD ERROR "
                f"({language}):",
                repr(e)
            )

    return tessdata_folder


# =========================================================
# IMAGE PREPROCESSING
# =========================================================

def preprocess_image(filepath):

    image = Image.open(
        filepath
    )

    image = image.convert(
        "RGB"
    )

    width, height = image.size

    # -----------------------------------------------------
    # Small images get stronger enlargement
    # -----------------------------------------------------

    try:

        file_size = os.path.getsize(
            filepath
        )

    except Exception:

        file_size = 0

    if file_size <= 100 * 1024:

        scale = 4

    else:

        scale = 2

    new_width = width * scale
    new_height = height * scale

    image = image.resize(
        (
            new_width,
            new_height
        ),
        Image.Resampling.LANCZOS
    )

    # -----------------------------------------------------
    # Grayscale
    # -----------------------------------------------------

    image = ImageOps.grayscale(
        image
    )

    # -----------------------------------------------------
    # Auto contrast
    # -----------------------------------------------------

    image = ImageOps.autocontrast(
        image
    )

    # -----------------------------------------------------
    # Increase contrast
    # -----------------------------------------------------

    image = ImageEnhance.Contrast(
        image
    ).enhance(2.0)

    # -----------------------------------------------------
    # Sharpen
    # -----------------------------------------------------

    image = image.filter(
        ImageFilter.SHARPEN
    )

    return image


# =========================================================
# OCR TEXT CLEANUP
# =========================================================

def clean_ocr_text(text):

    if not text:
        return ""

    # -----------------------------------------------------
    # Remove zero-width characters
    # -----------------------------------------------------

    text = text.replace(
        "\u200b",
        ""
    )

    text = text.replace(
        "\u200c",
        ""
    )

    text = text.replace(
        "\u200d",
        ""
    )

    text = text.replace(
        "\ufeff",
        ""
    )

    # -----------------------------------------------------
    # Remove completely useless symbol-only lines
    # -----------------------------------------------------

    cleaned_lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        if not any(
            char.isalnum()
            for char in line
        ):
            continue

        cleaned_lines.append(
            line
        )

    return "\n".join(
        cleaned_lines
    ).strip()


# =========================================================
# VERCEL OCR
# =========================================================

def extract_text_vercel(image):

    if not TESSEROCR_AVAILABLE:

        print(
            "TesserOCR is not available on Vercel."
        )

        return ""

    tessdata_folder = (
        prepare_tessdata()
    )

    # -----------------------------------------------------
    # Check English language availability
    # -----------------------------------------------------

    try:

        available_languages = (
            tesserocr.get_languages(
                tessdata_folder
            )[1]
        )

        print(
            "TESSERACT LANGUAGES:",
            available_languages
        )

    except Exception as e:

        print(
            "TESSERACT LANGUAGE CHECK ERROR:",
            repr(e)
        )

        available_languages = []

    # -----------------------------------------------------
    # Use English OCR only
    # -----------------------------------------------------

    if "eng" not in available_languages:

        print(
            "English Tesseract language data "
            "is not available."
        )

        return ""

    language = "eng"

    # -----------------------------------------------------
    # OCR
    # -----------------------------------------------------

    try:

        with PyTessBaseAPI(
            path=tessdata_folder,
            lang=language,
            psm=PSM.SPARSE_TEXT
        ) as api:

            api.SetImage(
                image
            )

            text = api.GetUTF8Text()

        return (
            text.strip()
            if text
            else ""
        )

    except Exception as e:

        print(
            "VERCEL OCR ERROR:",
            repr(e)
        )

        return ""


# =========================================================
# MAIN IMAGE OCR
# =========================================================

def extract_text_from_image(filepath):

    try:

        # -------------------------------------------------
        # Preprocess image
        # -------------------------------------------------

        image = preprocess_image(
            filepath
        )

        # -------------------------------------------------
        # Vercel production OCR
        # -------------------------------------------------

        if IS_VERCEL:

            text = extract_text_vercel(
                image
            )

            return clean_ocr_text(
                text
            )

        # -------------------------------------------------
        # Local Windows OCR
        # -------------------------------------------------

        text = pytesseract.image_to_string(
            image,
            lang="eng",
            config="--psm 11"
        )

        return clean_ocr_text(
            text
        )

    except Exception as e:

        print(
            "IMAGE OCR ERROR:",
            repr(e)
        )

        return ""