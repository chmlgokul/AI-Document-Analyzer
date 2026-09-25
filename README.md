# AI Document Analyzer

AI Document Analyzer is a Flask-based web application for uploading, extracting, analyzing, searching, and managing documents through a web interface and REST APIs.

The application supports PDF, DOCX, TXT, JPG, JPEG, and PNG files. It combines document text extraction, OCR, keyword extraction, structured information extraction, rule-based summarization, AI-powered analysis using Cohere, document search, re-analysis, deletion, and analysis export.

---

## Project Overview

The main objective of this project is to simplify document analysis by automatically processing uploaded documents and presenting useful information through an interactive web interface.

Users can:

- Create an account
- Log in and log out
- Upload supported documents
- Extract text from documents
- Perform OCR on images
- Extract keywords and structured information
- Generate document summaries
- Generate AI-powered document analysis
- Search uploaded documents
- Re-analyze existing documents
- Export analysis results
- Delete documents
- Access their documents through protected user-specific pages

The project also provides REST APIs and Swagger documentation for programmatic access to document analysis functionality.

---

## Features

### User Authentication

- User registration
- Email validation
- Password confirmation
- Secure password hashing
- User login
- User logout
- Unique username validation
- Unique email validation
- Protected user-specific pages

### Document Management

- Document upload
- Uploaded document listing
- Document search
- Filename-based search
- Extracted-text search
- Document analysis
- Document re-analysis
- Document deletion
- User-specific document access

### Supported File Formats

- PDF
- DOCX
- TXT
- JPG
- JPEG
- PNG

### Text Extraction

Different file formats are processed using specialized libraries.

**PDF**
- PyMuPDF

**DOCX**
- python-docx

**TXT**
- Python file handling

**Images**
- Tesseract OCR
- pytesseract
- Pillow

### OCR

Image documents are processed using Tesseract OCR.

OCR processing includes:

- Image resizing
- RGB conversion
- Grayscale conversion
- Contrast enhancement
- Image sharpening
- Text extraction using Tesseract

The project also includes Tamil font support for generated document outputs.

### Keyword Extraction

The keyword extraction service processes document text using:

- Text normalization
- Word extraction
- Stop-word removal
- Word-frequency calculation
- Top keyword selection

### Information Extraction

The application extracts structured information from document text, including supported:

- Email addresses
- Phone numbers
- URLs
- Names
- Dates
- Education information
- Occupation information
- Salary information
- Other supported structured fields

### Rule-Based Summarization

The application provides a rule-based document summary based on extracted document text.

### AI-Powered Analysis

The application integrates Cohere for AI-assisted document analysis.

AI analysis can provide:

- Document summary
- Key insights
- AI-generated analysis based on the uploaded document

The AI service is implemented separately from the core document-processing services.

The application is designed so that the Cohere API key is stored through environment variables rather than hard-coded into the source code.

### Search and Filter

Users can search their uploaded documents using:

- Filename
- Extracted document text

The application provides an appropriate response when no matching document is found.

### Re-analysis

Existing documents can be analyzed again without uploading the file again.

The application:

1. Reads the stored document
2. Extracts the document text again
3. Re-processes the analysis
4. Updates the stored analysis
5. Returns the updated result

### Export

Analysis results can be exported in:

- TXT
- PDF

Exported analysis can include:

- Document name
- Upload date
- Keywords
- Extracted information
- Summary
- Extracted text

### User Profile

Users can view account information including:

- Username
- Email address
- Account creation date

---

# REST API

The project provides both the original `/api` endpoints and a versioned `/api/v1` API.

## API v1

Base URL:

```text
/api/v1