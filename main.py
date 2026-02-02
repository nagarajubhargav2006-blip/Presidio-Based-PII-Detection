from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import re

from presidio_analyzer import (
    AnalyzerEngine,
    PatternRecognizer,
    Pattern,
    RecognizerRegistry,
    EntityRecognizer,
    RecognizerResult
)
from presidio_analyzer.nlp_engine import NlpEngineProvider

app = FastAPI()

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (CSS & JS)
app.mount("/static", StaticFiles(directory="."), name="static")

# Serve index.html
@app.get("/")
def serve_ui():
    return FileResponse("index.html")

class TextRequest(BaseModel):
    text: str
    threshold: float = 0.6   # Default threshold if not provided

# ---------------- ANALYZER SETUP ---------------- #

registry = RecognizerRegistry()
registry.load_predefined_recognizers()

# REMOVE DEFAULT CREDIT CARD RECOGNIZER & OTHERS
# This ensures Presidio's default logic doesn't interfere
registry.recognizers = [
    r for r in registry.recognizers
    if "UK_NHS" not in r.supported_entities
    and "US_DRIVER_LICENSE" not in r.supported_entities
    and "CREDIT_CARD" not in r.supported_entities  # <--- Removes default detector
]

# Remove weak DATE recognizer
registry.recognizers = [
    r for r in registry.recognizers
    if "DATE_TIME" not in r.supported_entities
]

# Load spaCy NLP model
configuration = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "en", "model_name": "en_core_web_lg"}],
}

provider = NlpEngineProvider(nlp_configuration=configuration)
nlp_engine = provider.create_engine()

analyzer = AnalyzerEngine(registry=registry, nlp_engine=nlp_engine)

# ---------------- CUSTOM NAME RECOGNIZER (Fix for "Name:" Context) ---------------- #
class ContextNameRecognizer(EntityRecognizer):
    def __init__(self):
        super().__init__(supported_entities=["PERSON"], supported_language="en")

    def analyze(self, text, entities, nlp_artifacts=None):
        results = []
        # FIX: Changed [:\-] to [:] to strictly look for "Name: "
        # We also added \b to ensure we match whole words only.
        pattern = r"\b(?:name|full name)\s*[:]\s*([a-zA-Z]+(?:\s[a-zA-Z]+)*)"
        
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            start, end = match.span(1)
            results.append(
                RecognizerResult(
                    entity_type="PERSON",
                    start=start,
                    end=end,
                    score=1.0 
                )
            )
        return results

analyzer.registry.add_recognizer(ContextNameRecognizer())

# ---------------- PERSON NAME RECOGNIZER (SpaCy with Blacklist) ---------------- #
class SpacyPersonRecognizer(EntityRecognizer):
    def __init__(self):
        super().__init__(supported_entities=["PERSON"], supported_language="en")
        
        # 🛑 BLACKLIST: Words that are NOT people but SpaCy confuses for names
        self.deny_list = {
            "aadhaar", "uidai", "aadhar",
            "pan", "card", "pancard",
            "vote", "voter", "id", "epic",
            "license", "driving", "dl",
            "credit", "debit", "visa", "mastercard",
            "phone", "mobile", "number",
            "passport", "email", "address",
            "india", "state", "govt", "government",
            "name", "is", "proof" # Added "is" and "proof" just in case
        }

    def analyze(self, text, entities, nlp_artifacts=None):
        results = []
        if not nlp_artifacts:
            return results

        for ent in nlp_artifacts.entities:
            if ent.label_ == "PERSON":
                # Check if the word is in our blacklist (case-insensitive)
                if ent.text.lower() in self.deny_list:
                    continue  # SKIP IT!
                
                results.append(
                    RecognizerResult(
                        entity_type="PERSON",
                        start=ent.start_char,
                        end=ent.end_char,
                        score=0.9
                    )
                )
        return results

analyzer.registry.add_recognizer(SpacyPersonRecognizer())

# ---------------- CUSTOM INDIAN + EXTRA RECOGNIZERS ---------------- #

def add_pattern(name, regex, entity, score=0.95, context=None):
    pattern = Pattern(name=name, regex=regex, score=score)
    analyzer.registry.add_recognizer(
        PatternRecognizer(
            supported_entity=entity,
            patterns=[pattern],
            context=context or []
        )
    )

