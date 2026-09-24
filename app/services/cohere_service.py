import os
import re

import cohere
from dotenv import load_dotenv


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# CLEAN AI TEXT
# =========================================================

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

    # Remove unwanted headings
    text = re.sub(
        r"\bSUMMARY\s*:\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    return text.strip()


# =========================================================
# EXTRACT SUMMARY
# =========================================================

def _extract_summary(ai_text):
    """
    Extract summary from Cohere response.
    """

    if not ai_text:
        return ""

    text = ai_text.strip()

    # -----------------------------------------------------
    # If KEY INSIGHTS exists, everything before it
    # is treated as summary.
    # -----------------------------------------------------

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

        # Try DOCUMENT marker
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

    # Remove accidental headings
    summary = re.sub(
        r"\bKEY\s+INSIGHTS\s*:\s*$",
        "",
        summary,
        flags=re.IGNORECASE
    )

    summary = re.sub(
        r"\bDOCUMENT\s*:\s*$",
        "",
        summary,
        flags=re.IGNORECASE
    )

    return summary.strip()


# =========================================================
# EXTRACT KEY INSIGHTS
# =========================================================

def _extract_insights(ai_text):
    """
    Extract key insights from Cohere response.
    """

    if not ai_text:
        return []

    text = ai_text.strip()

    # -----------------------------------------------------
    # Find KEY INSIGHTS section
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Remove DOCUMENT section
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # First try bullet lines
    # -----------------------------------------------------

    for line in insights_text.splitlines():

        line = line.strip()

        if not line:
            continue

        # Remove bullet symbols
        line = re.sub(
            r"^[\-\u2022\*\d\.\)\s]+",
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

    # -----------------------------------------------------
    # Fallback:
    # If Cohere returned insights in one paragraph
    # instead of bullet lines, split sentences.
    # -----------------------------------------------------

    if not insights:

        sentences = re.split(
            r"(?<=[.!?])\s+",
            insights_text
        )

        for sentence in sentences:

            sentence = sentence.strip()

            sentence = re.sub(
                r"^[\-\u2022\*\d\.\)\s]+",
                "",
                sentence
            ).strip()

            if sentence:

                insights.append(
                    sentence
                )

    # -----------------------------------------------------
    # Remove duplicates
    # -----------------------------------------------------

    cleaned = []

    for insight in insights:

        if insight not in cleaned:

            cleaned.append(
                insight
            )

    return cleaned[:5]


# =========================================================
# GENERATE AI ANALYSIS
# =========================================================

def generate_ai_analysis(text):
    """
    Send extracted document text to Cohere
    and return structured AI analysis.
    """

    # =====================================================
    # EMPTY TEXT CHECK
    # =====================================================

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

    # =====================================================
    # GET API KEY
    # =====================================================

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

        # =================================================
        # CREATE COHERE CLIENT
        # =================================================

        client = cohere.ClientV2(
            api_key=api_key
        )

        # =================================================
        # PROMPT
        # =================================================

        prompt = f"""
You are an AI Document Analyzer.

Analyze ONLY the information explicitly present in the
document below.

IMPORTANT RULES:

1. Do not invent facts.
2. Do not infer facts that are not explicitly written.
3. Do not calculate age.
4. Do not add information from outside the document.
5. Keep the summary concise and professional.
6. Identify important facts explicitly present in the document.
7. Return exactly one summary paragraph.
8. Return exactly five important key insights when enough
   information is available.
9. Each key insight must be a separate bullet point.
10. Do not repeat the original document.
11. Do not mention these instructions.

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

DOCUMENT:
{text}
"""

        # =================================================
        # CALL COHERE
        # =================================================

        response = client.chat(
            model="command-a-plus-05-2026",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # =================================================
        # READ RESPONSE
        # =================================================

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

        # =================================================
        # CHECK EMPTY RESPONSE
        # =================================================

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

        # =================================================
        # EXTRACT SUMMARY
        # =================================================

        summary = _extract_summary(
            ai_text
        )

        # =================================================
        # EXTRACT INSIGHTS
        # =================================================

        insights = _extract_insights(
            ai_text
        )

        # =================================================
        # FINAL SUMMARY CLEANUP
        # =================================================

        summary = _clean_ai_text(
            summary
        )

        # Remove DOCUMENT if it accidentally remains
        summary = re.sub(
            r"\bDOCUMENT\s*:.*$",
            "",
            summary,
            flags=re.IGNORECASE | re.DOTALL
        ).strip()

        # Remove KEY INSIGHTS if it accidentally remains
        summary = re.sub(
            r"\bKEY\s+INSIGHTS\s*:.*$",
            "",
            summary,
            flags=re.IGNORECASE | re.DOTALL
        ).strip()

        # =================================================
        # FINAL INSIGHT CLEANUP
        # =================================================

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

        final_insights = final_insights[
            :5
        ]

        # =================================================
        # SUCCESS RESPONSE
        # =================================================

        return {
            "success": True,
            "summary": summary,
            "insights": final_insights,
            "raw_response": ai_text,
            "message": (
                "AI analysis completed successfully."
            )
        }

    # =====================================================
    # API / GENERAL ERROR
    # =====================================================

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