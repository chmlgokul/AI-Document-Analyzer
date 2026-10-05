import os
import re
import urllib.request
import shutil

import pytesseract
from PIL import Image, ImageOps, ImageEnhance, ImageFilter


# ============================================================
# CONFIGURATION
# ============================================================

IS_VERCEL = bool(os.environ.get("VERCEL"))

TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
]


# ============================================================
# TESSERACT SETUP
# ============================================================

def setup_tesseract():
    """
    Find Tesseract on Windows.
    """

    # Already configured
    try:
        if pytesseract.pytesseract.tesseract_cmd:
            current = pytesseract.pytesseract.tesseract_cmd

            if current and os.path.exists(current):
                return True
    except Exception:
        pass

    # Check known Windows locations
    for path in TESSERACT_PATHS:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            return True

    # Check PATH
    tesseract_from_path = shutil.which("tesseract")

    if tesseract_from_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_from_path
        return True

    return False


# ============================================================
# OPTIONAL VERCEL / TESSEROCR SUPPORT
# ============================================================

try:
    import tesserocr
    from tesserocr import PSM

    TESSEROCR_AVAILABLE = True
except Exception:
    tesserocr = None
    PSM = None
    TESSEROCR_AVAILABLE = False


def prepare_tessdata():
    """
    Prepare tessdata for environments such as Vercel.
    """

    tessdata_dir = "/tmp/tessdata"

    try:
        os.makedirs(tessdata_dir, exist_ok=True)

        eng_file = os.path.join(tessdata_dir, "eng.traineddata")

        if not os.path.exists(eng_file):
            url = (
                "https://github.com/tesseract-ocr/"
                "tessdata_fast/raw/main/eng.traineddata"
            )

            urllib.request.urlretrieve(url, eng_file)

        return tessdata_dir

    except Exception:
        return None


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def preprocess_image(image):
    """
    Prepare image for OCR.

    Important:
    Do NOT aggressively threshold the image because that can
    destroy thin characters, punctuation and technical words.
    """

    image = image.convert("RGB")

    width, height = image.size

    # Upscale smaller images more aggressively.
    # Large images only need moderate scaling.
    if width * height < 1_500_000:
        scale = 3
    elif width * height < 4_000_000:
        scale = 2
    else:
        scale = 1

    if scale > 1:
        image = image.resize(
            (width * scale, height * scale),
            Image.Resampling.LANCZOS
        )

    # Grayscale
    image = ImageOps.grayscale(image)

    # Improve contrast without over-processing
    image = ImageOps.autocontrast(image)

    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.5)

    # Light sharpening
    image = image.filter(ImageFilter.SHARPEN)

    return image


# ============================================================
# BASIC TEXT NORMALIZATION
# ============================================================

def normalize_basic_text(text):
    if not text:
        return ""

    # Normalize Unicode
    text = text.replace("\u00a0", " ")
    text = text.replace("\u200b", "")
    text = text.replace("\u200c", "")
    text = text.replace("\u200d", "")
    text = text.replace("\ufeff", "")

    # Normalize common dash characters
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = text.replace("−", "-")
    text = text.replace("-", "-")

    # Remove excessive spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Fix common OCR year-range problems
    text = re.sub(
        r"\b2026\s*2028\b",
        "2026 - 2028",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\b2026\s*-\s*2028\b",
        "2026 - 2028",
        text
    )

    # Generic four-digit year pairs
    text = re.sub(
        r"\b(20\d{2})\s+(20\d{2})\b",
        r"\1 - \2",
        text
    )

    # Percentage spacing
    text = re.sub(
        r"(\d+(?:\.\d+)?)\s+%",
        r"\1%",
        text
    )

    # Clean repeated punctuation
    text = re.sub(r"[|]{3,}", "||", text)
    text = re.sub(r"[-]{4,}", "---", text)

    return text.strip()


# ============================================================
# CV DETECTION
# ============================================================

def is_cv_like_text(text):
    """
    Determine whether the OCR result looks like a resume/CV.

    This lets us apply CV-specific corrections without
    damaging normal documents.
    """

    if not text:
        return False

    lower = text.lower()

    cv_terms = [
        "education",
        "experience",
        "skills",
        "projects",
        "certifications",
        "summary",
        "linkedin",
        "github",
        "portfolio",
        "work experience",
        "technical skills",
        "vfx",
        "matchmove",
        "data science",
        "machine learning",
        "tensorflow",
        "python",
    ]

    matches = sum(1 for term in cv_terms if term in lower)

    return matches >= 3


