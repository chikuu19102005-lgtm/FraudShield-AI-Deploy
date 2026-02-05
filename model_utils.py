import pickle
import re

with open("model.pkl", "rb") as f:
    vectorizer, model = pickle.load(f)

SCAM_KEYWORDS = [
    "otp", "kyc", "account", "bank", "upi",
    "urgent", "police", "refund", "lottery",
    "verification", "kidnap"
]

def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"\d+", "", text)
    text = re.sub(r"[^\w\s]", "", text)
    return text

def keyword_risk_score(text):
    detected = [k for k in SCAM_KEYWORDS if k in text.lower()]
    score = min(len(set(detected)) * 15, 100)
    return score, detected

def ml_predict(text):
    text = clean_text(text)
    vec = vectorizer.transform([text])
    prob = model.predict_proba(vec)[0][1]
    return int(prob * 100)
FRAUD_FEATURES = {
    "Generic greeting": 10,
    "Fee before reward": 25,
    "Urgency pressure": 20,
    "Authority impersonation": 30
}
