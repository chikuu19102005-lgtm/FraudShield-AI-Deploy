from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import re
import os
import json

from model_utils import keyword_risk_score
from honeypot_bot import honeypot_reply

# ================= APP =================
app = FastAPI(title="FraudShield AI API")

# ================= DATABASE =================
DB_DIR = "database"
DB_FILE = os.path.join(DB_DIR, "honeypot_db.json")
os.makedirs(DB_DIR, exist_ok=True)

def load_db():
    if not os.path.exists(DB_FILE) or os.path.getsize(DB_FILE) == 0:
        return []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_to_db(entry):
    data = load_db()
    data.append(entry)
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# ================= INPUT SCHEMA =================
class MessageRequest(BaseModel):
    message: str

# ================= CLEAN TEXT =================
def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"\d+", "", text)
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()

# ================= API ENDPOINT =================
@app.post("/analyze")
def analyze_message(req: MessageRequest):
    clean = clean_text(req.message)
    score, detected = keyword_risk_score(clean)

    # If no scam words → return safe
    if not detected:
        return {
            "scam_detected": False,
            "message": "No scam keywords detected"
        }

    # Honeypot reply
    reply = honeypot_reply(
        req.message,
        detected_keywords=detected,
        step=0,
        model_name="phi3:mini"
    )

    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "scammer_message": req.message,
        "victim_reply": reply,
        "detected_keywords": detected
    }

    save_to_db(record)

    return {
        "scam_detected": True,
        "detected_keywords": detected,
        "honeypot_reply": reply
    }