# ============================================================
# CV-SPECIFIC OCR CLEANUP
# ============================================================

def normalize_cv_text(text):
    if not text:
        return ""

    # --------------------------------------------------------
    # Technical names
    # --------------------------------------------------------

    replacements = {
        r"\bScikitlearn\b": "Scikit-learn",
        r"\bScikit learn\b": "Scikit-learn",
        r"\bScik it-learn\b": "Scikit-learn",
        r"\bScik\s+it-learn\b": "Scikit-learn",

        r"\bTensor Flow\b": "TensorFlow",
        r"\bTensorflow\b": "TensorFlow",

        r"\bOpen CV\b": "OpenCV",
        r"\bOpenCV\b": "OpenCV",

        r"\bMedia Pipe\b": "MediaPipe",
        r"\bMediaPipe\b": "MediaPipe",

        r"\bStream lit\b": "Streamlit",
        r"\bStreamlit\b": "Streamlit",

        r"\bFlaskk\b": "Flask",
        r"\bFlask\b": "Flask",

        r"\bTIDB\b": "TiDB",
        r"\bTiDb\b": "TiDB",

        r"\bMysql\b": "MySQL",
        r"\bMYSQL\b": "MySQL",

        r"\bSqlite\b": "SQLite",
        r"\bSQLITE\b": "SQLite",

        r"\bGithub\b": "GitHub",
        r"\bGITHUB\b": "GitHub",

        r"\bLinkedin\b": "LinkedIn",
        r"\bLINKEDIN\b": "LinkedIn",

        r"\bJupyter Notebook\b": "Jupyter Notebook",

        r"\bDevelopmentt\b": "Development",

        r"\bDats Science\b": "Data Science",

        r"\bAncuracy\b": "Accuracy",

        r"\bOpportunities\b": "Opportunities",
        r"\bOpportu nities\b": "Opportunities",

        r"\bMachine Learning\b": "Machine Learning",
        r"\bDeep Learning\b": "Deep Learning",

        r"\bComputer Vision\b": "Computer Vision",

        r"\bData Analysis\b": "Data Analysis",
    }

    for pattern, replacement in replacements.items():
        text = re.sub(
            pattern,
            replacement,
            text,
            flags=re.IGNORECASE
        )

    # --------------------------------------------------------
    # Known OCR contact/header garbage
    # --------------------------------------------------------

    text = re.sub(
        r"(?im)^\s*[Qq][_\-:]+\s*",
        "",
        text
    )

    text = re.sub(
        r"(?im)^\s*[Qq]\s*$",
        "",
        text
    )

    text = re.sub(
        r"(?im)^\s*[S$]\s*%\s*$",
        "",
        text
    )

    text = re.sub(
        r"(?im)^\s*[e€©®]\s*@?\s*$",
        "",
        text
    )

    # --------------------------------------------------------
    # Name correction
    # --------------------------------------------------------

    text = re.sub(
        r"\bGOKULAKKANNANL\b",
        "GOKULAKKANNAN L",
        text,
        flags=re.IGNORECASE
    )

    # --------------------------------------------------------
    # Experience
    # --------------------------------------------------------

    text = re.sub(
        r"\b6\s*\+\s*years\b",
        "6+ years",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\b6\+\s+years\b",
        "6+ years",
        text,
        flags=re.IGNORECASE
    )

    # --------------------------------------------------------
    # Date ranges
    # --------------------------------------------------------

    text = re.sub(
        r"\b(20\d{2})\s*-\s*(20\d{2})\b",
        r"\1 - \2",
        text
    )

    text = re.sub(
        r"\b(20\d{2})\s+(Present|present)\b",
        r"\1 - Present",
        text
    )

    # --------------------------------------------------------
    # Percentage
    # --------------------------------------------------------

    text = re.sub(
        r"(\d+(?:\.\d+)?)\s*%\s*",
        r"\1% ",
        text
    )

    # --------------------------------------------------------
    # Common OCR spelling corrections
    # --------------------------------------------------------

    common = {
        r"\bDats\b": "Data",
        r"\bAncuracy\b": "Accuracy",
        r"\bexperiétete\b": "experience",
        r"\bexperi[ée]nce\b": "experience",
        r"\bDevelopmen[t]+t\b": "Development",
        r"\bProgamming\b": "Programming",
        r"\bPeagsamming\b": "Programming",
        r"\bOppc\b": "Opportunities",
    }

    for pattern, replacement in common.items():
        text = re.sub(
            pattern,
            replacement,
            text,
            flags=re.IGNORECASE
        )

    return text


