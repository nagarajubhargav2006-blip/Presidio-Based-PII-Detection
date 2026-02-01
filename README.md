# Presidio-Based-PII-Detection

A web-based application that detects, highlights, and masks **Personally Identifiable Information (PII)** from text and documents using **Microsoft Presidio** with custom Indian-specific recognizers.

This tool helps identify sensitive data such as Aadhaar numbers, PAN numbers, phone numbers, credit cards, emails, and locations before sharing or storing data.

---

## Overview

This application allows users to paste text or upload documents and automatically detect sensitive personal information.

Users can:
- Analyze text
- Highlight PII
- Mask sensitive values
- Restore original text
- Download results as JSON

The backend is powered by **FastAPI** and **Presidio**, and the frontend is built using **HTML, CSS, and JavaScript**.

---

## Key Features

- Detects PII such as:
  - Aadhaar Number
  - PAN Number
  - Phone Number
  - Credit Card Number
  - Email Address
  - Location
  - Voter ID
  - IBAN
- Highlights detected PII in text
- Masking and unmasking
- Adjustable confidence threshold
- Confidence score for each detected entity
- Supports file upload (TXT and PDF)
- Download detection results as JSON

---

## Supported File Types

This application supports **only** the following file formats:

- `.txt` — plain text files  
- `.pdf` — PDF documents  

Other file types (including JSON, Word, Excel, etc.) are **not supported** for text extraction.

---

## ⚠️ Known Limitations

### Drag and Drop
- Drag-and-drop upload is visible in the UI
- However, it is **not functional**
- Users must use the **“Choose File”** button to upload files

### File Type Support
- Only **TXT** and **PDF** files are supported
- JSON and other formats will not be processed

---

## Technology Stack

### Backend
- Python  
- FastAPI  
- Presidio Analyzer  
- Presidio Anonymizer  
- SpaCy  

### Frontend
- HTML  
- CSS  
- JavaScript  

---

## Application Flow

1. User pastes text or uploads a TXT or PDF file  
2. Text is extracted from the file  
3. User clicks **Analyze**  
4. Presidio detects PII  
5. Entities are highlighted  
6. User can **Mask** or **Unmask**  
7. Results can be downloaded as JSON  

---

## Positives of the Project

- Uses industry-grade PII detection (Presidio)  
- Supports Indian identifiers (Aadhaar, PAN, Voter ID)  
- Real-time highlighting and masking  
- Supports both text and PDF documents  
- Adjustable confidence level  
- Clean and modern UI  
- JSON export for further analysis  

---

## Negatives of the Project

- Drag-and-drop upload does not work  
- Only TXT and PDF files are supported  
- No database to store results  
- No user login or authentication  
- Not suitable for very large files  
- No real-time malware scanning  

---

## Future Initiatives

Planned improvements include:

- Enable full drag-and-drop file upload  
- Add support for more file types (Word, JSON, CSV)  
- Add user authentication  
- Store scan history in a database  
- Cloud storage integration  
- AI-based name and address recognition  
- Compliance reporting (GDPR, HIPAA)  
- API access for enterprise use  

---

## License

MIT License  

This project is intended for **academic, demo, and prototype use**.
