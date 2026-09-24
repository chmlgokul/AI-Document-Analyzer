AI DOCUMENT ANALYZER

Project Report

A Flask-Based Document Processing and Analysis Web Application

Technologies Used: Python, Flask, SQLite, SQLAlchemy, Tesseract OCR, PyMuPDF, python-docx

Submitted by: Gokulakkannan

Project Type: Data Science / Artificial Intelligence Project

2. ABSTRACT

The AI Document Analyzer is a web-based document processing application developed using Python and Flask. The system allows users to register, log in, upload documents, and automatically extract and analyze their content.

The application supports PDF, DOCX, TXT, JPG, JPEG, and PNG file formats. For text-based documents, the system performs text extraction using suitable document processing libraries. For image files, Optical Character Recognition (OCR) is performed using Tesseract OCR.

After extracting the document content, the system provides keyword extraction, structured information extraction, and document summarization. Users can search their uploaded documents, re-analyze existing documents, delete documents, and export analysis results in TXT and PDF formats.

The application uses SQLite with SQLAlchemy for database management and Flask-Login for user authentication and protected routes. The system was tested through both manual and automated testing. The automated test suite achieved a result of 3 passed tests out of 3.

3. INTRODUCTION

Documents contain large amounts of information that can require significant time to read, organize, and analyze manually. Different document formats also require different methods for extracting their content. Image-based documents create an additional challenge because their text cannot be directly accessed as normal text.

The AI Document Analyzer was developed to provide a single web-based platform for handling different types of documents. The application accepts commonly used document and image formats and automatically processes their content.

The system combines document text extraction, Optical Character Recognition, keyword extraction, structured information extraction, and summarization into one application. A web interface allows users to upload and manage their documents and view the generated analysis results.

The project also includes user authentication and user-specific document management. Each uploaded document is associated with the corresponding user, allowing users to manage their own documents.

The application was developed using Python and Flask as the primary backend technologies, with SQLite used for database storage. The project also includes automated tests using pytest to verify selected application functionality.

4. PROBLEM STATEMENT

Traditional document processing often requires users to manually read documents, identify important information, find keywords, and prepare summaries. This process can become time-consuming when multiple documents or different document formats are involved.

Text extraction also differs depending on the file type. PDF, DOCX, and TXT files require different processing methods, while image-based documents require Optical Character Recognition (OCR).

Therefore, there is a need for a unified document analysis system that can accept multiple file formats and automatically extract useful information from uploaded documents.

The AI Document Analyzer addresses this problem by providing a single web-based platform for document upload, text extraction, OCR, keyword extraction, information extraction, summarization, search, and analysis export.

5. OBJECTIVES

The main objectives of the AI Document Analyzer are:

To develop a web-based document analysis application using Python and Flask.

To allow users to securely register and log in to the application.

To support multiple document formats including PDF, DOCX, TXT, JPG, JPEG, and PNG.

To automatically extract text from uploaded documents.

To perform OCR on image-based documents using Tesseract OCR.

To identify important keywords from extracted document text.

To extract structured information such as email addresses, phone numbers, and URLs.

To generate a concise summary from extracted document content.

To provide document search and filtering functionality.

To allow users to re-analyze and delete previously uploaded documents.

To provide TXT and PDF export options for analysis results.

To maintain user-specific document records using a database.

To test the application using both manual and automated testing methods.

6. EXISTING SYSTEM

In a traditional document processing workflow, users generally perform document analysis manually or use separate tools for different tasks.

For example, a user may need one application to open a PDF, another tool to perform OCR on an image, and additional tools to identify keywords or summarize the document.

The existing approach can have the following challenges:

Manual document reading requires significant time.

Different file formats may require different applications.

Image-based text requires separate OCR processing.

Important information may be difficult to identify manually.

Keyword identification is often performed manually.

Document summaries may need to be created manually.

Analysis results may need to be copied and organized separately.

Managing multiple uploaded documents can become difficult.

These limitations create a need for an integrated document analysis solution.

7. PROPOSED SYSTEM

The proposed AI Document Analyzer provides an integrated web-based platform for processing and analyzing multiple document formats.

Users can create an account and securely log in to the application. After authentication, users can upload supported documents through the web interface.

The system automatically identifies the uploaded file type and uses the appropriate extraction method.

For PDF files, text is extracted using PyMuPDF. DOCX files are processed using python-docx, while TXT files are processed using Python file handling. Image files are processed using Tesseract OCR with pytesseract and Pillow.

After text extraction, the system performs several analysis operations:

