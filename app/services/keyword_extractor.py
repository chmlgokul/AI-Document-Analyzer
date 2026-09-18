import re
from collections import Counter


STOP_WORDS = {
    # Common English words
    "the", "is", "a", "an", "and", "or", "of", "to", "in",
    "for", "on", "at", "by", "with", "from", "this", "that",
    "are", "was", "were", "be", "as", "it", "has", "have",
    "had", "not", "only", "but", "also", "than", "into",
    "their", "there", "then", "them", "they", "you", "your",
    "which", "who", "what", "when", "where", "how",

    # Common auxiliary / filler words
    "will", "would", "could", "should", "can", "may", "might",
    "shall", "must", "been", "being", "being", "do", "does",
    "did", "done", "get", "got", "let", "make", "made",
    "during", "through", "within", "under", "after", "before",
    "between", "about", "against", "over", "such", "any",
    "each", "every", "all", "both", "more", "most", "some",
    "other", "another", "same", "very", "also",

    # Document/common business words
    "letter", "document", "details", "information", "section",
    "page", "number", "date", "name", "email", "phone",
    "company", "pvt", "ltd", "private", "limited",

    # Website/email fragments
    "com", "www", "http", "https"
}


def extract_keywords(text, limit=10):

    if not text:
        return []

    words = re.findall(
        r"\b[a-zA-Z][a-zA-Z0-9_-]{3,}\b",
        text.lower()
    )

    filtered_words = []

    for word in words:

        if word in STOP_WORDS:
            continue

        if word.isdigit():
            continue

        filtered_words.append(word)

    word_counts = Counter(filtered_words)

    keywords = [
        word
        for word, count in word_counts.most_common(limit)
    ]

    return keywords