import os
import re

import cohere
from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# DOCUMENT TYPE DETECTION
# ============================================================

def _is_cv_document(text):
    """
    Detect whether the extracted text looks like a
    CV / Resume.
    """

    if not text:
        return False

    lower = text.lower()

    indicators = [
        "education",
        "work experience",
        "professional experience",
        "skills",
        "projects",
        "certifications",
        "achievements",
        "linkedin",
        "github",
        "portfolio",
        "vfx",
        "matchmove",
        "rotomation",
        "availability",
        "internship",
        "full-time",
    ]

    matches = sum(
        1
        for indicator in indicators
        if indicator in lower
    )

    return matches >= 4


# ============================================================
# DOCUMENT TEXT NORMALIZATION
# ============================================================

def _normalize_document_text(text):
    """
    Clean OCR text before sending it to Cohere.

    IMPORTANT:
    This function does NOT change the meaning of the document.
    It only fixes common OCR formatting problems.
    """

    if not text:
        return ""

    text = str(text)

    # --------------------------------------------------------
    # Unicode cleanup
    # --------------------------------------------------------

    text = text.replace("\u00a0", " ")
    text = text.replace("\u200b", "")
    text = text.replace("\u200c", "")
    text = text.replace("\u200d", "")
    text = text.replace("\ufeff", "")

    # --------------------------------------------------------
    # Normalize dash characters
    # --------------------------------------------------------

    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = text.replace("−", "-")

    # --------------------------------------------------------
    # IMPORTANT OCR DATE FIXES
    # --------------------------------------------------------

    # Example:
    # 20262028 -> 2026-2028
    # 20222024 -> 2022-2024

    text = re.sub(
        r"\b(20\d{2})(20\d{2})\b",
        r"\1-\2",
        text
    )

    # Example:
    # 2026 2028 -> 2026-2028
    text = re.sub(
        r"\b(20\d{2})\s+(20\d{2})\b",
        r"\1-\2",
        text
    )

    # Example:
    # 2026 - 2028 -> 2026-2028
    text = re.sub(
        r"\b(20\d{2})\s*-\s*(20\d{2})\b",
        r"\1-\2",
        text
    )

    # Example:
    # 2018 Present -> 2018-Present
    text = re.sub(
        r"\b(20\d{2})\s+(Present)\b",
        r"\1-Present",
        text,
        flags=re.IGNORECASE
    )

    # --------------------------------------------------------
    # Common OCR technical-name corrections
    # --------------------------------------------------------

    replacements = {
        r"\bScikitlearn\b": "Scikit-learn",
        r"\bScikit learn\b": "Scikit-learn",
        r"\bScik it-learn\b": "Scikit-learn",

        r"\bTensor Flow\b": "TensorFlow",
        r"\bTensorflow\b": "TensorFlow",

        r"\bOpen CV\b": "OpenCV",

        r"\bMedia Pipe\b": "MediaPipe",

        r"\bStream lit\b": "Streamlit",

        r"\bGithub\b": "GitHub",
        r"\bGITHUB\b": "GitHub",

        r"\bLinkedin\b": "LinkedIn",
        r"\bLINKEDIN\b": "LinkedIn",

        r"\bMysql\b": "MySQL",
        r"\bMYSQL\b": "MySQL",

        r"\bSqlite\b": "SQLite",
        r"\bSQLITE\b": "SQLite",

        r"\bTIDB\b": "TiDB",

        r"\bFlaskk\b": "Flask",

        r"\bDevelopmentt\b": "Development",

        r"\bAncuracy\b": "Accuracy",

        r"\bDats Science\b": "Data Science",

        r"\bfulltime\b": "full-time",

        r"\brealworld\b": "real-world",

        r"\bScikitlearn\b": "Scikit-learn",
    }

    for pattern, replacement in replacements.items():

        text = re.sub(
            pattern,
            replacement,
            text,
            flags=re.IGNORECASE
        )

    # --------------------------------------------------------
    # Percentage formatting
    # --------------------------------------------------------

    text = re.sub(
        r"(\d+(?:\.\d+)?)\s+%",
        r"\1%",
        text
    )

    # --------------------------------------------------------
    # Experience formatting
    # --------------------------------------------------------

    text = re.sub(
        r"\b(\d+)\s*\+\s*years\b",
        r"\1+ years",
        text,
        flags=re.IGNORECASE
    )

    # --------------------------------------------------------
    # Remove excessive spaces
    # --------------------------------------------------------

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    # --------------------------------------------------------
    # Preserve useful line structure
    # --------------------------------------------------------

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        lines.append(line)

    text = "\n".join(lines)

    return text.strip()