Keyword extraction

Structured information extraction

Document summarization

Extracted text display

The analyzed document is stored with the corresponding user account. Users can search their documents, re-analyze existing documents, delete documents, and export analysis results in TXT or PDF format.

The proposed system therefore combines multiple document processing tasks into a single application and provides a structured workflow for document analysis.

8. SYSTEM REQUIREMENTS

8.1 Hardware Requirements

The minimum hardware requirements for running the AI Document Analyzer locally are:

Processor: Intel Core i3 or equivalent

RAM: 4 GB minimum

Storage: At least 2 GB of available space

Display: Standard monitor

Keyboard and mouse

Internet connection for installing Python packages and project dependencies

For better performance when processing larger documents or images, higher RAM and processing power are recommended.

8.2 Software Requirements

The software requirements for the project are:

Operating System: Windows

Python: 3.11 or compatible version

Flask

Flask-SQLAlchemy

Flask-Login

SQLite

PyMuPDF

python-docx

pytesseract

Pillow

ReportLab

pytest

Tesseract OCR

Google Chrome or another modern web browser

Visual Studio Code or another Python-compatible code editor

9. TECHNOLOGIES USED

9.1 Python

Python is used as the primary programming language for the project. It handles the application logic, document processing, text extraction, OCR integration, keyword extraction, information extraction, and summarization.

9.2 Flask

Flask is used as the backend web framework. It manages application routes, HTTP requests, authentication, document processing workflows, and communication between the frontend and backend.

9.3 SQLite

SQLite is used as the database for storing application data. It stores user information and uploaded document records.

9.4 SQLAlchemy

SQLAlchemy is used as the Object Relational Mapper (ORM). It provides a Python-based interface for interacting with the SQLite database.

9.5 Flask-Login

Flask-Login is used to manage user authentication and login sessions. It also helps protect routes that require authenticated users.

9.6 PyMuPDF

PyMuPDF is used to extract text from PDF documents.

9.7 python-docx

python-docx is used to read and extract text from Microsoft Word DOCX documents.

9.8 Tesseract OCR

Tesseract OCR is used to recognize and extract text from image-based documents.

9.9 pytesseract

pytesseract provides the Python interface used to communicate with the Tesseract OCR engine.

9.10 Pillow

Pillow is used for image processing before OCR. The application performs operations such as resizing, grayscale conversion, contrast enhancement, and sharpening.

9.11 ReportLab

ReportLab is used to generate PDF files containing the document analysis results.

9.12 pytest

pytest is used to create and execute automated tests for selected application functionality.

9.13 HTML, CSS and Jinja2

HTML is used to structure the application's web pages. CSS is used for styling and layout. Jinja2 templates are used to dynamically display application data in Flask templates.

10. SYSTEM ARCHITECTURE

The AI Document Analyzer follows a modular web application architecture.

The main components are:

User Interface

Flask Application

Authentication Module

Document Management Module

Document Extraction Services

OCR Service

Analysis Services

Database

Analysis Export Functionality

10.1 Architecture Workflow

                         USER
                           |
                           v
                    Web Interface
                   HTML / CSS / Jinja2
                           |
                           v
                     Flask Backend
                           |
             +-------------+-------------+
             |                           |
             v                           v
      Authentication             Document Management
             |                           |
             |                           v
             |                    File Validation
             |                           |
             |                           v
             |                  Document Processing
             |                           |
             |              +------------+------------+
             |              |            |            |
             |              v            v            v
             |            PDF          DOCX          TXT
             |         Extraction    Extraction    Extraction
             |              |            |            |
             |              +------------+------------+
             |                           |
             |                           v
             |                      Image Files
             |                           |
             |                           v
             |                       OCR Service
             |                      Tesseract OCR
             |                           |
             +---------------------------+
                                         |
                                         v
                                  Extracted Text
                                         |
                            +------------+------------+
                            |            |            |
                            v            v            v
                         Keywords   Information   Summary
                        Extraction   Extraction   Generation
                            |            |            |
                            +------------+------------+
                                         |
                                         v
                                  Analysis Results
                                         |
                              +----------+----------+
                              |                     |
                              v                     v
                          SQLite DB          TXT / PDF Export

11. DATABASE DESIGN

The AI Document Analyzer uses SQLite as its database and SQLAlchemy as the Object Relational Mapper (ORM).

The database is designed to store user account information and document records.

11.1 Users Table

Field

Data Type

Description

id

Integer

Primary key for the user

username

String

Unique username

email

String

