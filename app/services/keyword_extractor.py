import re
from collections import Counter


# ---------------------------------------------------------
# STOP WORDS
# ---------------------------------------------------------

STOP_WORDS = {
    # Common English words
    "the", "is", "a", "an", "and", "or", "of", "to", "in",
    "for", "on", "at", "by", "with", "from", "this", "that",
    "are", "was", "were", "be", "as", "it", "has", "have",
    "had", "not", "only", "but", "also", "than", "into",
    "their", "there", "then", "them", "they", "you", "your",
    "which", "who", "what", "when", "where", "how",

    # Auxiliary / filler words
    "will", "would", "could", "should", "can", "may", "might",
    "shall", "must", "been", "being", "do", "does", "did",
    "done", "get", "got", "let", "make", "made", "during",
    "through", "within", "under", "after", "before", "between",
    "about", "against", "over", "such", "any", "each", "every",
    "all", "both", "more", "most", "some", "other", "another",
    "same", "very", "just", "here", "there",

    # Weak/common document words
    "letter", "document", "details", "information", "section",
    "page", "number", "date", "name", "email", "phone",
    "company", "pvt", "ltd", "private", "limited",

    # Common verbs that create noisy keywords
    "add", "added", "adding", "use", "used", "using",
    "run", "runs", "running", "install", "installed",
    "create", "created", "creating", "include", "included",
    "including", "check", "checked", "checking",
    "work", "works", "working", "start", "started",
    "starting", "open", "opened", "openning",

    # Technical/common noise
    "version", "command", "commands", "output", "result",
    "example", "examples", "step", "steps", "note", "notes",
    "type", "types", "file", "files", "folder", "folders",
    "line", "lines",

    # Website/email fragments
    "com", "www", "http", "https"
}


# ---------------------------------------------------------
# TECHNICAL TERMS THAT SHOULD BE PRESERVED
# ---------------------------------------------------------

IMPORTANT_TECHNICAL_TERMS = {
    "python",
    "pip",
    "venv",
    "virtualenv",
    "requirements",
    "requirements.txt",
    "github",
    "git",
    "docker",
    "flask",
    "fastapi",
    "django",
    "sql",
    "mysql",
    "postgresql",
    "sqlite",
    "mongodb",
    "firebase",
    "tensorflow",
    "keras",
    "pytorch",
    "scikit-learn",
    "numpy",
    "pandas",
    "matplotlib",
    "seaborn",
    "plotly",
    "opencv",
    "mediapipe",
    "tesseract",
    "ocr",
    "nlp",
    "llm",
    "machine-learning",
    "machine learning",
    "deep-learning",
    "deep learning",
    "artificial-intelligence",
    "artificial intelligence",
    "data-science",
    "data science",
    "environment",
    "deployment",
    "testing",
    "logging",
    "reproducibility",
    "api",
    "rest",
    "backend",
    "frontend",
    "streamlit"
}


# ---------------------------------------------------------
# TEXT NORMALIZATION
# ---------------------------------------------------------

def normalize_text(text):
    """
    Normalize extracted document text.

    Keeps technical terms such as:
    Python, requirements.txt, GitHub, etc.
    """

    if not text:
        return ""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    return text.lower()


# ---------------------------------------------------------
# WORD EXTRACTION
# ---------------------------------------------------------

def extract_words(text):
    """
    Extract meaningful words and technical terms.
    """

    # Keep dots, hyphens and underscores because
    # technical terms may contain them.
    words = re.findall(
        r"\b[a-zA-Z][a-zA-Z0-9_.-]{2,}\b",
        text
    )

    return words


# ---------------------------------------------------------
# PHRASE EXTRACTION
# ---------------------------------------------------------

def extract_phrases(text):
    """
    Extract common two-word technical/concept phrases.

    Example:
        data science
        machine learning
        cloud fundamentals
        environment variables
    """

    words = re.findall(
        r"\b[a-zA-Z][a-zA-Z0-9_-]{2,}\b",
        text.lower()
    )

    phrases = []

    for index in range(len(words) - 1):

        first = words[index]
        second = words[index + 1]

        if (
            first not in STOP_WORDS
            and second not in STOP_WORDS
            and len(first) >= 3
            and len(second) >= 3
        ):
            phrases.append(
                f"{first} {second}"
            )

    return phrases


