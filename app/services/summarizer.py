import re
from collections import Counter


# ============================================================
# STOP WORDS
# ============================================================

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then", "than",
    "this", "that", "these", "those", "with", "without", "from",
    "for", "into", "onto", "about", "over", "under", "between",
    "through", "during", "before", "after", "while", "where",
    "when", "which", "who", "whom", "whose", "what", "why", "how",
    "is", "are", "was", "were", "be", "been", "being",
    "has", "have", "had", "do", "does", "did",
    "can", "could", "should", "would", "may", "might", "must",
    "will", "shall", "to", "of", "in", "on", "at", "by", "as",
    "it", "its", "their", "there", "they", "them", "you", "your",
    "we", "our", "i", "me", "my", "he", "she", "his", "her",
    "also", "very", "more", "most", "some", "any", "all",
    "each", "every", "both", "only", "just", "such",
    "not", "no", "yes", "using", "used", "use", "uses",
    "one", "two", "three", "first", "second", "third",
    "etc", "example", "examples"
}


# ============================================================
# TECHNICAL TOPICS
# ============================================================

TECHNICAL_TOPICS = [
    "Python", "Virtual Environments", "Package Management", "pip",
    "requirements.txt", "Git", "GitHub", "Environment Variables",
    "Secrets", "Jupyter", "VS Code", "Cloud Fundamentals",
    "Deployment", "Docker", "Testing", "Logging", "Debugging",
    "Reproducibility", "Data Science", "Machine Learning",
    "Deep Learning", "Computer Vision", "NLP", "Generative AI",
    "LLM", "RAG", "AI Agents", "Backend", "APIs", "Database",
    "Security"
]


# ============================================================
# CV / RESUME DETECTION
# ============================================================

CV_TERMS = [
    "resume", "curriculum vitae", "education", "work experience",
    "experience", "professional experience", "skills",
    "technical skills", "projects", "certifications",
    "achievements", "additional information", "availability",
    "linkedin", "github", "portfolio", "vfx", "matchmove",
    "rotomation", "animation", "internship", "full-time",
    "fulltime", "candidate"
]


def is_cv_document(text):
    """Detect whether extracted text looks like a CV / resume."""
    if not text:
        return False

    lower = text.lower()
    matches = sum(1 for term in CV_TERMS if term in lower)

    strong_indicators = [
        "work experience", "education", "certifications",
        "technical skills", "linkedin", "github", "portfolio"
    ]
    strong_matches = sum(1 for term in strong_indicators if term in lower)

    if strong_matches >= 2:
        return True

    return matches >= 6


# ============================================================
# STRUCTURAL / TABLE NOISE
# ============================================================

STRUCTURAL_PATTERNS = [
    r"\[TABLE\s*\d+\]",
    r"\btable\s*\d+\b",
    r"\btopic\s*\|\s*status\s*\|\s*role\b",
    r"\barea\s*\|\s*typical tools\b",
    r"\bconcept\s*\|\s*simple meaning\b",
    r"\blayer\s*\|\s*coverage\b",
    r"\bproblem\s*\|\s*first checks\b",
    r"\btypical tools\b",
    r"\bsimple meaning\b",
    r"\bfirst checks\b",
    r"\bstatus\s*\|\s*role\b",
]


def contains_structural_noise(text):
    if not text:
        return False

    lower = text.lower()
    return any(re.search(pattern, lower, re.IGNORECASE)
               for pattern in STRUCTURAL_PATTERNS)


# ============================================================
# COMMAND / CODE DETECTION
# ============================================================

COMMAND_PATTERNS = [
    r"^\$",
    r"^python\s",
    r"^python3\s",
    r"^pip\s",
    r"^git\s",
    r"^docker\s",
    r"^cd\s",
    r"^mkdir\s",
    r"^rm\s",
    r"^copy\s",
    r"^set\s",
    r"^export\s",
    r"^conda\s",
    r"^npm\s",
    r"^uv\s",
    r"^source\s",
    r"^jupyter\s",
]


def is_command_line(text):
    text = text.strip().lower()
    return any(re.match(pattern, text) for pattern in COMMAND_PATTERNS)


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):
    if not text:
        return ""

    text = text.replace("\x00", " ")
    text = text.replace("\u00a0", " ")
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Normalize year ranges without changing document content.
    text = re.sub(
        r"\b(20\d{2})\s*[-–—]\s*(20\d{2})\b",
        r"\1-\2",
        text
    )

    text = re.sub(
        r"\bfull\s*time\b",
        "full-time",
        text,
        flags=re.IGNORECASE
    )

    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        line = re.sub(r"[ \t]+", " ", line)
        lines.append(line)

    return "\n".join(lines).strip()


