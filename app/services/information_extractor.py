import re


# =========================================================
# TEXT NORMALIZATION
# =========================================================

def _normalize_text(text):

    if not text:
        return ""

    # Remove zero-width / invisible characters
    text = re.sub(
        r"[\u200b-\u200f\u202a-\u202e\ufeff]",
        "",
        text
    )

    # Normalize spaces
    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    return text.strip()


def _normalize_label(text):

    text = _normalize_text(text)

    text = text.replace(
        "–",
        "-"
    )

    text = text.replace(
        "—",
        "-"
    )

    # Normalize spaces around hyphen
    text = re.sub(
        r"\s*-\s*",
        " - ",
        text
    )

    return text.strip().lower()


def _clean_value(value):

    if not value:
        return ""

    value = _normalize_text(
        value
    )

    value = value.strip(
        " :-–—"
    )

    return value.strip()


# =========================================================
# FIELD DEFINITIONS
# =========================================================

FIELD_DEFINITIONS = {

    "name": [
        "பெயர்",
        "Name"
    ],

    "date_of_birth": [
        "பிறந்த தேதி",
        "பிறந்ததேதி",
        "Date of Birth",
        "DOB"
    ],

    "education": [
        "கல்வி தகுதி",
        "கல்வித்தகுதி",
        "Education",
        "Educational Qualification"
    ],

    "height_complexion": [
        "உயரம் - நிறம்",
        "உயரம்–நிறம்",
        "உயரம் -நிறம்",
        "உயரம்",
        "Height",
        "Height - Complexion"
    ],

    "occupation": [
        "வேலை",
        "தொழில்",
        "Occupation",
        "Job",
        "Profession"
    ],

    "salary": [
        "சம்பளம்",
        "Salary",
        "Income"
    ],

    "expectation": [
        "எதிர்பார்ப்பு",
        "எதிர்பார்ப்புகள்",
        "Expectation",
        "Expectations"
    ],

    "siblings": [
        "உடன்பிறப்பு",
        "உடன்பிறப்புகள்",
        "Siblings"
    ],

    "father": [
        "அப்பா",
        "தந்தை",
        "Father"
    ],

    "mother": [
        "அம்மா",
        "தாய்",
        "Mother"
    ],

    "address": [
        "முகவரி",
        "Address"
    ],

    "own_house": [
        "சொந்த வீடு",
        "சொந்தவீடு",
        "Own House"
    ],

    "rasi": [
        "ராசி",
        "Rasi"
    ],

    "star": [
        "நட்சத்திரம்",
        "Star",
        "Nakshatra"
    ],

    "lagna": [
        "லக்னம்",
        "Lagna"
    ],

    "dasa_balance": [
        "திசை இருப்பு",
        "திசைஇருப்பு",
        "Dasa Balance"
    ],

    "house_name": [
        "வீட்டுப் பெயர்",
        "வீட்டுப்பெயர்",
        "House Name"
    ]
}


# =========================================================
# MAXIMUM VALUE LINES
# =========================================================

FIELD_MAX_LINES = {

    "name": 1,

    "date_of_birth": 1,

    "education": 3,

    "height_complexion": 1,

    "occupation": 1,

    "salary": 1,

    "expectation": 2,

    "siblings": 1,

    "father": 1,

    "mother": 2,

    "address": 2,

    "own_house": 1,

    "rasi": 1,

    "star": 1,

    "lagna": 1,

    "dasa_balance": 1,

    "house_name": 1
}


# =========================================================
# BUILD LABEL MAP
# =========================================================

def _build_label_map():

    label_map = {}

    for field_name, labels in FIELD_DEFINITIONS.items():

        for label in labels:

            normalized = _normalize_label(
                label
            )

            label_map[
                normalized
            ] = field_name

    return label_map


# =========================================================
# CHECK WHETHER LINE IS A FIELD LABEL
# =========================================================

def _get_field_name(
    line,
    label_map
):

    normalized_line = _normalize_label(
        line
    )

    return label_map.get(
        normalized_line
    )


# =========================================================
# EXTRACT LABELED INFORMATION
# =========================================================

