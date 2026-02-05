import time
import random
import ollama

# ================= HUMAN-LIKE TYPING =================
def human_typing_delay(text):
    pass


# ================= CONFIDENCE SCORE =================
def compute_confidence(step, detected_keywords):
    return min(len(detected_keywords) * 15 + step * 5, 100)

# ================= AI-ONLY HONEYPOT =================
def honeypot_reply(
    message,
    detected_keywords,
    step,
    model_name="llama3",
    provider=None   # ignored
):
    confidence = compute_confidence(step, detected_keywords)

    prompt = f"""
You are an innocent human chatting with a stranger.

RULES:
- Never share OTP, PIN, UPI, passwords, or money
- Never pay any fee
- Never say you are an AI

Behavior:
- Be confused and cautious
- Ask questions
- Delay decisions
- Become skeptical under pressure

Confidence: {confidence}/100
Scammer message: "{message}"

Reply like a real human.
"""

    response = ollama.chat(
        model=model_name,
        messages=[{"role": "user", "content": prompt}]
    )

    reply = response["message"]["content"].strip()
    human_typing_delay(reply)
    return reply