Unique user email address

password_hash

String

Hashed user password

created_at

DateTime

User account creation date

11.2 Documents Table

Field

Data Type

Description

id

Integer

Primary key for the document

filename

String

Original uploaded filename

filepath

String

Stored file path

extracted_text

Text

Text extracted from the document

uploaded_at

DateTime

Document upload date and time

user_id

Integer

Foreign key associated with the user

11.3 Relationship

The application uses a one-to-many relationship between Users and Documents.

One user can upload multiple documents, while each document belongs to one user.

Users
  |
  | 1
  |
  |--------------------<
                         |
                         | Many
                         |
                     Documents

12. MODULE DESCRIPTION

12.1 Authentication Module

The Authentication Module manages user registration, login, logout, password validation, and session management.

Main functions include:

User registration

Email format validation

Password confirmation

Duplicate username and email checking

Password hashing

User login

User logout

Protected routes using Flask-Login

Main file: app/routes/auth.py

12.2 Dashboard Module

The Dashboard provides the main authenticated area of the application and allows users to navigate to document management and other available features.

Main file: app/routes/dashboard.py

12.3 Document Management Module

The Document Management Module handles the document workflow:

Upload documents

Validate file extensions

Store uploaded files

Save document records

List uploaded documents

Search and filter documents

Analyze documents

Re-analyze existing documents

Delete documents

Export analysis results

Main file: app/routes/documents.py

12.4 Profile Module

The Profile Module displays user account information such as username, email address, and account creation date.

Main file: app/routes/profile.py

12.5 Text Extraction Module

The Text Extraction Module selects an extraction method based on the uploaded file type.

PDF text extraction using PyMuPDF

DOCX text extraction using python-docx

TXT file reading using Python

Image text extraction through the OCR service

Main file: app/services/text_extractor.py

12.6 OCR Module

The OCR Module extracts text from JPG, JPEG, and PNG image files using Tesseract OCR.

The image preprocessing workflow includes:

Opening the image

Converting the image to RGB

Resizing the image

Converting it to grayscale

Applying autocontrast

Enhancing contrast

Applying sharpening

Performing OCR using Tesseract

Main file: app/services/ocr_service.py

12.7 Keyword Extraction Module

The Keyword Extraction Module identifies frequently occurring meaningful words from extracted document text using regular expressions, stop-word filtering, and frequency counting.

Main file: app/services/keyword_extractor.py

12.8 Information Extraction Module

The Information Extraction Module identifies structured information from extracted text, including:

Email addresses

Phone numbers

URLs

Main file: app/services/information_extractor.py

12.9 Summarization Module

The Summarization Module generates a concise representation of extracted document content using the implemented text-processing logic.

Main file: app/services/summarizer.py

12.10 Export Functionality

The application allows users to export analysis results in TXT and PDF formats.

TXT reports contain document information, keywords, extracted information, summary, and extracted text. PDF reports are generated using ReportLab.

The export functionality is implemented in the document routes.

13. IMPLEMENTATION DETAILS

13.1 Application Factory

The Flask application is created using an application factory function named create_app().

The application initializes Flask configuration, SQLite database, SQLAlchemy, Flask-Login, user loading, application blueprints, template folders, and static folders.

The main implementation is located in app/__init__.py.

13.2 User Registration and Authentication

During registration, the system receives the username, email, password, and password confirmation.

The application validates the email format, checks that the password fields match, and verifies that the username and email are not already registered.

Passwords are stored as password hashes rather than plain-text passwords.

During login, the system checks the registered email and verifies the entered password against the stored password hash.

13.3 Document Upload Workflow

The document upload process follows these steps:

User logs in.

User opens the upload page.

User selects a supported file.

The application validates the file extension.

The file is stored on the server.

A document record is created in the SQLite database.

The system extracts text from the uploaded file.

Extracted text is stored in the document record.

The user can view the analysis results.

13.4 Document Analysis Workflow

Uploaded Document
       |
       v
File Type Detection
       |
       v
Text Extraction / OCR
       |
       v
Extracted Text
       |
       +---------> Keyword Extraction
       |
       +---------> Information Extraction
       |
       +---------> Summarization
       |
       v
Analysis Results

13.5 Search and Filtering

Users can search their uploaded documents using the document filename and extracted document text.

The search functionality helps users locate previously uploaded documents.

13.6 Re-analysis

When re-analysis is requested, the system checks whether the original stored file exists. It then extracts the content again and updates the stored extracted text.

13.7 Document Deletion

