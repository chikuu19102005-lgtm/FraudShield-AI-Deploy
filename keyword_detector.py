SCAM_KEYWORDS = [
    "otp", "kyc", "account", "bank", "upi",
    "urgent", "police", "refund", "lottery", "verification , kidnap"
]

def keyword_risk_score(text):
    score = 0
    detected = []

    for word in SCAM_KEYWORDS:
        if word in text.lower():
            score += 15
            detected.append(word)

    return min(score, 100), detected
