from presidio_analyzer import PatternRecognizer, Pattern

# =========================
# 🇮🇳 AADHAAR RECOGNIZER
# =========================
aadhaar_pattern = Pattern(
    name="aadhaar_pattern",
    regex=r"\b\d{4}\s?\d{4}\s?\d{4}\b",
    score=0.85
)

aadhaar_recognizer = PatternRecognizer(
    supported_entity="AADHAAR_NUMBER",
    patterns=[aadhaar_pattern]
)


# =========================
# 🇮🇳 PAN CARD RECOGNIZER
# =========================
pan_pattern = Pattern(
    name="pan_pattern",
    regex=r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
    score=0.85
)

pan_recognizer = PatternRecognizer(
    supported_entity="PAN_NUMBER",
    patterns=[pan_pattern]
)


# =========================
# 🇮🇳 INDIAN PHONE NUMBER
# =========================
phone_pattern = Pattern(
    name="indian_phone",
    regex=r"\b[6-9]\d{9}\b",
    score=0.80
)

phone_recognizer = PatternRecognizer(
    supported_entity="PHONE_NUMBER",
    patterns=[phone_pattern]
)


# =========================
# 🇮🇳 VOTER ID
# =========================
voter_pattern = Pattern(
    name="voter_pattern",
    regex=r"\b[A-Z]{3}[0-9]{7}\b",
    score=0.75
)

voter_recognizer = PatternRecognizer(
    supported_entity="VOTER_ID",
    patterns=[voter_pattern]
)


# =========================
# 🏦 BANK ACCOUNT (Simple)
# =========================
bank_pattern = Pattern(
    name="bank_account",
    regex=r"\b\d{9,18}\b",
    score=0.60
)

bank_recognizer = PatternRecognizer(
    supported_entity="BANK_ACCOUNT",
    patterns=[bank_pattern]
)


# =========================
# 📍 INDIAN LOCATIONS
# (Add more cities/states if needed)
# =========================
location_pattern = Pattern(
    name="indian_location",
    regex=r"\b(Bengaluru|Bangalore|Karnataka|Delhi|Mumbai|Chennai|Hyderabad|Pune|Kolkata)\b",
    score=0.75
)

location_recognizer = PatternRecognizer(
    supported_entity="LOCATION",
    patterns=[location_pattern]
)