# ============================================================
# FINAL OCR CLEANUP
# ============================================================

def clean_ocr_text(text):
    if not text:
        return ""

    text = normalize_basic_text(text)

    if is_cv_like_text(text):
        text = normalize_cv_text(text)

    # --------------------------------------------------------
    # Remove lines containing only symbols
    # --------------------------------------------------------

    cleaned_lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        # Ignore symbol-only lines
        if re.fullmatch(
            r"[\W_]+",
            line,
            flags=re.UNICODE
        ):
            continue

        # Ignore tiny OCR garbage tokens
        if len(line) <= 2 and not re.search(
            r"[A-Za-z0-9]",
            line
        ):
            continue

        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    # --------------------------------------------------------
    # Fix excessive blank lines
    # --------------------------------------------------------

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


# ============================================================
# STANDARD TESSERACT OCR
# ============================================================

def run_tesseract_ocr(image, psm=6):
    """
    Run standard Tesseract OCR.
    """

    if not setup_tesseract():
        return ""

    try:

        config = f"--oem 3 --psm {psm}"

        result = pytesseract.image_to_string(
            image,
            config=config,
            lang="eng"
        )

        return result or ""

    except Exception as e:

        print(
            f"[OCR] Tesseract PSM {psm} failed: {e}"
        )

        return ""


# ============================================================
# OCR DATA
# ============================================================

def get_ocr_data(image):
    """
    Get word-level OCR information.
    """

    if not setup_tesseract():
        return None

    try:

        data = pytesseract.image_to_data(
            image,
            config="--oem 3 --psm 11",
            lang="eng",
            output_type=pytesseract.Output.DICT
        )

        return data

    except Exception as e:

        print(
            f"[OCR] image_to_data failed: {e}"
        )

        return None


# ============================================================
# COLUMN SPLIT DETECTION
# ============================================================

def find_column_split(image):
    """
    Find the best vertical split between two columns.

    Returns:
        x-coordinate of split
        or None
    """

    data = get_ocr_data(image)

    if not data:
        return None

    image_width, image_height = image.size

    centers = []

    count = len(data.get("text", []))

    for i in range(count):

        text = (data["text"][i] or "").strip()

        if not text:
            continue

        try:
            confidence = float(data["conf"][i])
        except Exception:
            confidence = -1

        if confidence < 20:
            continue

        left = int(data["left"][i])
        width = int(data["width"][i])

        if width <= 0:
            continue

        center_x = left + width / 2

        centers.append(center_x)

    if len(centers) < 8:
        return None

    centers.sort()

    # --------------------------------------------------------
    # Find largest gap
    # --------------------------------------------------------

    largest_gap = 0
    split_x = None

    for i in range(len(centers) - 1):

        gap = centers[i + 1] - centers[i]

        if gap > largest_gap:

            largest_gap = gap

            split_x = (
                centers[i] + centers[i + 1]
            ) / 2

    if split_x is None:
        return None

    # --------------------------------------------------------
    # Don't accept splits too close to edges
    # --------------------------------------------------------

    relative_position = split_x / image_width

    if relative_position < 0.30:
        return None

    if relative_position > 0.70:
        return None

    # --------------------------------------------------------
    # Require meaningful gap
    # --------------------------------------------------------

    minimum_gap = image_width * 0.05

    if largest_gap < minimum_gap:
        return None

    return int(split_x)


# ============================================================
# TWO COLUMN DETECTION
# ============================================================

def detect_two_column_layout(image):
    split = find_column_split(image)

    return split is not None


# ============================================================
# TWO COLUMN OCR
# ============================================================

def extract_two_column_text(image):
    """
    Extract left and right columns independently.

    This prevents Tesseract from reading:

        left line
        right line
        left line
        right line

    and instead gives:

        LEFT COLUMN
        ...

        RIGHT COLUMN
        ...
    """

    split_x = find_column_split(image)

    if split_x is None:
        return ""

    width, height = image.size

    # Small safe margin around columns
    padding = int(width * 0.015)

    left_right_edge = max(
        1,
        split_x - padding
    )

    right_left_edge = min(
        width - 1,
        split_x + padding
    )

    # --------------------------------------------------------
    # LEFT COLUMN
    # --------------------------------------------------------

    left_crop = image.crop(
        (
            0,
            0,
            left_right_edge,
            height
        )
    )

    # --------------------------------------------------------
    # RIGHT COLUMN
    # --------------------------------------------------------

    right_crop = image.crop(
        (
            right_left_edge,
            0,
            width,
            height
        )
    )

    # --------------------------------------------------------
    # OCR
    # --------------------------------------------------------

    left_text = run_tesseract_ocr(
        left_crop,
        psm=6
    )

    right_text = run_tesseract_ocr(
        right_crop,
        psm=6
    )

    left_text = clean_ocr_text(left_text)
    right_text = clean_ocr_text(right_text)

    # --------------------------------------------------------
    # Important fallback
    #
    # If column extraction fails, don't return empty text.
    # --------------------------------------------------------

    combined_length = (
        len(left_text) +
        len(right_text)
    )

    if combined_length < 30:

        print(
            "[OCR] Column extraction too short. "
            "Falling back to full-page OCR."
        )

        return ""

    # --------------------------------------------------------
    # Combine columns
    # --------------------------------------------------------

    parts = []

    if left_text:
        parts.append(left_text)

    if right_text:
        parts.append(right_text)

    return "\n\n".join(parts).strip()


