import time
import random

# ================= HUMAN-LIKE TYPING =================
def human_typing_delay(text):
    """
    Simulates human typing delay based on message length
    """
    delay = min(len(text) * 0.03, 2.5)  # max 2.5 seconds
    time.sleep(delay)


# ================= CONFIDENCE SCORE =================
def compute_confidence(step, detected_keywords):
    """
    Confidence increases with scam pressure and conversation steps
    """
    return min(len(detected_keywords) * 15 + step * 5, 100)


# ================= RULE-BASED HONEYPOT REPLIES =================
RESPONSES = {
    0: [  # Curious / innocent
        "Hello, I just saw your message. What is this about?",
        "Hi, can you explain this to me?",
        "Sorry, I don’t really understand what you mean.",
        "I’m not sure why I received this message.",
        "Can you tell me more about this?"
    ],
    1: [  # Confused
        "I’m not very good with phones. What should I do?",
        "I’m a bit confused. Can you explain slowly?",
        "Why do I need to do this?",
        "I don’t usually get messages like this.",
        "Can you explain step by step?"
    ],
    2: [  # Skeptical
        "Is this really safe?",
        "Why is this so urgent?",
        "Are you sure this is official?",
        "This sounds a little strange to me.",
        "How do I know this is not a scam?"
    ],
    3: [  # Defensive
        "I don’t feel comfortable sharing details.",
        "I think I should ask someone first.",
        "I’m worried about giving information.",
        "Can I do this later?",
        "I’m not convinced this is real."
    ],
    4: [  # Rejecting / aware
        "I don’t trust this.",
        "I’m not going to continue this conversation.",
        "I will visit the bank instead.",
        "Please stop messaging me.",
        "I think this is a scam."
    ]
}


# ================= KEYWORD SENSITIVITY =================
KEYWORD_TRIGGERS = {
    "otp": ["otp", "verification code", "one time password"],
    "money": ["pay", "fee", "charge", "amount", "transfer"],
    "urgency": ["urgent", "immediately", "act now"],
    "bank": ["bank", "account", "kyc", "ifsc"],
    "upi": ["upi", "paytm", "gpay", "phonepe"],
}


def keyword_pressure_boost(message, step):
    """
    Increases step faster if scammer uses dangerous keywords
    """
    msg = message.lower()
    for words in KEYWORD_TRIGGERS.values():
        for w in words:
            if w in msg:
                return min(step + 1, 4)
    return step


# ================= FINAL HONEYPOT FUNCTION =================
def honeypot_reply(
    message,
    detected_keywords,
    step,
    model_name=None,
    provider=None
):
    """
    Pure rule-based innocent honeypot reply
    AI-free, deterministic, safe
    """

    # Adjust step based on scam pressure
    step = keyword_pressure_boost(message, step)
    step = min(step, max(RESPONSES.keys()))

    # Generate reply
    reply = random.choice(RESPONSES[step])

    # Simulate human typing
    human_typing_delay(reply)

    return reply