# ============================================================
# REMOVE PDF PAGE MARKERS
# ============================================================

def remove_page_markers(text):
    if not text:
        return ""

    return re.sub(
        r"---\s*Page\s+\d+\s*---",
        " ",
        text,
        flags=re.IGNORECASE
    )


# ============================================================
# REMOVE TABLE BLOCKS
# ============================================================

def remove_table_artifacts(text):
    if not text:
        return ""

    text = re.sub(
        r"\[TABLE\s*\d+\]",
        " ",
        text,
        flags=re.IGNORECASE
    )

    table_headers = [
        r"Topic\s*\|\s*Status\s*\|\s*Role",
        r"Area\s*\|\s*Typical tools",
        r"Concept\s*\|\s*Simple meaning",
        r"Layer\s*\|\s*Coverage",
        r"Problem\s*\|\s*First checks",
    ]

    for pattern in table_headers:
        text = re.sub(
            pattern,
            " ",
            text,
            flags=re.IGNORECASE
        )

    return text


# ============================================================
# REMOVE DOCUMENT TITLE ARTIFACTS
# ============================================================

def remove_title_artifacts(text):
    if not text:
        return ""

    title_patterns = [
        r"AI\s*/\s*Data Science\s*/\s*ML\s*[-—]\s*Practical Setup\s*&\s*Missing Topics Master Book",
        r"Python Installation\s+Environments\s+Git\s+Cloud\s+Reproducibility\s+Production Basics",
    ]

    for pattern in title_patterns:
        text = re.sub(
            pattern,
            " ",
            text,
            flags=re.IGNORECASE
        )

    return text


# ============================================================
# NOISE DETECTION
# ============================================================

def is_noise(line):
    line = line.strip()

    if not line:
        return True

    if len(line) < 35:
        return True

    if is_command_line(line):
        return True

    if contains_structural_noise(line):
        return True

    lower = line.lower()

    noise_patterns = [
        "one-page memory map",
        "memory map",
        "practice checklist",
        "quick reference",
        "table of contents",
        "contents",
        "page ",
        "chapter ",
        "section ",
        "final gap audit",
        "core ai/ds package stack",
        "final ai/ds/ml topic audit",
        "python installation environments",
        "production basics",
    ]

    if any(lower.startswith(pattern) for pattern in noise_patterns):
        return True

    if line.count("|") >= 1:
        return True

    if line.count(":") >= 4:
        return True

    if "{" in line or "}" in line or "=>" in line or "->" in line:
        return True

    alpha_chars = sum(character.isalpha() for character in line)
    if alpha_chars < 25:
        return True

    return False


# ============================================================
# SENTENCE SPLITTER
# ============================================================

def split_sentences(text):
    text = clean_text(text)

    if not text:
        return []

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text.replace("\n", " ")
    )

    return [
        sentence.strip()
        for sentence in sentences
        if len(sentence.strip()) >= 40
    ]


# ============================================================
# TECHNICAL TOPIC DETECTION
# ============================================================

def detect_topics(text):
    lower = text.lower()
    return [
        topic
        for topic in TECHNICAL_TOPICS
        if topic.lower() in lower
    ]


# ============================================================
# SENTENCE QUALITY CHECK
# ============================================================

def is_good_summary_sentence(sentence):
    lower = sentence.lower()

    if contains_structural_noise(sentence):
        return False

    title_indicators = [
        "master book",
        "practical setup & missing topics",
        "production basics purpose",
        "python installation environments git cloud",
    ]

    if any(indicator in lower for indicator in title_indicators):
        return False

    if "|" in sentence:
        return False

    if sentence.count(":") >= 3:
        return False

    words = sentence.split()

    if len(words) <= 18:
        verbs = [
            "is", "are", "was", "were", "provides", "explains",
            "records", "helps", "allows", "requires", "prevents",
            "recommends", "covers", "focuses", "means", "supports",
            "isolates", "connects"
        ]
        has_verb = any(
            re.search(rf"\b{re.escape(verb)}\b", lower)
            for verb in verbs
        )
        if not has_verb:
            return False

    alpha_words = re.findall(r"\b[A-Za-z]+\b", sentence)
    if alpha_words:
        uppercase_words = sum(
            1 for word in alpha_words
            if word.isupper() and len(word) > 2
        )
        if uppercase_words >= 4:
            return False

    return True


