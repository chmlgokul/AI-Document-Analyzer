# AI Document Analyzer

AI Document Analyzer is a Flask-based web application that allows users to upload documents and automatically extract, analyze, and organize useful information from them.

The application supports PDF, DOCX, TXT, JPG, JPEG, and PNG files. It provides text extraction, OCR for images, keyword extraction, structured information extraction, document summarization, search, re-analysis, document deletion, and analysis export.

## Project Overview

The main objective of this project is to simplify document analysis by automatically processing uploaded documents and presenting the extracted information through a web interface.

Users can create an account, log in securely, upload documents, analyze them, search their documents, re-analyze existing files, export analysis results, and manage their uploaded documents.

## Features

### User Authentication

- User registration
- Email validation
- Password confirmation
- Secure password hashing
- User login
- User logout
- Unique username and email validation
- Protected user-specific pages

### Document Management

- Upload documents
- View uploaded documents
- Search documents by filename
- Search documents using extracted text
- Analyze documents
- Re-analyze documents
- Delete documents
- User-specific document access

### Supported File Formats

- PDF
- DOCX
- TXT
- JPG
- JPEG
- PNG

### Text Extraction

The application extracts text from different document formats using specialized Python libraries.

PDF:
- PyMuPDF

DOCX:
- python-docx

TXT:
- Python file handling

Images:
- Tesseract OCR
- pytesseract
- Pillow

### OCR

The application uses Tesseract OCR to extract text from image-based documents.

OCR processing includes:

- Image resizing
- RGB conversion
- Grayscale conversion
- Automatic contrast enhancement
- Contrast adjustment
- Image sharpening
- Text extraction using Tesseract

### Keyword Extraction

The application identifies frequently occurring meaningful words from extracted document text.

The keyword extraction process includes:

- Text normalization
- Word extraction
- Stop-word removal
- Word frequency calculation
- Top keyword selection

### Information Extraction

The application extracts structured information from document text, such as:

- Email addresses
- Phone numbers
- URLs
- Other identifiable information supported by the extraction logic

### Document Summarization

The application generates a concise summary from the extracted document text using a rule-based summarization approach.

### Search and Filter

Users can search their uploaded documents using:

- Filename
- Extracted document text

The application also displays an appropriate message when no matching document is found.

### Re-analysis

Users can re-analyze an existing document without uploading it again.

The application reads the original stored file, performs text extraction again, updates the database, and displays the updated analysis.

### Export

Users can export document analysis results in:

- TXT format
- PDF format

The exported analysis includes:

- Document name
- Upload date
- Keywords
- Extracted information
- Summary
- Extracted text

### User Profile

Users can view their:

- Username
- Email address
- Account creation date

## Technology Stack

### Backend

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Werkzeug

### Document Processing

- PyMuPDF
- python-docx
- Pillow
- pytesseract
- Tesseract OCR

### Database

- SQLite
- SQLAlchemy ORM

### PDF Generation

- ReportLab

### Testing

- pytest

### Frontend

- HTML
- CSS
- Jinja2 Templates

## Project Structure

```text
Document_Analyzer/
│
├── app/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── document.py
│   │   └── user.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── documents.py
│   │   └── profile.py
│   │
│   ├── services/
│   │   ├── keyword_extractor.py
│   │   ├── information_extractor.py
│   │   ├── summarizer.py
│   │   ├── ocr_service.py
│   │   └── text_extractor.py
│   │
│   ├── static/
│   │
│   ├── templates/
│   │   ├── auth/
│   │   ├── analysis.html
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── documents.html
│   │   ├── profile.html
│   │   └── upload.html
│   │
│   └── __init__.py
│
├── tests/
│   ├── conftest.py
│   ├── test_extraction.py
│   └── test_upload.py
│
├── app.py
├── config.py
├── requirements.txt
└── README.md