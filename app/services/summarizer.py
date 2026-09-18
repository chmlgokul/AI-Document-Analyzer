import re
from collections import Counter


STOP_WORDS = {
    "the", "is", "a", "an", "and", "or", "of", "to", "in",
    "for", "on", "at", "by", "with", "from", "this", "that",
    "are", "was", "were", "be", "as", "it", "has", "have",
    "had", "not", "only", "but", "also", "than", "into",
    "their", "there", "then", "them", "they", "you", "your",
    "which", "who", "what", "when", "where", "how",
    "our", "these", "those", "during", "through", "within",
    "under", "over", "after", "before", "between", "about"
}


def clean_line(line):
    if not line:
        return ""

    line = re.sub(
        r"[_|~`@#$%^&*+=<>\\/]+",
        " ",
        line
    )

    line = re.sub(
        r"\s+",
        " ",
        line
    )

    return line.strip()


def get_words(text):
    return re.findall(
        r"\b[a-zA-Z][a-zA-Z0-9_-]{2,}\b",
        text.lower()
    )


def is_noise(line):
    if not line:
        return True

    words = get_words(line)

    if len(words) < 2:
        return True

    letters = sum(
        char.isalpha()
        for char in line
    )

    non_space = len(
        line.replace(" ", "")
    )

    if non_space == 0:
        return True

    ratio = letters / non_space

    if ratio < 0.60:
        return True

    return False


def remove_duplicates(lines):
    result = []
    seen = set()

    for line in lines:

        key = re.sub(
            r"\s+",
            " ",
            line.lower()
        ).strip()

        if key in seen:
            continue

        seen.add(key)
        result.append(line)

    return result


def extract_sentences(text):
    sentences = re.split(
        r"(?<=[.!?])\s+",
        text.strip()
    )

    result = []

    for sentence in sentences:

        sentence = clean_line(sentence)

        words = get_words(sentence)

        if len(words) < 7:
            continue

        if len(sentence) > 350:
            continue

        if is_noise(sentence):
            continue

        result.append(sentence)

    return remove_duplicates(result)


def extract_meaningful_lines(text):
    lines = []

    for raw_line in text.splitlines():

        line = clean_line(raw_line)

        if is_noise(line):
            continue

        if len(line) < 8:
            continue

        if len(line) > 180:
            continue

        lines.append(line)

    return remove_duplicates(lines)


def score_sentences(sentences, full_text):

    words = get_words(full_text)

    frequency = Counter(
        word
        for word in words
        if word not in STOP_WORDS
    )

    scored = []

    for index, sentence in enumerate(sentences):

        sentence_words = get_words(sentence)

        useful_words = [
            word
            for word in sentence_words
            if word not in STOP_WORDS
        ]

        if not useful_words:
            continue

        score = sum(
            frequency.get(word, 0)
            for word in useful_words
        )

        # Prefer medium-length useful sentences
        if 10 <= len(sentence_words) <= 45:
            score += 4

        # Small preference for early sentences
        score += max(
            0,
            2 - index * 0.05
        )

        scored.append(
            (score, index, sentence)
        )

    return scored


def summarize_normal_document(text, sentence_count=4):

    sentences = extract_sentences(text)

    if not sentences:
        return ""

    scored = score_sentences(
        sentences,
        text
    )

    if not scored:
        return ""

    selected = sorted(
        scored,
        key=lambda item: item[0],
        reverse=True
    )[:sentence_count]

    selected.sort(
        key=lambda item: item[1]
    )

    return " ".join(
        item[2]
        for item in selected
    ).strip()


def summarize_structured_document(text, limit=8):

    lines = extract_meaningful_lines(text)

    if not lines:
        return ""

    # Detect section-like headings
    heading_lines = []
    content_lines = []

    for line in lines:

        words = get_words(line)

        # Short lines are often headings / labels
        if 1 <= len(words) <= 5:
            heading_lines.append(line)

        else:
            content_lines.append(line)

    # Use important content lines
    scored = []

    all_words = get_words(text)

    frequency = Counter(
        word
        for word in all_words
        if word not in STOP_WORDS
    )

    for index, line in enumerate(content_lines):

        words = get_words(line)

        useful_words = [
            word
            for word in words
            if word not in STOP_WORDS
        ]

        if not useful_words:
            continue

        score = sum(
            frequency.get(word, 0)
            for word in useful_words
        )

        # Prefer informative lines
        if 5 <= len(useful_words) <= 30:
            score += 3

        score += max(
            0,
            2 - index * 0.03
        )

        scored.append(
            (score, index, line)
        )

    if not scored:
        return ""

    selected = sorted(
        scored,
        key=lambda item: item[0],
        reverse=True
    )[:limit]

    selected.sort(
        key=lambda item: item[1]
    )

    selected_lines = [
        item[2]
        for item in selected
    ]

    return " ".join(
        selected_lines
    ).strip()


def summarize_flowchart(text, limit=10):

    lines = extract_meaningful_lines(text)

    if not lines:
        return ""

    # Remove very long OCR sentences
    short_lines = [
        line
        for line in lines
        if len(get_words(line)) <= 10
    ]

    if not short_lines:
        short_lines = lines

    short_lines = remove_duplicates(
        short_lines
    )

    selected = short_lines[:limit]

    return (
        "The document contains the following "
        "key topics: "
        + "; ".join(selected)
        + "."
    )


def summarize_text(text, sentence_count=4):

    if not text:
        return ""

    # ----------------------------------------
    # Clean input
    # ----------------------------------------

    cleaned_text = text.strip()

    if len(cleaned_text) < 30:
        return cleaned_text

    # ----------------------------------------
    # Try sentence-based summary first
    # ----------------------------------------

    normal_summary = summarize_normal_document(
        cleaned_text,
        sentence_count
    )

    # ----------------------------------------
    # Detect structured documents
    # ----------------------------------------

    lines = extract_meaningful_lines(
        cleaned_text
    )

    line_count = len(lines)

    sentence_count_found = len(
        extract_sentences(cleaned_text)
    )

    # Many short lines + few sentences
    # usually means resume, table, flowchart,
    # technical document or OCR content.
    structured_document = (
        line_count >= 8
        and sentence_count_found <= 3
    )

    if structured_document:

        structured_summary = summarize_structured_document(
            cleaned_text,
            limit=8
        )

        if structured_summary:

            # Avoid returning an extremely long summary
            if len(structured_summary) > 1000:
                structured_summary = (
                    structured_summary[:1000]
                    + "..."
                )

            return structured_summary

    # ----------------------------------------
    # Normal document
    # ----------------------------------------

    if normal_summary:

        if len(normal_summary) > 1200:
            normal_summary = (
                normal_summary[:1200]
                + "..."
            )

        return normal_summary

    # ----------------------------------------
    # Final fallback
    # ----------------------------------------

    flowchart_summary = summarize_flowchart(
        cleaned_text,
        limit=10
    )

    if flowchart_summary:
        return flowchart_summary

    return cleaned_text[:1000]