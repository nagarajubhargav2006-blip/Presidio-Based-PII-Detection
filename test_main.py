import pytest
from fastapi.testclient import TestClient
from main import app, clean_results
from presidio_analyzer import RecognizerResult

client = TestClient(app)

# --- 1. Unit Tests for clean_results logic ---

def test_clean_results_removes_overlaps():
    """Test that overlapping entities are filtered, keeping the one with higher score."""
    results = [
        RecognizerResult(entity_type="PHONE_NUMBER", start=0, end=10, score=0.95),
        # This overlaps with the phone number but has a lower score
        RecognizerResult(entity_type="PINCODE", start=5, end=11, score=0.4) 
    ]
    cleaned = clean_results(results)
    assert len(cleaned) == 1
    assert cleaned[0].entity_type == "PHONE_NUMBER"

def test_clean_results_keeps_longer_match():
    """Test that longer matches are prioritized if scores are equal."""
    results = [
        RecognizerResult(entity_type="SHORT", start=0, end=5, score=0.9),
        RecognizerResult(entity_type="LONG", start=0, end=10, score=0.9)
    ]
    cleaned = clean_results(results)
    assert len(cleaned) == 1
    assert cleaned[0].entity_type == "LONG"


# --- 2. Integration Tests for API Endpoints ---

def test_serve_ui():
    """Verify the home route returns the HTML page."""
    response = client.get("/")
    assert response.status_code == 200
    assert "PII Detection Tool" in response.text

@pytest.mark.parametrize("pii_type, text, expected_entity", [
    ("Aadhaar", "My number is 2345 6789 1234", "AADHAAR_NUMBER"),
    ("PAN", "The PAN is ABCDE1234F", "PAN_NUMBER"),
    ("Phone", "Call me at 9876543210", "PHONE_NUMBER"),
    ("VoterID", "Voter ID: ZYX1234567", "VOTER_ID"),
    ("Email", "Email me at test@example.com", "EMAIL_ADDRESS"),
    ("UPI", "Pay via upi_user@okaxis", "UPI_ID")
])
def test_analyze_pii_detection(pii_type, text, expected_entity):
    """Test various PII types against the /analyze endpoint."""
    response = client.post("/analyze", json={"text": text, "threshold": 0.6})
    assert response.status_code == 200
    
    entities = response.json()["entities"]
    entity_types = [e["entity"] for e in entities]
    
    assert expected_entity in entity_types, f"Failed to detect {pii_type}"

def test_analyze_empty_text():
    """Ensure the API handles empty input gracefully."""
    response = client.post("/analyze", json={"text": "", "threshold": 0.6})
    assert response.status_code == 200
    assert response.json()["entities"] == []

def test_location_detection():
    """Test if major Indian cities are recognized as LOCATION."""
    text = "I live in Bangalore, Karnataka."
    response = client.post("/analyze", json={"text": text})
    entities = response.json()["entities"]
    
    location_entities = [e for e in entities if e["entity"] == "LOCATION"]
    assert len(location_entities) >= 1


# --- 3. Negative Tests ---

def test_invalid_pan_not_detected():
    """Ensure fake/malformed PANs aren't incorrectly flagged with high scores."""
    # PAN must be 5 letters, 4 digits, 1 letter
    text = "This is NOTAPAN123." 
    response = client.post("/analyze", json={"text": text})
    entities = response.json()["entities"]
    
    pan_results = [e for e in entities if e["entity"] == "PAN_NUMBER"]
    assert len(pan_results) == 0