# Aadhaar (Strict 12-digit check)
# UPDATED: Changed [2-9] to [1-9] to allow your test data "1234..."
add_pattern(
    "aadhaar",
    r"(?<!\d)[1-9]\d{3}(?:\s?\d{4}){2}(?!\d)", 
    "AADHAAR_NUMBER",
    0.95,
    ["aadhaar", "uidai"]
)

# Credit Card (STRICT: Matches ONLY 16 digits. Ignores 13-digit Aadhaar errors)
add_pattern(
    "credit_card", 
    r"\b(?:\d[ -]*?){16}\b", 
    "CREDIT_CARD", 
    0.9, 
    ["card", "visa", "mastercard"]
)

# PAN
# STRICT: Changed back to {5} letters. Will ignore "ABC1234F".
add_pattern("pan", r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", "PAN_NUMBER", 1.0, ["pan"])

# Phone
add_pattern("phone", r"\b[6-9]\d{9}\b", "PHONE_NUMBER", 0.95, ["phone", "mobile"])

# Bank Account / IBAN
add_pattern("iban", r"\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b", "IBAN_CODE", 0.95, ["bank", "account", "iban"])

# --- UPDATED EMPLOYEE ID REGEX (Allows EMP5566 and EMP-5566) ---
add_pattern(
    "employee", 
    r"\b(?:EMP[-]?\d{4,6}|ORG[-]?\d{4,6})\b", 
    "EMPLOYEE_ID", 
    0.95, 
    ["employee", "emp id"]
)

# Voter ID
add_pattern("voter", r"\b[A-Z]{3}[0-9]{7}\b", "VOTER_ID", 0.95, ["voter"])

# Passport
add_pattern("passport", r"\b[A-Z][0-9]{7}\b", "PASSPORT_NUMBER", 0.9, ["passport"])

# Driving License
add_pattern("dl", r"\b[A-Z]{2}[0-9]{2}[0-9]{11}\b", "DRIVING_LICENSE", 0.9, ["dl", "license"])

# Vehicle Registration
add_pattern("vehicle", r"\b[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}\b", "VEHICLE_REGISTRATION", 0.95)

# PINCODE
add_pattern("pincode", r"\b[1-9][0-9]{5}\b", "PINCODE", 0.9)

# UPI
add_pattern("upi", r"\b[\w.-]+@[a-zA-Z]+\b", "UPI_ID", 0.85, ["upi"])

# ---------------- ADDRESS / LOCATION RECOGNIZER ---------------- #

class AddressRecognizer(EntityRecognizer):
    def __init__(self):
        super().__init__(supported_entities=["LOCATION"], supported_language="en")

    def analyze(self, text, entities, nlp_artifacts=None):
        results = []
        if not nlp_artifacts:
            return results

        for ent in nlp_artifacts.entities:
            if ent.label_ in ["GPE", "LOC"]: 
                results.append(
                    RecognizerResult(
                        entity_type="LOCATION",
                        start=ent.start_char,
                        end=ent.end_char,
                        score=0.85
                    )
                )
        return results

analyzer.registry.add_recognizer(AddressRecognizer())

# ---------------- REMOVE OVERLAPS ---------------- #

def clean_results(results):
    results = sorted(results, key=lambda r: (r.start, -(r.end - r.start), -r.score))
    filtered = []

    for r in results:
        keep = True
        for e in filtered:
            if not (r.end <= e.start or r.start >= e.end):
                if r.score <= e.score:
                    keep = False
                else:
                    filtered.remove(e)
                break
        if keep:
            filtered.append(r)

    return filtered

# -------- CUSTOM LOCATION RECOGNIZER --------
location_pattern = Pattern(
    name="indian_locations",
    regex=r"\b(Bangalore|Bengaluru|Mumbai|Delhi|Chennai|Hyderabad|Kolkata|Pune|Karnataka|Tamil Nadu|Maharashtra|India)\b",
    score=0.85,
)

location_recognizer = PatternRecognizer(
    supported_entity="LOCATION",
    patterns=[location_pattern],
)

registry.add_recognizer(location_recognizer)

# ---------------- API ROUTE ---------------- #

@app.post("/analyze")
async def analyze_text(request: TextRequest):
    results = analyzer.analyze(
        text=request.text,
        language="en"
    )

    # Filtering Logic
    results = [r for r in results if r.score >= request.threshold]

    results = clean_results(results)

    return {
        "entities": [
            {
                "entity": r.entity_type,
                "start": r.start,
                "end": r.end,
                "score": r.score
            }
            for r in results
        ]
    }
