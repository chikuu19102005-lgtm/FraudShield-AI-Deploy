from fastapi import FastAPI, Header, HTTPException
import json

app = FastAPI(title="FraudShield API")

# ---------------- API KEY VERIFICATION ----------------
def verify_key(x_api_key: str):
    try:
        with open("keys.json", "r", encoding="utf-8") as f:
            keys = json.load(f)["valid_keys"]
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="keys.json not found")

    if x_api_key not in keys:
        raise HTTPException(status_code=401, detail="Invalid API Key")

# ---------------- API ENDPOINT ----------------
@app.post("/analyze")
def analyze(message: str, x_api_key: str = Header(...)):
    verify_key(x_api_key)

    # For now, just echo message
    # Later you can add scam detection + honeypot logic here
    return {
        "status": "authorized",
        "message": message
    }
@app.get("/")
def home():
    return {
        "status": "running",
        "message": "FraudShield API is live. Visit /docs"
    }

