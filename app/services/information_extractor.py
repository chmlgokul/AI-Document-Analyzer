import re


def extract_information(text):

    if not text:
        return {}

    information = {}

    # Email addresses
    emails = re.findall(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        text
    )

    if emails:
        information["emails"] = list(
            dict.fromkeys(emails)
        )

    # Phone numbers
    phone_numbers = re.findall(
        r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{2}[\s-]?\d{3}[\s-]?\d{4}(?!\d)",
        text
    )

    if phone_numbers:
        information["phone_numbers"] = list(
            dict.fromkeys(phone_numbers)
        )

    # Dates - DD/MM/YYYY or DD-MM-YYYY
    numeric_dates = re.findall(
        r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b",
        text
    )

    # Dates - DD Month YYYY
    text_dates = re.findall(
        r"\b\d{1,2}\s+"
        r"(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December)"
        r"\s+\d{4}\b",
        text,
        re.IGNORECASE
    )

    all_dates = numeric_dates + text_dates

    if all_dates:
        information["dates"] = list(
            dict.fromkeys(all_dates)
        )

    # URLs
    urls = re.findall(
        r"(?:https?://|www\.)[^\s]+",
        text,
        re.IGNORECASE
    )

    if urls:
        information["urls"] = list(
            dict.fromkeys(urls)
        )

    # Currency amounts
    amounts = re.findall(
        r"(?:₹|Rs\.?|INR)\s?[\d,]+(?:\.\d{1,2})?",
        text,
        re.IGNORECASE
    )

    if amounts:
        information["currency_amounts"] = list(
            dict.fromkeys(amounts)
        )

    # PAN numbers
    pan_numbers = re.findall(
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
        text
    )

    if pan_numbers:
        information["pan_numbers"] = list(
            dict.fromkeys(pan_numbers)
        )

    return information