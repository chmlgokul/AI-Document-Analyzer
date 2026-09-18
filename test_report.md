# AI Document Analyzer - Test Report

## 1. Project Information

Project Name: AI Document Analyzer

Technology: Python, Flask, SQLite, SQLAlchemy

Testing Framework: pytest

Testing Type:
- Manual Testing
- Automated Testing

## 2. Testing Objective

The objective of testing is to verify that the major features of the AI Document Analyzer work correctly and produce the expected results.

The testing process covers user authentication, document upload, document processing, OCR, analysis, search, document management, export functionality, and automated application tests.

## 3. Testing Environment

Operating System: Windows

Python Version: 3.11.9

Web Framework: Flask

Database: SQLite

Testing Framework: pytest 9.1.1

OCR Engine: Tesseract OCR

Browser: Google Chrome

## 4. Manual Test Cases

| Test ID | Test Case | Expected Result | Status |
|---|---|---|---|
| TC01 | User Registration | New user account should be created | PASS |
| TC02 | Invalid Email | Invalid email should be rejected | PASS |
| TC03 | Password Mismatch | Registration should be rejected | PASS |
| TC04 | Duplicate Username/Email | Existing account details should be rejected | PASS |
| TC05 | User Login | Valid credentials should login successfully | PASS |
| TC06 | Invalid Password | Login should be rejected | PASS |
| TC07 | Logout | User should be logged out successfully | PASS |
| TC08 | PDF Upload | PDF should be uploaded successfully | PASS |
| TC09 | DOCX Upload | DOCX should be uploaded successfully | PASS |
| TC10 | TXT Upload | TXT should be uploaded successfully | PASS |
| TC11 | JPG Upload | JPG image should be uploaded and processed | PASS |
| TC12 | PNG Upload | PNG image should be uploaded and processed | PASS |
| TC13 | PDF Text Extraction | Text should be extracted from PDF | PASS |
| TC14 | DOCX Text Extraction | Text should be extracted from DOCX | PASS |
| TC15 | TXT Text Extraction | Text should be extracted from TXT | PASS |
| TC16 | Image OCR | Text should be extracted from image | PASS |
| TC17 | Keyword Extraction | Important keywords should be displayed | PASS |
| TC18 | Information Extraction | Structured information should be displayed | PASS |
| TC19 | Document Summary | Document summary should be generated | PASS |
| TC20 | Document Search | Matching documents should be displayed | PASS |
| TC21 | No Search Result | Appropriate no-result message should be displayed | PASS |
| TC22 | Clear Search | Search filter should be cleared | PASS |
| TC23 | Document Analysis | Analysis page should display results | PASS |
| TC24 | Re-analysis | Document should be analyzed again | PASS |
| TC25 | Document Delete | Selected document should be deleted | PASS |
| TC26 | TXT Export | Analysis should download as TXT | PASS |
| TC27 | PDF Export | Analysis should download as PDF | PASS |
| TC28 | Profile Page | User profile details should be displayed | PASS |
| TC29 | Invalid File Type | Unsupported file should be rejected | PASS |
| TC30 | Empty File Selection | Upload should require a file | PASS |

## 5. Automated Testing

The project includes automated tests using pytest.

Test command:

```text
pytest