# ============================================================
# SENTENCE SCORING
# ============================================================

def score_sentence(sentence, word_frequency):
    lower = sentence.lower()

    words = re.findall(
        r"\b[a-zA-Z][a-zA-Z0-9_.+-]*\b",
        lower
    )

    score = 0

    for word in words:
        if word in STOP_WORDS:
            continue
        score += word_frequency.get(word, 0)

    for topic in TECHNICAL_TOPICS:
        if topic.lower() in lower:
            score += 8

    important_words = [
        "purpose", "important", "recommended", "production",
        "deployment", "reproducibility", "security", "workflow",
        "architecture", "testing", "debugging", "environment",
        "installation", "project", "development", "version",
        "package", "documentation", "practical", "isolate",
        "dependencies", "repository", "secrets"
    ]

    for word in important_words:
        if word in lower:
            score += 4

    if 60 <= len(sentence) <= 300:
        score += 5

    if len(sentence) > 450:
        score -= 15

    if sentence.count(":") >= 2:
        score -= 8

    if "|" in sentence:
        score -= 20

    if "[" in sentence or "]" in sentence:
        score -= 15

    return score


# ============================================================
# DOCUMENT PURPOSE
# ============================================================

def detect_document_purpose(text):
    lower = text.lower()

    if (
        "python" in lower
        and "environment" in lower
        and "deployment" in lower
        and "machine learning" in lower
    ):
        return (
            "The document provides a practical setup and gap-audit "
            "guide for Python, Data Science, Machine Learning and "
            "related AI development workflows, with emphasis on "
            "reproducibility and production readiness."
        )

    if "machine learning" in lower and "data science" in lower:
        return (
            "The document provides practical guidance on Data Science "
            "and Machine Learning development workflows."
        )

    if "python" in lower:
        return (
            "The document provides practical guidance for Python "
            "development and project setup."
        )

    return (
        "The document presents practical technical guidance organized "
        "around development concepts and workflows."
    )


# ============================================================
# CV SECTION HELPERS
# ============================================================

CV_SECTION_HEADINGS = {
    "summary": {
        "summary", "profile", "professional summary", "career objective",
        "objective", "about me"
    },
    "education": {
        "education", "academic background", "educational background"
    },
    "experience": {
        "work experience", "professional experience", "experience",
        "employment history", "work history"
    },
    "projects": {
        "projects", "personal projects", "academic projects",
        "key projects", "project experience"
    },
    "skills": {
        "skills", "technical skills", "core skills", "skills & technologies",
        "technical skills & tools"
    },
    "certifications": {
        "certifications", "certificates", "licenses & certifications"
    },
    "achievements": {
        "achievements", "awards", "accomplishments"
    },
    "additional": {
        "additional information", "additional info", "availability",
        "personal details"
    },
}


def normalize_heading(line):
    value = re.sub(r"[^a-zA-Z& ]", "", line.lower())
    value = re.sub(r"\s+", " ", value).strip()
    return value


def detect_section_heading(line):
    normalized = normalize_heading(line)

    for section, headings in CV_SECTION_HEADINGS.items():
        if normalized in headings:
            return section

    return None


def get_cv_sections(text):
    """
    Split a CV into named sections while preserving the extracted text.
    This is downstream parsing only; it does not modify OCR output.
    """
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    sections = {}
    current = "header"
    sections[current] = []

    for line in lines:
        section = detect_section_heading(line)

        if section:
            current = section
            sections.setdefault(current, [])
            continue

        sections.setdefault(current, []).append(line)

    return sections


# ============================================================
# CV INFORMATION EXTRACTION
# ============================================================

def find_cv_line(lines, keywords):
    for line in lines:
        lower = line.lower()
        if any(keyword in lower for keyword in keywords):
            return line.strip()
    return ""


def extract_cv_name(text):
    """Try to identify a person's name from the beginning of a CV."""
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    for line in lines[:10]:
        if (
            2 <= len(line.split()) <= 5
            and re.fullmatch(r"[A-Z][A-Z\s.]+", line)
        ):
            if line.lower() not in {
                "data science",
                "machine learning",
                "artificial intelligence",
                "summary",
                "education",
                "skills",
            }:
                return line.title()

    return ""


