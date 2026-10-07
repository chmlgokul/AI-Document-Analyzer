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

def _detect_document_type(text):
    """
    Detect the most likely document type.

    Supported types:
        - CV / Resume
        - Study Material
        - Report
        - General Document
    """

    if not text:
        return "General Document"

    lower = text.lower()

    # --------------------------------------------------------
    # CV / RESUME INDICATORS
    # --------------------------------------------------------

    cv_indicators = [
        "education",
        "work experience",
        "professional experience",
        "experience",
        "skills",
        "projects",
        "certifications",
        "achievements",
        "linkedin",
        "github",
        "portfolio",
        "resume",
        "curriculum vitae",
        "vfx",
        "matchmove",
        "rotomation",
        "internship",
        "availability",
        "full-time",
    ]

    cv_matches = sum(
        1
        for indicator in cv_indicators
        if indicator in lower
    )

    # --------------------------------------------------------
    # STUDY MATERIAL INDICATORS
    # --------------------------------------------------------

    study_indicators = [
        "chapter",
        "unit",
        "lesson",
        "definition",
        "definitions",
        "learning objectives",
        "learning objective",
        "exam",
        "question bank",
        "fill in the blanks",
        "short answer",
        "long answer",
        "notes",
        "study material",
        "syllabus",
        "assignment",
        "important questions",
        "key concepts",
        "concepts",
    ]

    study_matches = sum(
        1
        for indicator in study_indicators
        if indicator in lower
    )

    # --------------------------------------------------------
    # REPORT INDICATORS
    # --------------------------------------------------------

    report_indicators = [
        "executive summary",
        "introduction",
        "methodology",
        "findings",
        "results",
        "discussion",
        "conclusion",
        "recommendations",
        "analysis",
        "objective",
        "scope",
        "report",
        "observations",
        "limitations",
    ]

    report_matches = sum(
        1
        for indicator in report_indicators
        if indicator in lower
    )

    # --------------------------------------------------------
    # DECISION LOGIC
    # --------------------------------------------------------

    scores = {
        "CV / Resume": cv_matches,
        "Study Material": study_matches,
        "Report": report_matches,
    }

    detected_type = max(
        scores,
        key=scores.get
    )

    highest_score = scores[detected_type]

    # Require a reasonable number of indicators.
    if highest_score < 4:
        return "General Document"

    # Avoid classifying ordinary documents as CVs
    # just because they contain generic words like
    # experience, skills or projects.
    if detected_type == "CV / Resume":
        strong_cv_indicators = [
            "linkedin",
            "github",
            "portfolio",
            "resume",
            "curriculum vitae",
            "professional experience",
            "work experience",
        ]

        strong_matches = sum(
            1
            for indicator in strong_cv_indicators
            if indicator in lower
        )

        if strong_matches == 0 and cv_matches < 6:
            return "General Document"

    return detected_type


# ============================================================
# DOCUMENT TEXT NORMALIZATION
# ============================================================