def _extract_labeled_fields(lines):

    label_map = _build_label_map()

    extracted = {}

    index = 0

    while index < len(lines):

        current_line = _normalize_text(
            lines[index]
        )

        field_name = _get_field_name(
            current_line,
            label_map
        )

        # Not a label
        if not field_name:

            index += 1

            continue

        max_lines = FIELD_MAX_LINES.get(
            field_name,
            1
        )

        values = []

        next_index = index + 1

        while (
            next_index < len(lines)
            and len(values) < max_lines
        ):

            next_line = _normalize_text(
                lines[next_index]
            )

            # Skip empty lines
            if not next_line:

                next_index += 1

                continue

            # Stop if next line is another label
            next_field = _get_field_name(
                next_line,
                label_map
            )

            if next_field:

                break

            values.append(
                next_line
            )

            next_index += 1

        # Join collected lines
        if values:

            value = " ".join(
                values
            )

            value = _clean_value(
                value
            )

            if value:

                extracted[
                    field_name
                ] = value

        index = next_index

    return extracted


# =========================================================
# CLEAN SPECIFIC FIELDS
# =========================================================

def _clean_specific_fields(
    information
):

    # -----------------------------------------------------
    # DATE OF BIRTH
    # -----------------------------------------------------

    if "date_of_birth" in information:

        value = information[
            "date_of_birth"
        ]

        match = re.search(
            r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b",
            value
        )

        if match:

            information[
                "date_of_birth"
            ] = match.group(0)

    # -----------------------------------------------------
    # SALARY
    # -----------------------------------------------------

    if "salary" in information:

        value = information[
            "salary"
        ]

        match = re.search(
            r"(?:₹|Rs\.?|INR)?\s*[\d,]+(?:\.\d+)?",
            value,
            re.IGNORECASE
        )

        if match:

            information[
                "salary"
            ] = match.group(0).strip()

    # -----------------------------------------------------
    # HEIGHT / COMPLEXION
    # -----------------------------------------------------

    if "height_complexion" in information:

        value = information[
            "height_complexion"
        ]

        information[
            "height_complexion"
        ] = value.strip()

    # -----------------------------------------------------
    # OWN HOUSE
    # -----------------------------------------------------

    if "own_house" in information:

        information[
            "own_house"
        ] = information[
            "own_house"
        ].strip()

    return information


# =========================================================
# MAIN INFORMATION EXTRACTION
# =========================================================

def extract_information(text):

    if not text:

        return {}

    normalized_text = _normalize_text(
        text
    )

    # -----------------------------------------------------
    # SPLIT INTO LINES
    # -----------------------------------------------------

    lines = []

    for line in normalized_text.splitlines():

        clean_line = _normalize_text(
            line
        )

        if clean_line:

            lines.append(
                clean_line
            )

    information = {}

    # =====================================================
    # GENERIC INFORMATION
    # =====================================================

    # -----------------------------------------------------
    # DATES
    # -----------------------------------------------------

    dates = re.findall(
        r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b",
        normalized_text
    )

    if dates:

        information[
            "dates"
        ] = list(
            dict.fromkeys(
                dates
            )
        )

    # -----------------------------------------------------
    # EMAILS
    # -----------------------------------------------------

    emails = re.findall(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        normalized_text
    )

    if emails:

        information[
            "emails"
        ] = list(
            dict.fromkeys(
                emails
            )
        )

    # -----------------------------------------------------
    # PHONE NUMBERS
    # -----------------------------------------------------

    phones = re.findall(
        r"\b(?:\+91[\s-]?)?[6-9]\d{9}\b",
        normalized_text
    )

    if phones:

        information[
            "phone_numbers"
        ] = list(
            dict.fromkeys(
                phones
            )
        )

    # -----------------------------------------------------
    # URLS
    # -----------------------------------------------------

    urls = re.findall(
        r"https?://[^\s]+",
        normalized_text
    )

    if urls:

        information[
            "urls"
        ] = list(
            dict.fromkeys(
                urls
            )
        )

    # -----------------------------------------------------
    # CURRENCY
    # -----------------------------------------------------

    currency = re.findall(
        r"(?:₹|Rs\.?|INR)\s?[\d,]+(?:\.\d+)?",
        normalized_text,
        re.IGNORECASE
    )

    if currency:

        information[
            "currency"
        ] = list(
            dict.fromkeys(
                currency
            )
        )

    # -----------------------------------------------------
    # PAN NUMBER
    # -----------------------------------------------------

    pan_numbers = re.findall(
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
        normalized_text.upper()
    )

    if pan_numbers:

        information[
            "pan_numbers"
        ] = list(
            dict.fromkeys(
                pan_numbers
            )
        )

    # =====================================================
    # LABELED INFORMATION
    # =====================================================

    labeled_information = (
        _extract_labeled_fields(
            lines
        )
    )

    information.update(
        labeled_information
    )

    # =====================================================
    # FIELD CLEANUP
    # =====================================================

    information = _clean_specific_fields(
        information
    )

    return information