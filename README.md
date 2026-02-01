# Presidio-Based-PII-Detection

A web-based application that detects, highlights, and masks **Personally Identifiable Information (PII)** from text and documents using **Microsoft Presidio** with custom Indian-specific recognizers.

This tool helps identify and protect sensitive data such as names, addresses, Aadhaar numbers, PAN numbers, phone numbers, credit cards, emails, and voter IDs before sharing or storing data.

---

## Overview

This application allows users to paste text or upload documents and automatically detect sensitive personal information.

Users can:
- Analyze text
- Highlight detected PII
- Mask sensitive values
- Restore original text
- Download detection results as JSON

The backend is powered by **FastAPI** and **Presidio**, and the frontend is built using **HTML, CSS, and JavaScript**.

---

## Key Features

- Detects PII such as:
  - Person Name  
  - Address / Location  
  - Aadhaar Number  
  - PAN Number  
  - Phone Number  
  - Credit Card Number  
  - Email Address  
  - Voter ID  
  - Bank / IBAN Numbers  
  - Employee ID  
- Highlights detected entities in different colors  
- Masks sensitive information  
- Unmask to restore original content  
- Adjustable detection confidence  
- Confidence score for each detection  
- Supports file upload (TXT and PDF)  
- Download detection results as JSON  

---

## Supported File Types

This application supports **only**:

- `.txt` — Plain text files  
- `.pdf` — PDF documents  

Other file types are not supported.

---

## ⚠️ Known Masking Behavior

The masking is applied differently for different PII types:

| Data Type | Masked Output |
|---------|---------------|
| Name | Shown as a **blank colored block** |
| Address (Location) | Replaced with **`[ADDRESS]`** |
| Email | Partially hidden (e.g., `rXXXX@gmail.com`) |
| Phone Number | Digits hidden except first & last |
| Aadhaar | Last 4 digits visible |
| PAN | Partial letters visible |
| Credit Card | Last 4 digits visible |
| Voter ID | Partial value visible |
| Bank / IBAN | Partial value visible |
| Employee ID | Shown as a **blank colored block** |

This behavior matches what is displayed in the UI.

---

## ⚠️ Known Limitations

### Drag and Drop
- Drag-and-drop upload is visible in the UI  
- However, it is **not functional**  
- Users must use the **“Choose File”** button  

### Name & Employee ID Mask Display
- Names and Employee IDs are masked  
- They appear as **empty colored blocks instead of XXXX**  
- This is a UI masking display limitation  

### Address Masking
- When a real address (e.g., *Bangalore, Karnataka*) is detected  
- It is replaced with **`[ADDRESS]`** in the masked output  

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
2. Text is extracted  
3. User clicks **Analyze**  
4. Presidio detects PII  
5. Entities are highlighted  
6. User clicks **Mask**  
7. Sensitive values are hidden  
8. User can **Unmask** or **Download JSON**  

---

## Positives of the Project

- Uses industry-grade PII detection (Presidio)  
- Supports Indian identifiers (Aadhaar, PAN, Voter ID)  
- Detects names, contact details, addresses, and financial data  
- Real-time highlighting and masking  
- Works with both text and PDF files  
- Adjustable confidence threshold  
- Clean and modern UI  
- JSON export for further analysis  

---

## Negatives of the Project

- Drag-and-drop upload does not work  
- Name and Employee ID appear as blank blocks  
- Only TXT and PDF files are supported  
- No user authentication  
- No scan history storage  
- No malware scanning  
- Not optimized for very large files  

---

## Future Initiatives

Planned improvements include:

- Enable full drag-and-drop file upload  
- Show masked values (XXXX) instead of blank blocks for Name and Employee ID  
- Improve address detection accuracy  
- Support more file formats (DOCX, CSV, etc.)  
- Add user login and roles  
- Store scan history in a database  
- Cloud storage integration  
- AI-based name and address recognition  
- Compliance reports (GDPR, HIPAA)  
- Enterprise REST API  

---

## License

MIT License  

This project is intended for **academic, demo, and prototype use**.
