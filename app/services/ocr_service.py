import pytesseract

from PIL import (
    Image,
    ImageEnhance,
    ImageFilter,
    ImageOps
)


# Tesseract installation path
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def extract_text_from_image(filepath):

    try:

        # Open image
        image = Image.open(filepath)

        # Convert to RGB
        image = image.convert("RGB")


        # Get original dimensions
        width, height = image.size


        # Resize image for better OCR
        image = image.resize(
            (width * 2, height * 2)
        )


        # Convert to grayscale
        image = ImageOps.grayscale(image)


        # Improve contrast
        image = ImageOps.autocontrast(
            image
        )

        image = ImageEnhance.Contrast(
            image
        ).enhance(2.0)


        # Sharpen image
        image = image.filter(
            ImageFilter.SHARPEN
        )


        # OCR
        text = pytesseract.image_to_string(
            image,
            lang="eng",
            config="--psm 11"
        )


        return text.strip()


    except Exception as e:

        print(
            "IMAGE OCR ERROR:",
            repr(e)
        )

        return ""