# ---------------------------------------------------------
# KEYWORD EXTRACTION
# ---------------------------------------------------------

def extract_keywords(text, limit=10):

    if not text:
        return []

    normalized_text = normalize_text(text)

    # ---------------------------------------------
    # 1. Extract individual words
    # ---------------------------------------------

    words = extract_words(
        normalized_text
    )

    filtered_words = []

    for word in words:

        word = word.strip(
            ".,;:!?()[]{}<>\"'`"
        )

        if not word:
            continue

        # Ignore pure numbers
        if word.isdigit():
            continue

        # Ignore stop words
        if word in STOP_WORDS:
            continue

        # Ignore very short words
        if len(word) < 4:
            continue

        filtered_words.append(
            word
        )

    word_counts = Counter(
        filtered_words
    )

    # ---------------------------------------------
    # 2. Extract useful phrases
    # ---------------------------------------------

    phrases = extract_phrases(
        normalized_text
    )

    phrase_counts = Counter(
        phrases
    )

    # ---------------------------------------------
    # 3. Score individual keywords
    # ---------------------------------------------

    scored_keywords = []

    total_words = max(
        len(filtered_words),
        1
    )

    for word, count in word_counts.items():

        score = count

        # Reward technical terms
        if word in IMPORTANT_TECHNICAL_TERMS:
            score += 5

        # Reward repeated meaningful words
        if count >= 3:
            score += 2

        # Slight reward for longer specific words
        if len(word) >= 8:
            score += 1

        # Penalize extremely common generic words
        if word in {
            "project",
            "system",
            "process",
            "content",
            "basic",
            "important",
            "different",
            "general"
        }:
            score -= 2

        # Frequency ratio
        frequency_ratio = count / total_words

        if frequency_ratio > 0.01:
            score += 1

        scored_keywords.append(
            (
                word,
                score,
                count
            )
        )

    # ---------------------------------------------
    # 4. Sort individual keywords
    # ---------------------------------------------

    scored_keywords.sort(
        key=lambda item: (
            item[1],
            item[2],
            len(item[0])
        ),
        reverse=True
    )

    # ---------------------------------------------
    # 5. Select final keywords
    # ---------------------------------------------

    final_keywords = []

    # First add strong technical terms
    for word, score, count in scored_keywords:

        if word in IMPORTANT_TECHNICAL_TERMS:

            if word not in final_keywords:

                final_keywords.append(
                    word
                )

        if len(final_keywords) >= limit:
            break

    # Then fill remaining slots
    for word, score, count in scored_keywords:

        if word not in final_keywords:

            final_keywords.append(
                word
            )

        if len(final_keywords) >= limit:
            break

    # ---------------------------------------------
    # 6. Add useful multi-word phrases
    # ---------------------------------------------

    important_phrases = []

    for phrase, count in phrase_counts.items():

        phrase_words = phrase.split()

        if len(phrase_words) != 2:
            continue

        first = phrase_words[0]
        second = phrase_words[1]

        # Keep phrases that contain technical terms
        if (
            first in IMPORTANT_TECHNICAL_TERMS
            or second in IMPORTANT_TECHNICAL_TERMS
        ):
            important_phrases.append(
                (
                    phrase,
                    count
                )
            )

    important_phrases.sort(
        key=lambda item: (
            item[1],
            len(item[0])
        ),
        reverse=True
    )

    # Replace weak keywords with meaningful phrases
    for phrase, count in important_phrases:

        if phrase in final_keywords:
            continue

        if len(final_keywords) < limit:

            final_keywords.append(
                phrase
            )

    # ---------------------------------------------
    # 7. Final cleanup
    # ---------------------------------------------

    cleaned_keywords = []

    for keyword in final_keywords:

        keyword = keyword.strip()

        if not keyword:
            continue

        if keyword in STOP_WORDS:
            continue

        if keyword not in cleaned_keywords:

            cleaned_keywords.append(
                keyword
            )

        if len(cleaned_keywords) >= limit:
            break

    return cleaned_keywords