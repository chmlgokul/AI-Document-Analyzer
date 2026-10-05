import re


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def _normalize_text(text):
    """
    Normalize extracted document text while preserving
    meaningful content.
    """

    if not text:
        return ""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove zero-width / invisible characters
    text = re.sub(
        r"[\u200b-\u200f\u202a-\u202e\ufeff]",
        "",
        text
    )

    # Normalize repeated spaces
    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# TECHNICAL CONCEPTS
# ============================================================

TECHNICAL_CONCEPTS = {

    "Python": [
        "python",
        "python programming",
        "python installation"
    ],

    "Virtual Environments": [
        "venv",
        "virtual environment",
        "virtual environments",
        "virtualenv",
        "conda"
    ],

    "Package Management": [
        "pip",
        "package management",
        "package-management"
    ],

    "Requirements & Reproducibility": [
        "requirements.txt",
        "requirements file",
        "reproducibility",
        "dependencies"
    ],

    "Git & GitHub": [
        "git",
        "github",
        "version control",
        "git repository"
    ],

    "Environment Variables & Secrets": [
        "environment variables",
        "environment variable",
        ".env",
        "secrets",
        "api keys",
        "api key"
    ],

    "Jupyter & VS Code": [
        "jupyter",
        "jupyterlab",
        "jupyter notebook",
        "vs code",
        "visual studio code"
    ],

    "Cloud Fundamentals": [
        "cloud",
        "cloud fundamentals",
        "compute",
        "storage",
        "networking",
        "dns",
        "https",
        "tls",
        "object storage",
        "serverless"
    ],

    "Deployment": [
        "deployment",
        "deploy",
        "deploying",
        "production"
    ],

    "Docker": [
        "docker",
        "dockerfile",
        "container",
        "containerize",
        "containerized"
    ],

    "Testing": [
        "testing",
        "test",
        "unit testing",
        "ml testing"
    ],

    "Logging & Debugging": [
        "logging",
        "debugging",
        "troubleshooting",
        "debug",
        "traceback"
    ],

    "Data Science": [
        "data science",
        "data analysis",
        "data visualization"
    ],

    "Machine Learning": [
        "machine learning",
        "classical ml",
        "ml"
    ],

    "Deep Learning": [
        "deep learning",
        "deep-learning",
        "tensorflow",
        "keras",
        "pytorch"
    ],

    "Computer Vision": [
        "computer vision",
        "opencv",
        "pillow",
        "mediapipe",
        "cv"
    ],

    "NLP": [
        "nlp",
        "natural language processing",
        "spacy",
        "nltk"
    ],

    "Generative AI / LLM": [
        "genai",
        "generative ai",
        "llm",
        "large language model"
    ],

    "RAG & AI Agents": [
        "rag",
        "retrieval augmented generation",
        "ai agents",
        "agents"
    ],

    "Backend & APIs": [
        "backend",
        "api",
        "rest api",
        "flask",
        "fastapi"
    ],

    "Database": [
        "database",
        "dbms",
        "sql",
        "mysql",
        "postgresql",
        "sqlite",
        "mongodb"
    ],

    "Model Reproducibility": [
        "dataset reproducibility",
        "model reproducibility",
        "random seeds",
        "evaluation metrics"
    ],

    "Security": [
        "security",
        "credentials",
        "private credentials",
        "secret exposure"
    ]
}


# ============================================================
# DOCUMENT SECTION DETECTION
# ============================================================

SECTION_PATTERNS = {

    "Python Installation": [
        r"\bpython installation\b",
        r"\binstall python\b"
    ],

    "Virtual Environments": [
        r"\bvirtual environments?\b",
        r"\bvenv\b",
        r"\bconda\b"
    ],

    "Package Management": [
        r"\bpip\b",
        r"\bpackage management\b"
    ],

    "Git & GitHub": [
        r"\bgit\b",
        r"\bgithub\b",
        r"\bversion control\b"
    ],

    "Cloud Fundamentals": [
        r"\bcloud fundamentals\b",
        r"\bcloud architecture\b"
    ],

    "Deployment": [
        r"\bdeployment\b",
        r"\bdeploy\b"
    ],

    "Docker": [
        r"\bdocker\b",
        r"\bdockerfile\b"
    ],

    "Testing": [
        r"\btesting basics\b",
        r"\btesting\b"
    ],

    "Logging & Debugging": [
        r"\blogging\b",
        r"\bdebugging\b",
        r"\btroubleshooting\b"
    ],

    "Reproducibility": [
        r"\breproducibility\b",
        r"\breproducible\b"
    ],

    "AI / DS / ML Topic Audit": [
        r"\btopic audit\b",
        r"\bai/ds/ml\b",
        r"\bai/.+ml topic audit\b"
    ]
}


# ============================================================
# ENTITY EXTRACTION
# ============================================================

def _extract_emails(text):

    return list(dict.fromkeys(
        re.findall(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            text
        )
    ))


def _extract_phone_numbers(text):

    return list(dict.fromkeys(
        re.findall(
            r"\b(?:\+91[\s-]?)?[6-9]\d{9}\b",
            text
        )
    ))


def _extract_urls(text):

    return list(dict.fromkeys(
        re.findall(
            r"https?://[^\s]+",
            text
        )
    ))


def _extract_dates(text):

    return list(dict.fromkeys(
        re.findall(
            r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b",
            text
        )
    ))


# ============================================================
# IMPROVED CURRENCY EXTRACTION
# ============================================================

