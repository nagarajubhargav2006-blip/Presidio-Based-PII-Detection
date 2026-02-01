import pytest
import json
import os
from fastapi.testclient import TestClient
from presidio_analyzer import RecognizerResult
from main import app, clean_results

# Initialize the test client
client = TestClient(app)

# ==========================================
# 0. SETUP / TEARDOWN (Fixes 'index.html' error)
# ==========================================

@pytest.fixture(scope="module", autouse=True)
def setup_dummy_ui_file():
    """
    Creates a dummy 'index.html' file so test_serve_ui doesn't crash.
    Cleans it up after tests are done.
    """
    filename = "index.html"
    # Create file if it doesn't exist
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write("<html><body><h1>PII Detection Tool</h1></body></html>")
        created = True
    else:
        created = False
    
    yield  # Run tests
    
    # Cleanup
    if created and os.path.exists(filename):
        os.remove(filename)

# ==========================================
# 1. UNIT TESTS (Internal Logic)
# ==========================================

def test_clean_results_removes_overlaps():
    """Test that overlapping entities are filtered, keeping the one with higher score."""
    results = [
        RecognizerResult(entity_type="PHONE_NUMBER", start=0, end=10, score=0.95),
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

# ==========================================
# 2. INTEGRATION TESTS (API Endpoints)
# ==========================================

def test_serve_ui():
    """Verify the home route returns the HTML page."""
    response = client.get("/")
    assert response.status_code == 200
    assert "PII Detection Tool" in response.text

@pytest.mark.parametrize("pii_type, text, expected_entity", [
    ("Aadhaar", "My number is 5485 5000 8000", "AADHAAR_NUMBER"),
    ("PAN", "The PAN is ABCDE1234F", "PAN_NUMBER"),
    ("Phone", "Call me at 9876543210", "PHONE_NUMBER"),
    ("Email", "Email me at test@example.com", "EMAIL_ADDRESS"),
    ("UPI", "Pay via upi_user@okaxis", "UPI_ID")
])
def test_analyze_pii_detection(pii_type, text, expected_entity):
    """Test various PII types against the /analyze endpoint."""
    response = client.post("/analyze", json={"text": text, "threshold": 0.4})
    assert response.status_code == 200
    
    entities = response.json()["entities"]
    entity_types = [e["entity"] for e in entities]
    
    assert expected_entity in entity_types, f"Failed to detect {pii_type}"

def test_analyze_empty_text():
    """Ensure the API handles empty input gracefully."""
    response = client.post("/analyze", json={"text": "", "threshold": 0.6})
    assert response.status_code == 200
    assert response.json()["entities"] == []

# ==========================================
# 3. NEGATIVE TESTS
# ==========================================

def test_threshold_filtering():
    """
    Ensure entities with score lower than threshold are filtered out.
    """
    text = "Call 9876543210" # Usually scores ~0.7 to 0.95
    
    # 1. Test with low threshold (Should detect)
    resp_low = client.post("/analyze", json={"text": text, "threshold": 0.1})
    assert len(resp_low.json()["entities"]) > 0
    
    # 2. Test with MAX threshold (Should NOT detect)
    # Using 1.0 to ensure strict filtering
    resp_high = client.post("/analyze", json={"text": text, "threshold": 1.0})
    
    entities = resp_high.json()["entities"]
    assert len(entities) == 0, f"Expected 0 entities at threshold 1.0, but got: {entities}"

def test_invalid_pan_not_detected():
    """Ensure fake/malformed PANs aren't incorrectly flagged."""
    text = "This is NOTAPAN123." 
    response = client.post("/analyze", json={"text": text})
    entities = response.json()["entities"]
    
    pan_results = [e for e in entities if e["entity"] == "PAN_NUMBER"]
    assert len(pan_results) == 0

# ==========================================
# 4. LIVE DATA SIMULATION
# ==========================================

def load_live_data():
    file_path = os.path.join(os.path.dirname(__file__), "test_data.json")
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r") as f:
        return json.load(f)

@pytest.mark.skipif(not os.path.exists(os.path.join(os.path.dirname(__file__), "test_data.json")), 
                    reason="test_data.json not found")
@pytest.mark.parametrize("test_case", load_live_data())
def test_live_data_scenarios(test_case):
    text = test_case["text"]
    must_contain = test_case["must_contain"]
    
    response = client.post("/analyze", json={"text": text})
    assert response.status_code == 200
    
    detected = [e["entity"] for e in response.json()["entities"]]
    for item in must_contain:
        assert item in detected, f"Missing {item} in text: {text}"