def extract_cv_experience(text):
    patterns = [
        r"\b\d+\+?\s+years?\s+of\s+(?:professional\s+)?(?:vfx|animation|experience)",
        r"\b\d+\+?\s+years?\s+of\s+experience",
        r"\b\d+\+?\s+years?\s+vfx",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(0).strip()

    return ""


def extract_cv_accuracy(text):
    patterns = [
        r"\b\d+(?:\.\d+)?%\s*(?:test\s+)?accuracy",
        r"accuracy\s*[:\-]?\s*\d+(?:\.\d+)?%",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            value = re.sub(r"\s+", " ", match.group(0))
            return value.strip()

    return ""


# ============================================================
# CV EDUCATION — SECTION-AWARE
# ============================================================

def extract_cv_education(text):
    """
    Extract only education entries from the EDUCATION section.

    Expected examples:
        2026 - 2028 | M.Sc. Computer Science
        2022 - 2024 | Diploma in Data Science and AI
        2019 - 2022 | B.A. VFX and Animation
        2013 - 2016 | B.Sc. Computer Science

    This intentionally avoids generic keyword matching across the whole
    CV because words such as 'data science' and 'computer science' can
    also occur in skills/projects.
    """
    sections = get_cv_sections(text)
    lines = sections.get("education", [])

    degree_pattern = re.compile(
        r"\b("
        r"M\.?\s*Sc\.?|"
        r"M\.?\s*S\.?|"
        r"MCA|"
        r"B\.?\s*Sc\.?|"
        r"B\.?\s*A\.?|"
        r"B\.?\s*Tech\.?|"
        r"B\.?\s*E\.?|"
        r"BCA|"
        r"Diploma|"
        r"Ph\.?\s*D\.?"
        r")\b",
        re.IGNORECASE
    )

    year_range_pattern = re.compile(
        r"\b20\d{2}\s*[-–—]\s*(?:20\d{2}|Present)\b",
        re.IGNORECASE
    )

    result = []

    for line in lines:
        cleaned = re.sub(r"\s+", " ", line).strip()

        # The strongest signal is a year range + degree.
        if year_range_pattern.search(cleaned) and degree_pattern.search(cleaned):
            if cleaned not in result:
                result.append(cleaned)
            continue

        # Fallback for education lines without dates.
        if degree_pattern.search(cleaned):
            lower = cleaned.lower()

            # Avoid lines that are clearly skills/subject lists.
            if "|" in cleaned and not year_range_pattern.search(cleaned):
                parts = [part.strip() for part in cleaned.split("|")]
                if len(parts) > 2:
                    continue

            if len(cleaned.split()) >= 2 and "classification" not in lower:
                if cleaned not in result:
                    result.append(cleaned)

    return result[:6]


# ============================================================
# CV PROJECTS — SECTION-AWARE
# ============================================================

def _looks_like_project_title(line):
    """
    Decide whether a line inside PROJECTS is a project title rather than
    a technology/detail line.
    """
    cleaned = re.sub(r"\s+", " ", line).strip()
    lower = cleaned.lower()

    if not cleaned or len(cleaned) > 140:
        return False

    # Detail / technology / metric lines should never become project names.
    detail_prefixes = (
        "selenium,",
        "streamlit,",
        "pandas,",
        "sql,",
        "plotly,",
        "tensorflow,",
        "keras,",
        "opencv,",
        "mediapipe,",
        "python,",
        "test accuracy",
        "accuracy:",
        "in progress",
        "technologies:",
        "technology:",
        "tools:",
        "stack:",
        "built with",
        "developed using",
        "used:",
    )

    if lower.startswith(detail_prefixes):
        return False

    # Pipe-separated skill/detail rows are not project titles.
    if "|" in cleaned:
        return False

    # A one-word line such as "Rotomation." is not a project title.
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9&'().-]*", cleaned)
    if len(words) < 2:
        return False

    # Pure technology/skill lines should not become project names.
    technology_only = {
        "python", "tensorflow", "keras", "opencv", "mediapipe",
        "streamlit", "pandas", "numpy", "sql", "plotly",
        "machine learning", "deep learning", "computer vision",
        "data science", "artificial intelligence", "rotomation",
        "matchmove", "animation"
    }

    if lower.rstrip(".") in technology_only:
        return False

    project_keywords = [
        "classification",
        "data scraping",
        "visualizations",
        "pipeline",
        "analyzer",
        "recommendation",
        "forecast",
        "drowsiness",
        "dashboard",
        "prediction",
        "detection",
        "recognition",
        "application",
        "app",
    ]

    return any(keyword in lower for keyword in project_keywords)


def extract_cv_projects(text):
    """
    Extract project title lines only from the PROJECTS section.

    For the current CV this should identify:
      - IMDB Data Scraping & Visualizations
      - Brain Tumor Classification (CNN)
      - Fish Image Classification (11 Classes)
      - AIRA - AI Rotomation & Animation Pipeline
    """
    sections = get_cv_sections(text)
    lines = sections.get("projects", [])

    project_names = []

    for line in lines:
        cleaned = re.sub(r"\s+", " ", line).strip()

        if _looks_like_project_title(cleaned):
            if cleaned not in project_names:
                project_names.append(cleaned)

    return project_names[:8]


# ============================================================
# CV SKILLS
# ============================================================

def extract_cv_skills(text):
    lower = text.lower()

    skill_map = [
        ("Python", "python"),
        ("C++", "c++"),
        ("SQL", "sql"),
        ("Pandas", "pandas"),
        ("NumPy", "numpy"),
        ("Matplotlib", "matplotlib"),
        ("Scikit-learn", "scikit-learn"),
        ("TensorFlow", "tensorflow"),
        ("Keras", "keras"),
        ("OpenCV", "opencv"),
        ("MediaPipe", "mediapipe"),
        ("Flask", "flask"),
        ("Streamlit", "streamlit"),
        ("MySQL", "mysql"),
        ("TiDB", "tidb"),
        ("SQLite", "sqlite"),
        ("Firebase", "firebase"),
        ("Git", "git"),
        ("GitHub", "github"),
        ("Jupyter", "jupyter"),
        ("CNN", "cnn"),
        ("RNN", "rnn"),
        ("LSTM", "lstm"),
    ]

    found = []

    for display_name, search_name in skill_map:
        if search_name in lower:
            found.append(display_name)

    return found


# ============================================================
# CV SUMMARY
# ============================================================

def summarize_cv(text):
    if not text:
        return "No meaningful text was available for summarization."

    experience = extract_cv_experience(text)
    accuracy = extract_cv_accuracy(text)
    education = extract_cv_education(text)
    projects = extract_cv_projects(text)
    skills = extract_cv_skills(text)

    output = []

    # PURPOSE
    purpose_parts = []

    if experience:
        purpose_parts.append(f"The candidate has {experience}")
    else:
        purpose_parts.append(
            "The candidate has a background in Data Science, AI "
            "and related technical fields"
        )

    if skills:
        purpose_parts.append(
            "with skills including " + ", ".join(skills[:8])
        )

    purpose = " ".join(purpose_parts).strip()
    if not purpose.endswith("."):
        purpose += "."

    output.append("PURPOSE\n" + purpose)

    # EDUCATION
    if education:
        education_text = [
            f"• {item}"
            for item in education
            if len(item) <= 150
        ]

        if education_text:
            output.append(
                "EDUCATION\n" + "\n".join(education_text[:6])
            )

    # PROJECTS
    if projects:
        project_text = [f"• {project}" for project in projects]

        output.append(
            "PROJECTS\n" + "\n".join(project_text[:8])
        )

    # SKILLS
    if skills:
        output.append(
            "SKILLS\n" + ", ".join(skills) + "."
        )

    # ACHIEVEMENTS
    achievement_lines = []

    if accuracy:
        achievement_lines.append(
            f"• {accuracy.capitalize()}."
        )

    if experience:
        achievement_lines.append(
            f"• {experience.capitalize()}."
        )

    if achievement_lines:
        output.append(
            "KEY ACHIEVEMENTS\n" + "\n".join(achievement_lines)
        )

    # FINAL OVERVIEW
    overview_parts = []

    if experience:
        overview_parts.append(experience)

    if projects:
        overview_parts.append(f"{len(projects)} notable project(s)")

    if accuracy:
        overview_parts.append(accuracy)

    if overview_parts:
        overview = (
            "Overall, the CV highlights "
            + ", ".join(overview_parts)
            + "."
        )
        output.append("OVERVIEW\n" + overview)

    return "\n\n".join(output)


# ============================================================
# PREPARE SUMMARY TEXT
# ============================================================

def prepare_summary_text(text):
    text = remove_page_markers(text)
    text = remove_table_artifacts(text)
    text = remove_title_artifacts(text)
    return clean_text(text)


# ============================================================
# SELECT MEANINGFUL SENTENCES
# ============================================================

def select_meaningful_sentences(text, max_sentences=5):
    prepared_text = prepare_summary_text(text)
    sentences = split_sentences(prepared_text)

    valid = []

    for sentence in sentences:
        if is_noise(sentence):
            continue

        if not is_good_summary_sentence(sentence):
            continue

        if len(sentence.split()) < 8:
            continue

        normalized = sentence.lower().strip()

        if any(
            normalized == existing.lower().strip()
            for existing in valid
        ):
            continue

        valid.append(sentence)

    if not valid:
        return []

    words = []

    for sentence in valid:
        sentence_words = re.findall(
            r"\b[a-zA-Z][a-zA-Z0-9_.+-]*\b",
            sentence.lower()
        )
        words.extend(
            word
            for word in sentence_words
            if word not in STOP_WORDS
        )

    frequency = Counter(words)

    scored = []

    for index, sentence in enumerate(valid):
        score = score_sentence(sentence, frequency)

        if index < 10:
            score += 3

        scored.append((score, index, sentence))

    scored.sort(key=lambda item: item[0], reverse=True)

    selected = []
    covered_topics = set()

    for score, index, sentence in scored:
        lower = sentence.lower()

        sentence_topics = {
            topic
            for topic in TECHNICAL_TOPICS
            if topic.lower() in lower
        }

        if (
            sentence_topics
            and sentence_topics.issubset(covered_topics)
        ):
            continue

        selected.append((index, sentence))
        covered_topics.update(sentence_topics)

        if len(selected) >= max_sentences:
            break

    selected.sort(key=lambda item: item[0])

    return [sentence for _, sentence in selected]


# ============================================================
# TOPIC SUMMARY
# ============================================================

def create_topic_summary(text):
    topics = detect_topics(text)

    if not topics:
        return ""

    unique_topics = []
    for topic in topics:
        if topic not in unique_topics:
            unique_topics.append(topic)

    if len(unique_topics) > 12:
        unique_topics = unique_topics[:12]

    if len(unique_topics) == 1:
        return (
            "The main technical area covered is "
            + unique_topics[0]
            + "."
        )

    return (
        "The main technical areas covered are "
        + ", ".join(unique_topics[:-1])
        + " and "
        + unique_topics[-1]
        + "."
    )


# ============================================================
# NORMAL TECHNICAL DOCUMENT SUMMARY
# ============================================================

def summarize_normal_document(text):
    if not text:
        return "No meaningful text was available for summarization."

    purpose = detect_document_purpose(text)
    topic_summary = create_topic_summary(text)

    important_sentences = select_meaningful_sentences(
        text,
        max_sentences=5
    )

    output = ["PURPOSE\n" + purpose]

    if topic_summary:
        output.append("\nCOVERAGE\n" + topic_summary)

    if important_sentences:
        output.append(
            "\nKEY POINTS\n"
            + "\n".join(
                f"• {sentence}"
                for sentence in important_sentences
            )
        )

    return "\n\n".join(output)


# ============================================================
# STRUCTURED DOCUMENT
# ============================================================

def summarize_structured_document(text):
    return summarize_normal_document(text)


# ============================================================
# FLOWCHART / SHORT DOCUMENT
# ============================================================

def summarize_flowchart(text):
    if not text:
        return "No meaningful text was available for summarization."

    sentences = select_meaningful_sentences(
        text,
        max_sentences=4
    )

    if not sentences:
        return detect_document_purpose(text)

    return (
        detect_document_purpose(text)
        + "\n\nKEY FLOW / STEPS\n"
        + "\n".join(
            f"• {sentence}"
            for sentence in sentences
        )
    )


# ============================================================
# MAIN ENTRY POINT
# ============================================================

def summarize_text(text):
    if not text:
        return "No meaningful text was available for summarization."

    cleaned = prepare_summary_text(text)

    # IMPORTANT:
    # OCR / PDF extraction is NOT changed here.
    # This function only consumes the already-extracted text.

    if is_cv_document(cleaned):
        print("[SUMMARIZER] CV/Resume detected.")
        return summarize_cv(cleaned)

    lines = cleaned.splitlines()
    structured_score = 0

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if "|" in line:
            structured_score += 1

        if "[TABLE" in line.upper():
            structured_score += 2

        if is_command_line(line):
            structured_score += 1

    if structured_score >= 8:
        return summarize_structured_document(cleaned)

    if len(cleaned) < 1200:
        return summarize_flowchart(cleaned)

    return summarize_normal_document(cleaned)


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

def generate_summary(text):
    """Compatibility wrapper used by existing routes."""
    return summarize_text(text)