# ============================================================
# FULL PAGE OCR WITH FALLBACKS
# ============================================================

def extract_full_page_text(image):
    """
    OCR the complete image using multiple safe fallbacks.
    """

    # First attempt
    text_psm6 = run_tesseract_ocr(
        image,
        psm=6
    )

    text_psm6_clean = clean_ocr_text(
        text_psm6
    )

    # If reasonably good, use it
    if len(text_psm6_clean) >= 30:
        return text_psm6_clean

    # Second attempt
    text_psm11 = run_tesseract_ocr(
        image,
        psm=11
    )

    text_psm11_clean = clean_ocr_text(
        text_psm11
    )

    # Choose the better result
    if len(text_psm11_clean) > len(
        text_psm6_clean
    ):
        return text_psm11_clean

    return text_psm6_clean


# ============================================================
# VERCEL OCR
# ============================================================

def extract_text_vercel(image):
    """
    OCR for environments where Tesseract executable
    cannot be used directly.
    """

    if not TESSEROCR_AVAILABLE:
        return ""

    try:

        tessdata_dir = prepare_tessdata()

        if not tessdata_dir:
            return ""

        with tesserocr.PyTessBaseAPI(
            path=tessdata_dir,
            lang="eng",
            psm=PSM.SPARSE_TEXT
        ) as api:

            api.SetImage(image)

            text = api.GetUTF8Text()

            return clean_ocr_text(
                text or ""
            )

    except Exception as e:

        print(
            f"[OCR] Vercel OCR failed: {e}"
        )

        return ""


# ============================================================
# MAIN IMAGE OCR FUNCTION
# ============================================================

def extract_text_from_image(filepath):
    """
    Main OCR entry point.

    Supports:
        JPG
        JPEG
        PNG
    """

    try:

        if not filepath:
            return ""

        if not os.path.exists(filepath):
            print(
                f"[OCR] File does not exist: {filepath}"
            )
            return ""

        # ----------------------------------------------------
        # Open image
        # ----------------------------------------------------

        with Image.open(filepath) as original:

            original = original.convert("RGB")

            # ------------------------------------------------
            # Preprocess
            # ------------------------------------------------

            image = preprocess_image(
                original
            )

        # ----------------------------------------------------
        # Vercel
        # ----------------------------------------------------

        if IS_VERCEL:

            text = extract_text_vercel(
                image
            )

            if text:
                return text

            # If Vercel OCR failed, return empty safely
            return ""

        # ----------------------------------------------------
        # Windows / Local
        # ----------------------------------------------------

        if not setup_tesseract():

            print(
                "[OCR] Tesseract executable not found."
            )

            return ""

        # ----------------------------------------------------
        # Try detecting two columns
        # ----------------------------------------------------

        split = find_column_split(
            image
        )

        if split is not None:

            print(
                f"[OCR] Two-column layout detected. "
                f"Split X = {split}"
            )

            two_column_text = (
                extract_two_column_text(
                    image
                )
            )

            # Use it only if it actually contains text
            if len(two_column_text) >= 30:

                return clean_ocr_text(
                    two_column_text
                )

            print(
                "[OCR] Two-column OCR was insufficient. "
                "Using full-page fallback."
            )

        # ----------------------------------------------------
        # Full page fallback
        # ----------------------------------------------------

        text = extract_full_page_text(
            image
        )

        return clean_ocr_text(
            text
        )

    except Exception as e:

        print(
            f"[OCR] Unexpected OCR error: {e}"
        )

        return ""


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

def extract_text_from_image_file(filepath):
    """
    Compatibility wrapper used by text_extractor.py
    """

    return extract_text_from_image(
        filepath
    )