import os
import tempfile

from app.services.text_extractor import (
    extract_text_from_txt
)


def test_txt_extraction():

    test_text = (
        "AI Document Analyzer\n"
        "Python Flask Project\n"
        "Machine Learning"
    )

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".txt",
        delete=False,
        encoding="utf-8"
    ) as file:

        file.write(test_text)
        filepath = file.name

    try:

        extracted_text = extract_text_from_txt(
            filepath
        )

        assert "AI Document Analyzer" in extracted_text
        assert "Python Flask Project" in extracted_text
        assert "Machine Learning" in extracted_text

    finally:

        if os.path.exists(filepath):
            os.remove(filepath)