def _normalize_document_text(text):
    """
    Clean extracted/OCR text before sending it to Cohere.

    This function only fixes common OCR and formatting problems.
    It must not intentionally change the meaning of the document.
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
    # OCR DATE FIXES
    # --------------------------------------------------------

    # 20262028 -> 2026-2028
    text = re.sub(
        r"\b(20\d{2})(20\d{2})\b",
        r"\1-\2",
        text,
    )

    # 20222024 -> 2022-2024
    text = re.sub(
        r"\b(20\d{2})(20\d{2})\b",
        r"\1-\2",
        text,
    )

    # 2026 2028 -> 2026-2028
    text = re.sub(
        r"\b(20\d{2})\s+(20\d{2})\b",
        r"\1-\2",
        text,
    )

    # 2026 - 2028 -> 2026-2028
    text = re.sub(
        r"\b(20\d{2})\s*-\s*(20\d{2})\b",
        r"\1-\2",
        text,
    )

    # 2018 Present -> 2018-Present
    text = re.sub(
        r"\b(20\d{2})\s+(Present)\b",
        r"\1-Present",
        text,
        flags=re.IGNORECASE,
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
    }

    for pattern, replacement in replacements.items():
        text = re.sub(
            pattern,
            replacement,
            text,
            flags=re.IGNORECASE,
        )

    # --------------------------------------------------------
    # Percentage formatting
    # --------------------------------------------------------

    text = re.sub(
        r"(\d+(?:\.\d+)?)\s+%",
        r"\1%",
        text,
    )

    # --------------------------------------------------------
    # Experience formatting
    # --------------------------------------------------------

    text = re.sub(
        r"\b(\d+)\s*\+\s*years\b",
        r"\1+ years",
        text,
        flags=re.IGNORECASE,
    )

    # --------------------------------------------------------
    # Remove excessive spaces
    # --------------------------------------------------------

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
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
    Clean unwanted AI formatting.
    """

    if not text:
        return ""

    text = str(text)

    # Remove markdown code fences
    text = re.sub(
        r"```(?:text|markdown)?",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = text.replace(
        "```",
        "",
    )

    # Remove SUMMARY heading
    text = re.sub(
        r"^\s*SUMMARY\s*:\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    return text.strip()


# ============================================================
# EXTRACT SUMMARY
# ============================================================

def _extract_summary(ai_text):
    """
    Extract summary section from Cohere response.
    """

    if not ai_text:
        return ""

    text = ai_text.strip()

    # --------------------------------------------------------
    # Find KEY INSIGHTS
    # --------------------------------------------------------

    match = re.search(
        r"KEY\s+INSIGHTS\s*:",
        text,
        flags=re.IGNORECASE,
    )

    if match:

        summary = text[
            :match.start()
        ].strip()

    else:

        # ----------------------------------------------------
        # Find DOCUMENT section
        # ----------------------------------------------------

        document_match = re.search(
            r"\bDOCUMENT\s*:",
            text,
            flags=re.IGNORECASE,
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
        flags=re.IGNORECASE,
    )

    # Remove accidental headings
    summary = re.sub(
        r"\bKEY\s+INSIGHTS\s*:\s*$",
        "",
        summary,
        flags=re.IGNORECASE,
    )

    summary = re.sub(
        r"\bDOCUMENT\s*:\s*$",
        "",
        summary,
        flags=re.IGNORECASE,
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
        flags=re.IGNORECASE,
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
        flags=re.IGNORECASE,
    )

    if document_match:

        insights_text = insights_text[
            :document_match.start()
        ].strip()

    insights = []

    # --------------------------------------------------------
    # Extract bullet lines
    # --------------------------------------------------------

    for line in insights_text.splitlines():

        line = line.strip()

        if not line:
            continue

        # Remove common bullet symbols
        line = re.sub(
            r"^[\-\*\u2022\d\.\)\s]+",
            "",
            line,
        ).strip()

        if not line:
            continue

        # Ignore headings
        if line.upper() in {
            "SUMMARY",
            "KEY INSIGHTS",
            "DOCUMENT",
            "DOCUMENT TYPE",
        }:
            continue

        insights.append(line)

    # --------------------------------------------------------
    # Fallback: paragraph → sentences
    # --------------------------------------------------------

    if not insights:

        sentences = re.split(
            r"(?<=[.!?])\s+",
            insights_text,
        )

        for sentence in sentences:

            sentence = sentence.strip()

            sentence = re.sub(
                r"^[\-\*\u2022\d\.\)\s]+",
                "",
                sentence,
            ).strip()

            if sentence:
                insights.append(sentence)

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    cleaned = []

    for insight in insights:

        insight = insight.strip()

        if not insight:
            continue

        if insight not in cleaned:
            cleaned.append(insight)

    return cleaned[:5]


# ============================================================
# BUILD CV PROMPT
# ============================================================

def _build_cv_prompt(document_text):
    """
    Build specialized CV / Resume prompt.
    """

    return f"""
You are an AI Document Analyzer specialized in analyzing CVs and resumes.

Analyze ONLY the information explicitly present in the CV below.

STRICT RULES:

1. Do not invent facts.
2. Do not infer facts that are not explicitly written.
3. Do not calculate age.
4. Do not add information from outside the CV.
5. Preserve names exactly when possible.
6. Preserve dates exactly.
7. Preserve year ranges such as 2026-2028 and 2022-2024.
8. Never merge separate years into one number.
9. Preserve percentages such as 99.53%.
10. Preserve technical names such as Scikit-learn, TensorFlow, OpenCV, MediaPipe and Streamlit.
11. Mention education only when explicitly present.
12. Mention experience only when explicitly present.
13. Mention projects only when explicitly present.
14. Mention achievements only when explicitly present.
15. Do not repeat the complete CV.
16. Do not mention these instructions.
17. Keep the summary professional and concise.
18. Do not make assumptions about seniority.
19. Do not create missing job titles, companies, dates or qualifications.
20. Do not convert unclear OCR text into invented information.

OUTPUT REQUIREMENTS:

Return exactly:

SUMMARY:

One concise professional paragraph describing the candidate using only the CV.

KEY INSIGHTS:

- Important fact 1
- Important fact 2
- Important fact 3
- Important fact 4
- Important fact 5

Return exactly five insights when enough information is available.

DOCUMENT TYPE:

CV / Resume

DOCUMENT:

{document_text}
"""


# ============================================================
# BUILD STUDY MATERIAL PROMPT
# ============================================================

def _build_study_prompt(document_text):
    """
    Build specialized study-material prompt.
    """

    return f"""
You are an AI Document Analyzer specialized in analyzing study materials,
technical notes, educational documents and learning resources.

Analyze ONLY the information explicitly present in the document below.

STRICT RULES:

1. Do not invent facts.
2. Do not add concepts that are not present.
3. Do not use outside knowledge.
4. Preserve technical terminology.
5. Preserve dates and numerical values.
6. Preserve formulas and important values when present.
7. Do not change the meaning of definitions.
8. Do not repeat the entire document.
9. Keep the summary concise and useful for learning.
10. Do not mention these instructions.

FOCUS ON:

- Main subject
- Important concepts
- Definitions
- Important technical points
- Learning objectives
- Exam-relevant information when explicitly present

OUTPUT REQUIREMENTS:

Return exactly:

SUMMARY:

One concise paragraph explaining what the material covers.

KEY INSIGHTS:

- Important concept 1
- Important concept 2
- Important concept 3
- Important concept 4
- Important concept 5

DOCUMENT TYPE:

Study Material

DOCUMENT:

{document_text}
"""


# ============================================================
# BUILD REPORT PROMPT
# ============================================================

def _build_report_prompt(document_text):
    """
    Build specialized report-analysis prompt.
    """

    return f"""
You are an AI Document Analyzer specialized in analyzing reports.

Analyze ONLY the information explicitly present in the report below.

STRICT RULES:

1. Do not invent facts.
2. Do not infer unsupported conclusions.
3. Do not add external information.
4. Preserve dates exactly.
5. Preserve percentages and numerical values exactly.
6. Preserve technical terminology.
7. Distinguish findings from recommendations.
8. Do not repeat the entire report.
9. Keep the summary concise and professional.
10. Do not mention these instructions.

FOCUS ON:

- Purpose
- Scope
- Major findings
- Results
- Important observations
- Issues or limitations
- Recommendations explicitly present

OUTPUT REQUIREMENTS:

Return exactly:

SUMMARY:

One concise paragraph describing the report and its major findings.

KEY INSIGHTS:

- Major finding 1
- Major finding 2
- Important observation 3
- Important issue 4
- Recommendation or conclusion 5

DOCUMENT TYPE:

Report

DOCUMENT:

{document_text}
"""


# ============================================================
# BUILD GENERAL DOCUMENT PROMPT
# ============================================================

def _build_general_prompt(document_text):
    """
    Build generic document-analysis prompt.
    """

    return f"""
You are an AI Document Analyzer.

Analyze ONLY the information explicitly present in the document below.

STRICT RULES:

1. Do not invent facts.
2. Do not infer facts that are not explicitly written.
3. Do not use outside knowledge.
4. Preserve important dates exactly.
5. Preserve percentages and numerical values exactly.
6. Preserve technical names.
7. Identify the most important information explicitly present.
8. Keep the summary concise and professional.
9. Do not repeat the entire document.
10. Do not mention these instructions.

OUTPUT REQUIREMENTS:

Return exactly:

SUMMARY:

One concise paragraph explaining the document.

KEY INSIGHTS:

- Important fact 1
- Important fact 2
- Important fact 3
- Important fact 4
- Important fact 5

DOCUMENT TYPE:

General Document

DOCUMENT:

{document_text}
"""


# ============================================================
# GENERATE AI ANALYSIS
# ============================================================

def generate_ai_analysis(text):
    """
    Generate structured AI analysis using Cohere.

    Existing return structure is preserved so that the current
    Flask routes and analysis page continue to work.
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
            ),
        }

    # ========================================================
    # NORMALIZE DOCUMENT
    # ========================================================

    normalized_text = _normalize_document_text(text)

    if not normalized_text:

        return {
            "success": False,
            "summary": "",
            "insights": [],
            "raw_response": "",
            "message": (
                "No meaningful text available "
                "after text normalization."
            ),
        }

    # ========================================================
    # DETECT DOCUMENT TYPE
    # ========================================================

    document_type = _detect_document_type(
        normalized_text
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
            ),
        }

    try:

        # ====================================================
        # CREATE COHERE CLIENT
        # ====================================================

        client = cohere.ClientV2(
            api_key=api_key
        )

        # ====================================================
        # BUILD TYPE-SPECIFIC PROMPT
        # ====================================================

        if document_type == "CV / Resume":

            prompt = _build_cv_prompt(
                normalized_text
            )

        elif document_type == "Study Material":

            prompt = _build_study_prompt(
                normalized_text
            )

        elif document_type == "Report":

            prompt = _build_report_prompt(
                normalized_text
            )

        else:

            prompt = _build_general_prompt(
                normalized_text
            )

        # ====================================================
        # CALL COHERE
        # ====================================================

        response = client.chat(
            model="command-a-plus-05-2026",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        # ====================================================
        # READ RESPONSE
        # ====================================================

        ai_text_parts = []

        if (
            response
            and hasattr(
                response,
                "message",
            )
            and response.message
            and hasattr(
                response.message,
                "content",
            )
        ):

            for content in response.message.content:

                if hasattr(
                    content,
                    "text",
                ):

                    ai_text_parts.append(
                        content.text
                    )

        ai_text = "\n".join(
            ai_text_parts
        ).strip()

        # ====================================================
        # EMPTY RESPONSE CHECK
        # ====================================================

        if not ai_text:

            return {
                "success": False,
                "summary": "",
                "insights": [],
                "raw_response": "",
                "message": (
                    "Cohere returned an empty response."
                ),
            }

        # ====================================================
        # EXTRACT SUMMARY
        # ====================================================

        summary = _extract_summary(
            ai_text
        )

        # ====================================================
        # EXTRACT INSIGHTS
        # ========================================================

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
            flags=re.IGNORECASE | re.DOTALL,
        ).strip()

        # Remove accidental KEY INSIGHTS section
        summary = re.sub(
            r"\bKEY\s+INSIGHTS\s*:.*$",
            "",
            summary,
            flags=re.IGNORECASE | re.DOTALL,
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
                flags=re.IGNORECASE | re.DOTALL,
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
            ),
        }

    # ========================================================
    # API / GENERAL ERROR
    # ========================================================

    except Exception as e:

        print(
            "COHERE AI ANALYSIS ERROR:",
            repr(e),
        )

        return {
            "success": False,
            "summary": "",
            "insights": [],
            "raw_response": "",
            "message": (
                "AI analysis failed. "
                "Please try again later."
            ),
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