def _extract_currency(text):
    """
    Extract real currency values only.

    IMPORTANT:
    Do NOT treat a standalone 'rs' as currency.

    Valid examples:
        ₹500
        Rs. 500
        Rs 500
        INR 500
        ₹1,500.50

    Invalid:
        rs
        Rs
        rs,
        random technical text containing 'rs'
    """

    patterns = [

        # Indian Rupee symbol
        r"₹\s?[\d,]+(?:\.\d+)?",

        # Rs / Rs. / INR must be followed by an actual number
        r"\bRs\.?\s?[\d,]+(?:\.\d+)?",

        r"\bINR\s?[\d,]+(?:\.\d+)?"

    ]

    matches = []

    for pattern in patterns:

        found = re.findall(
            pattern,
            text,
            re.IGNORECASE
        )

        matches.extend(found)

    # Normalize whitespace
    cleaned = []

    for value in matches:

        value = re.sub(
            r"\s+",
            " ",
            value.strip()
        )

        if value not in cleaned:
            cleaned.append(value)

    return cleaned


# ============================================================
# TECHNICAL CONCEPT DETECTION
# ============================================================

def _detect_technical_concepts(text):
    """
    Detect meaningful technical concepts from the document.

    Instead of returning random repeated words, this returns
    recognized topics and technologies.
    """

    normalized = text.lower()

    detected = []

    for concept, patterns in TECHNICAL_CONCEPTS.items():

        found = False

        for pattern in patterns:

            if re.search(
                re.escape(pattern.lower()),
                normalized
            ):
                found = True
                break

        if found:
            detected.append(concept)

    return detected


# ============================================================
# SECTION DETECTION
# ============================================================

def _detect_sections(text):
    """
    Detect important sections/topics present in the document.
    """

    normalized = text.lower()

    sections = []

    for section_name, patterns in SECTION_PATTERNS.items():

        for pattern in patterns:

            if re.search(
                pattern,
                normalized,
                re.IGNORECASE
            ):

                sections.append(section_name)
                break

    return sections


# ============================================================
# IMPORTANT COMMANDS
# ============================================================

def _extract_commands(text):
    """
    Detect useful technical commands from code blocks/text.
    """

    command_patterns = [

        r"python\s+-m\s+pip\s+[^\n]+",

        r"python\s+-m\s+venv\s+[^\n]+",

        r"python\s+--version",

        r"python3\s+--version",

        r"pip\s+--version",

        r"pip\s+install\s+[^\n]+",

        r"git\s+(?:init|status|add|commit|push|pull|branch|switch)[^\n]*",

        r"jupyter\s+lab",

        r"conda\s+(?:create|activate|deactivate)[^\n]*"
    ]

    commands = []

    for pattern in command_patterns:

        matches = re.findall(
            pattern,
            text,
            re.IGNORECASE
        )

        for match in matches:

            cleaned = match.strip()

            if cleaned and cleaned not in commands:
                commands.append(cleaned)

    return commands[:15]


# ============================================================
# TABLE / PAGE INFORMATION
# ============================================================

def _extract_page_count(text):
    """
    Detect page markers added by the PDF extractor.
    """

    pages = re.findall(
        r"---\s*Page\s+(\d+)\s*---",
        text,
        re.IGNORECASE
    )

    if not pages:
        return None

    return len(set(pages))


def _extract_table_count(text):
    """
    Detect extracted DOCX tables.
    """

    tables = re.findall(
        r"\[TABLE\s+(\d+)\]",
        text,
        re.IGNORECASE
    )

    if not tables:
        return None

    return len(set(tables))


# ============================================================
# MAIN INFORMATION EXTRACTION
# ============================================================

def extract_information(text):

    if not text:
        return {}

    normalized_text = _normalize_text(text)

    information = {}

    # ========================================================
    # TECHNICAL TOPICS
    # ========================================================

    technical_topics = _detect_technical_concepts(
        normalized_text
    )

    if technical_topics:
        information["technical_topics"] = technical_topics

    # ========================================================
    # DOCUMENT SECTIONS
    # ========================================================

    sections = _detect_sections(
        normalized_text
    )

    if sections:
        information["major_sections"] = sections

    # ========================================================
    # IMPORTANT COMMANDS
    # ========================================================

    commands = _extract_commands(
        normalized_text
    )

    if commands:
        information["important_commands"] = commands

    # ========================================================
    # PAGE COUNT
    # ========================================================

    page_count = _extract_page_count(
        normalized_text
    )

    if page_count:
        information["pages_processed"] = page_count

    # ========================================================
    # TABLE COUNT
    # ========================================================

    table_count = _extract_table_count(
        normalized_text
    )

    if table_count:
        information["tables_detected"] = table_count

    # ========================================================
    # EMAILS
    # ========================================================

    emails = _extract_emails(
        normalized_text
    )

    # Ignore obvious placeholder/example emails
    real_emails = [
        email
        for email in emails
        if email.lower()
        not in {
            "you@example.com",
            "example@example.com"
        }
    ]

    if real_emails:
        information["emails"] = real_emails

    # ========================================================
    # PHONE NUMBERS
    # ========================================================

    phones = _extract_phone_numbers(
        normalized_text
    )

    if phones:
        information["phone_numbers"] = phones

    # ========================================================
    # URLS
    # ========================================================

    urls = _extract_urls(
        normalized_text
    )

    if urls:
        information["urls"] = urls

    # ========================================================
    # DATES
    # ========================================================

    dates = _extract_dates(
        normalized_text
    )

    if dates:
        information["dates"] = dates

    # ========================================================
    # CURRENCY
    # ========================================================

    currency = _extract_currency(
        normalized_text
    )

    if currency:
        information["currency"] = currency

    # ========================================================
    # EMPTY RESULT FALLBACK
    # ========================================================

    if not information:

        information[
            "message"
        ] = "No significant structured information detected."

    return information