Users can delete uploaded documents through the document management interface. The application removes the stored document file when available and deletes the corresponding database record.

13.8 Analysis Export

Users can export analysis results as TXT or PDF files. The exported report contains:

Document filename

Upload date

Keywords

Structured information

Summary

Extracted text

14. TESTING AND RESULTS

The application was tested using both manual testing and automated testing.

14.1 Automated Testing

The project uses pytest for automated testing.

The automated test suite currently contains three tests covering:

TXT text extraction

Login page availability

Registration page availability

Test execution result:

3 passed in 1.07s

Therefore, all three automated tests passed successfully.

14.2 Manual Testing

Test Area

Result

User registration

Pass

Invalid email validation

Pass

Password mismatch validation

Pass

Duplicate username/email validation

Pass

User login

Pass

Invalid password handling

Pass

User logout

Pass

PDF upload

Pass

DOCX upload

Pass

TXT upload

Pass

JPG/PNG upload

Pass

PDF text extraction

Pass

DOCX text extraction

Pass

TXT text extraction

Pass

Image OCR

Pass

Keyword extraction

Pass

Information extraction

Pass

Summarization

Pass

Document search/filter

Pass

Clear search

Pass

Document analysis

Pass

Document re-analysis

Pass

Document deletion

Pass

TXT export

Pass

PDF export

Pass

Profile page

Pass

Invalid file type validation

Pass

No-file selection validation

Pass

14.3 Testing Conclusion

The tested application workflow successfully handled user authentication, document upload, document extraction, OCR, analysis, document management, profile access, and report export.

The automated test suite also completed successfully with 3 out of 3 tests passing.

15. LIMITATIONS

The current implementation has some limitations:

OCR accuracy can vary depending on image quality, font style, image resolution, and document layout.

The current OCR implementation is focused on image files such as JPG, JPEG, and PNG.

The summarization functionality uses implemented text-processing logic rather than a large language model.

The current application uses SQLite, which is suitable for local development and small-scale usage but may require a different database for larger production deployments.

Uploaded files are stored on the local server filesystem.

The application currently uses a local Tesseract OCR installation.

Automated testing currently covers selected functionality rather than every application route and service.

16. FUTURE ENHANCEMENTS

Possible future improvements include:

Add scanned-PDF OCR support.

Improve OCR preprocessing and recognition accuracy.

Add multilingual OCR support.

Improve summarization using advanced NLP or local language models.

Add document classification.

Add semantic document search.

Add duplicate document detection.

Add pagination for large document collections.

Add more comprehensive automated tests.

Replace local SQLite storage with a production database when required.

Add cloud-based file storage for production use.

Add role-based access control for multiple user types.

Improve deployment support for cloud platforms.

Add additional export formats if required.

17. CONCLUSION

The AI Document Analyzer demonstrates a complete web-based workflow for uploading, extracting, processing, analyzing, managing, and exporting information from multiple document formats.

The project integrates Python, Flask, SQLite, SQLAlchemy, PyMuPDF, python-docx, Tesseract OCR, pytesseract, Pillow, and ReportLab into a single application.

The system provides user authentication, multi-format document processing, OCR, keyword extraction, structured information extraction, summarization, search, re-analysis, deletion, profile management, and TXT/PDF export functionality.

Testing confirmed that the implemented application features worked as expected in the tested scenarios, and the automated test suite completed with 3 out of 3 tests passing.

The project provides a practical foundation for further development in document intelligence, natural language processing, OCR, and automated document analysis.

18. REFERENCES

Python Documentation — https://docs.python.org/

Flask Documentation — https://flask.palletsprojects.com/

Flask-SQLAlchemy Documentation — https://flask-sqlalchemy.palletsprojects.com/

Flask-Login Documentation — https://flask-login.readthedocs.io/

PyMuPDF Documentation — https://pymupdf.readthedocs.io/

python-docx Documentation — https://python-docx.readthedocs.io/

Tesseract OCR Documentation — https://tesseract-ocr.github.io/

pytesseract Documentation — https://pypi.org/project/pytesseract/

Pillow Documentation — https://pillow.readthedocs.io/

ReportLab Documentation — https://docs.reportlab.com/

pytest Documentation — https://docs.pytest.org/

PROJECT STATUS

Project: AI Document Analyzer
Status: Completed and tested
Automated Tests: 3/3 passed
Supported Input Formats: PDF, DOCX, TXT, JPG, JPEG, PNG
Export Formats: TXT, PDF
Database: SQLite
Backend: Flask
OCR: Tesseract OCR