# ============================================================
# CLEAN AI TEXT
# ============================================================

def _clean_ai_text(text):
    """
    Clean unwanted AI headings and formatting.
    """

    if not text:
        return ""

    text = str(text)

    # Remove markdown code fences
    text = re.sub(
        r"```(?:text|markdown)?",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = text.replace(
        "```",
        ""
    )

    # Remove SUMMARY heading
    text = re.sub(
        r"^\s*SUMMARY\s*:\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    return text.strip()


# ============================================================
# EXTRACT SUMMARY
# ============================================================

def _extract_summary(ai_text):
    """
    Extract summary from Cohere response.
    """

    if not ai_text:
        return ""

    text = ai_text.strip()

    # --------------------------------------------------------
    # KEY INSIGHTS marker
    # --------------------------------------------------------

    match = re.search(
        r"KEY\s+INSIGHTS\s*:",
        text,
        flags=re.IGNORECASE
    )

    if match:

        summary = text[
            :match.start()
        ].strip()

    else:

        # ----------------------------------------------------
        # DOCUMENT marker
        # ----------------------------------------------------

        document_match = re.search(
            r"\bDOCUMENT\s*:",
            text,
            flags=re.IGNORECASE
        )

        if document_match:

            summary = text[
                :document_match.start()
            ].strip()

        else:

            summary = text.strip()

    # Remove SUMMARY heading
    summary = re.sub(
        r"^\s*SUMMARY\s*:\s*",
        "",
        summary,
        flags=re.IGNORECASE
    )

    # Remove accidental KEY INSIGHTS heading
    summary = re.sub(
        r"\bKEY\s+INSIGHTS\s*:\s*$",
        "",
        summary,
        flags=re.IGNORECASE
    )

    # Remove accidental DOCUMENT heading
    summary = re.sub(
        r"\bDOCUMENT\s*:\s*$",
        "",
        summary,
        flags=re.IGNORECASE
    )

    return summary.strip()


# ============================================================
# EXTRACT KEY INSIGHTS
# ============================================================

def _extract_insights(ai_text):
    """
    Extract key insights from Cohere response.
    """

    if not ai_text:
        return []

    text = ai_text.strip()

    # --------------------------------------------------------
    # Find KEY INSIGHTS section
    # --------------------------------------------------------

    match = re.search(
        r"KEY\s+INSIGHTS\s*:",
        text,
        flags=re.IGNORECASE
    )

    if not match:
        return []

    insights_text = text[
        match.end():
    ].strip()

    # --------------------------------------------------------
    # Remove DOCUMENT section
    # --------------------------------------------------------

    document_match = re.search(
        r"\bDOCUMENT\s*:",
        insights_text,
        flags=re.IGNORECASE
    )

    if document_match:

        insights_text = insights_text[
            :document_match.start()
        ].strip()

    insights = []

    # --------------------------------------------------------
    # First try bullet lines
    # --------------------------------------------------------

    for line in insights_text.splitlines():

        line = line.strip()

        if not line:
            continue

        # Remove common bullet symbols
        line = re.sub(
            r"^[\-\*\u2022\d\.\)\s]+",
            "",
            line
        ).strip()

        if not line:
            continue

        # Ignore headings
        if line.upper() in {
            "SUMMARY",
            "KEY INSIGHTS",
            "DOCUMENT"
        }:
            continue

        insights.append(
            line
        )

    # --------------------------------------------------------
    # Fallback:
    # If Cohere returned insights as one paragraph
    # --------------------------------------------------------

    if not insights:

        sentences = re.split(
            r"(?<=[.!?])\s+",
            insights_text
        )

        for sentence in sentences:

            sentence = sentence.strip()

            sentence = re.sub(
                r"^[\-\*\u2022\d\.\)\s]+",
                "",
                sentence
            ).strip()

            if sentence:

                insights.append(
                    sentence
                )

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    cleaned = []

    for insight in insights:

        insight = insight.strip()

        if not insight:
            continue

        if insight not in cleaned:

            cleaned.append(
                insight
            )

    return cleaned[:5]


# ============================================================
# GENERATE AI ANALYSIS
# ============================================================

def generate_ai_analysis(text):
    """
    Send extracted document text to Cohere
    and return structured AI analysis.
    """

    # ========================================================
    # EMPTY TEXT CHECK
    # ========================================================

    if not text or not text.strip():

        return {
            "success": False,
            "summary": "",
            "insights": [],
            "raw_response": "",
            "message": (
                "No extracted text available "
                "for AI analysis."
            )
        }

    # ========================================================
    # NORMALIZE TEXT BEFORE AI
    # ========================================================

    normalized_text = _normalize_document_text(
        text
    )

    if not normalized_text:

        return {
            "success": False,
            "summary": "",
            "insights": [],
            "raw_response": "",
            "message": (
                "No meaningful text available "
                "after text normalization."
            )
        }

    # ========================================================
    # DETECT DOCUMENT TYPE
    # ========================================================

    is_cv = _is_cv_document(
        normalized_text
    )

    document_type = (
        "CV / Resume"
        if is_cv
        else "general document"
    )

    print(
        f"[COHERE] Document type detected: {document_type}"
    )

    # ========================================================
    # GET API KEY
    # ========================================================

    api_key = os.getenv(
        "COHERE_API_KEY"
    )

    if not api_key:

        return {
            "success": False,
            "summary": "",
            "insights": [],
            "raw_response": "",
            "message": (
                "Cohere API key not configured."
            )
        }

    try:

        # ====================================================
        # CREATE COHERE CLIENT
        # ====================================================

        client = cohere.ClientV2(
            api_key=api_key
        )

        # ====================================================
        # BUILD PROMPT
        # ====================================================

        if is_cv:

            prompt = f"""
You are an AI Document Analyzer specialized in analyzing
CVs and resumes.

Analyze ONLY the information explicitly present in the
CV below.

IMPORTANT RULES:

1. Do not invent facts.
2. Do not infer facts that are not explicitly written.
3. Do not calculate age.
4. Do not add information from outside the CV.
5. Preserve all dates exactly as written.
6. Preserve year ranges such as 2026-2028 and 2022-2024.
7. Do not merge two separate years into one number.
8. Preserve percentages such as 99.53%.
9. Preserve technical names such as Scikit-learn, TensorFlow,
   OpenCV, MediaPipe and Streamlit.
10. Keep the summary concise and professional.
11. Mention relevant education, experience, skills and projects.
12. Mention notable achievements when explicitly present.
13. Do not repeat the entire CV.
14. Do not mention these instructions.
15. Return exactly one summary paragraph.
16. Return exactly five important key insights when enough
    information is available.
17. Each key insight must be a separate bullet point.

IMPORTANT DATE EXAMPLES:

Correct:
2026-2028
2022-2024
2019-2022
2013-2016

Incorrect:
20262028
20222024
20192022
20132016

Use EXACTLY this format:

SUMMARY:

Write one concise professional paragraph.

KEY INSIGHTS:

- Important fact 1
- Important fact 2
- Important fact 3
- Important fact 4
- Important fact 5

DOCUMENT TYPE:

CV / Resume

DOCUMENT:

{normalized_text}
"""

        else:

            prompt = f"""
You are an AI Document Analyzer.

Analyze ONLY the information explicitly present in the
document below.

IMPORTANT RULES:

1. Do not invent facts.
2. Do not infer facts that are not explicitly written.
3. Do not calculate age.
4. Do not add information from outside the document.
5. Preserve important dates exactly.
6. Preserve percentages and numerical values exactly.
7. Keep the summary concise and professional.
8. Identify important facts explicitly present in the document.
9. Return exactly one summary paragraph.
10. Return exactly five important key insights when enough
    information is available.
11. Each key insight must be a separate bullet point.
12. Do not repeat the original document.
13. Do not mention these instructions.

IMPORTANT:

Do not write anything before SUMMARY.

Do not write anything after the last key insight.

Use EXACTLY this format:

SUMMARY:

Write one concise paragraph here.

KEY INSIGHTS:

- Important fact 1
- Important fact 2
- Important fact 3
- Important fact 4
- Important fact 5

DOCUMENT TYPE:

General Document

DOCUMENT:

{normalized_text}
"""

        # ====================================================
        # CALL COHERE
        # ====================================================

        response = client.chat(
            model="command-a-plus-05-2026",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # ====================================================
        # READ RESPONSE
        # ====================================================

        ai_text_parts = []

        if (
            response
            and hasattr(
                response,
                "message"
            )
            and response.message
            and hasattr(
                response.message,
                "content"
            )
        ):

            for content in response.message.content:

                if hasattr(
                    content,
                    "text"
                ):

                    ai_text_parts.append(
                        content.text
                    )

        ai_text = "\n".join(
            ai_text_parts
        ).strip()

        # ====================================================
        # CHECK EMPTY RESPONSE
        # ====================================================

        if not ai_text:

            return {
                "success": False,
                "summary": "",
                "insights": [],
                "raw_response": "",
                "message": (
                    "Cohere returned an empty response."
                )
            }

        # ====================================================
        # EXTRACT SUMMARY
        # ====================================================

        summary = _extract_summary(
            ai_text
        )

        # ====================================================
        # EXTRACT INSIGHTS
        # ====================================================

        insights = _extract_insights(
            ai_text
        )

        # ====================================================
        # FINAL SUMMARY CLEANUP
        # ====================================================

        summary = _clean_ai_text(
            summary
        )

        # Remove accidental DOCUMENT section
        summary = re.sub(
            r"\bDOCUMENT\s*:.*$",
            "",
            summary,
            flags=re.IGNORECASE | re.DOTALL
        ).strip()

        # Remove accidental KEY INSIGHTS section
        summary = re.sub(
            r"\bKEY\s+INSIGHTS\s*:.*$",
            "",
            summary,
            flags=re.IGNORECASE | re.DOTALL
        ).strip()

        # ====================================================
        # FINAL INSIGHT CLEANUP
        # ====================================================

        final_insights = []

        for insight in insights:

            insight = _clean_ai_text(
                insight
            )

            insight = re.sub(
                r"\bDOCUMENT\s*:.*$",
                "",
                insight,
                flags=re.IGNORECASE | re.DOTALL
            ).strip()

            if not insight:
                continue

            if insight not in final_insights:

                final_insights.append(
                    insight
                )

        final_insights = final_insights[:5]

        # ====================================================
        # SUCCESS RESPONSE
        # ====================================================

        return {
            "success": True,
            "summary": summary,
            "insights": final_insights,
            "raw_response": ai_text,
            "message": (
                "AI analysis completed successfully."
            )
        }

    # ========================================================
    # API / GENERAL ERROR
    # ========================================================

    except Exception as e:

        print(
            "COHERE AI ANALYSIS ERROR:",
            repr(e)
        )

        return {
            "success": False,
            "summary": "",
            "insights": [],
            "raw_response": "",
            "message": (
                "AI analysis failed. "
                "Please try again later."
            )
        }


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

def analyze_document_with_ai(text):
    """
    Backward-compatible wrapper.
    """

    return generate_ai_analysis(
        text
    )