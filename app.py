import streamlit as st
import re
import csv
import os
import json
import random
from datetime import datetime
import pandas as pd

# =================================================
# =============== APP CONFIG ======================
# =================================================

st.set_page_config(
    page_title="FraudShield AI",
    page_icon="🚨",
    layout="centered"
)

# =================================================
# =============== DATABASE ========================
# =================================================

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
        json.dump(data, f, indent=2, ensure_ascii=False)

# =================================================
# =============== CONTINUOUS LEARNING =============
# =================================================

LOG_DIR = "learning_logs"
os.makedirs(LOG_DIR, exist_ok=True)

def save_chat_for_learning(chat_history):
    path = os.path.join(LOG_DIR, "honeypot_chats.csv")
    write_header = not os.path.exists(path)

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["role", "message"])
        for role, msg in chat_history:
            writer.writerow([role, msg])

# =================================================
# =============== KEYWORD ENGINE ==================
# =================================================

SCAM_KEYWORDS = {
    "upi": ["upi", "@upi", "paytm", "gpay", "phonepe"],
    "bank": ["account", "kyc", "ifsc", "atm", "debit", "credit"],
    "otp": ["otp", "one time password", "verification code"],
    "delivery": ["courier", "parcel", "delivery", "shipment"],
    "urgency": ["urgent", "immediately", "act now", "limited time"],
    "reward": ["winner", "lottery", "prize", "reward", "jackpot", "mega draw"],
    "job": ["job offer", "work from home", "easy money"],
    "link": ["http", "https", ".com", ".link"]
}

def keyword_risk_score(text):
    detected = set()
    for words in SCAM_KEYWORDS.values():
        for w in words:
            if w in text:
                detected.add(w)
    return len(detected), list(detected)

# =================================================
# =============== HONEYPOT REPLIES =================
# =================================================

RESPONSES = {
    0: [
        "Hello, I received your message. What is this about?",
        "Hi, can you explain this to me?",
        "Sorry, I didn’t understand this message.",
        "Why did you contact me?",
        "Can you tell me more about this?"
    ],
    1: [
        "I’m not very good with phones. What should I do?",
        "I’m a bit confused. Can you explain slowly?",
        "Why are you asking me for details?",
        "I don’t usually get messages like this."
    ],
    2: [
        "Is this safe to do?",
        "Why do I need to do this now?",
        "Are you sure this is official?",
        "This sounds suspicious."
    ],
    3: [
        "I’m not comfortable sharing my information.",
        "I think I should ask someone first.",
        "I will visit the bank instead.",
        "I don’t trust this."
    ],
    4: [
        "This looks like a scam.",
        "Do not contact me again.",
        "I will report this.",
        "You should stop scamming people."
    ]
}

def honeypot_reply(step):
    step = min(step, max(RESPONSES.keys()))
    return random.choice(RESPONSES[step])

# =================================================
# =============== SESSION STATE ===================
# =================================================

defaults = {
    "honeypot_active": False,
    "chat_history": [],
    "detected_words": [],
    "interaction_log": [],
    "fraud_stats": {
        "UPI IDs": 0,
        "Bank Mentions": 0,
        "Scam Links": 0,
        "Phone Numbers": 0
    }
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =================================================
# =============== HEADER ==========================
# =================================================

st.markdown("""
<h1 style='text-align:center;'>🚨 FraudShield AI</h1>
<h4 style='text-align:center;color:gray;'>
Silent Scam Detection + Honeypot System
</h4>
<hr>
""", unsafe_allow_html=True)

# =================================================
# =============== MESSAGE INPUT ===================
# =================================================

st.markdown("## 📩 Incoming Message")

message = st.text_area(
    "Paste the received SMS / WhatsApp / chat message",
    height=120
)

def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"\d+", "", text)
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()

# =================================================
# =============== DETECTION =======================
# =================================================

if st.button("🔍 Process Message") and message:
    st.session_state.pop("conversation_id", None)
    st.session_state.honeypot_active = False
    st.session_state.chat_history = []
    st.session_state.detected_words = []

    clean = clean_text(message)
    _, detected = keyword_risk_score(clean)

    if detected:
        st.session_state.honeypot_active = True
        st.session_state.detected_words = detected
        st.success(f"🚨 Scam keywords detected: {', '.join(detected)}")
    else:
        st.info("✅ No scam keywords detected. Message ignored.")

# =================================================
# =============== FRAUD INTELLIGENCE ==============
# =================================================

def extract_entities(text):
    return {
        "upi": re.findall(r'\b[\w.-]+@upi\b', text),
        "links": re.findall(r'https?://\S+', text),
        "phones": re.findall(r'\b\d{10}\b', text),
        "bank": re.findall(r'\baccount\b|\bkyc\b|\bifsc\b', text, re.IGNORECASE)
    }

# =================================================
# =============== HONEYPOT ========================
# =================================================

if st.session_state.honeypot_active:
    st.markdown("## 🤖 Honeypot Chatbot")
    scammer_msg = st.text_input("🧑‍💼 Scammer Message")

    if scammer_msg:
        step = len(st.session_state.chat_history)
        bot_reply = honeypot_reply(step)

        st.session_state.chat_history.extend([
            ("Scammer", scammer_msg),
            ("Victim Bot", bot_reply)
        ])

        db_entry = {
            "conversation_id": st.session_state.get(
                "conversation_id",
                datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            ),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "scammer_message": scammer_msg,
            "victim_reply": bot_reply,
            "detected_keywords": st.session_state.detected_words,
            "confidence_level": len(st.session_state.detected_words) * 15 + step * 5
        }

        st.session_state["conversation_id"] = db_entry["conversation_id"]
        save_to_db(db_entry)
        save_chat_for_learning(st.session_state.chat_history)

        st.session_state.interaction_log.append({
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Scammer": scammer_msg,
            "Bot": bot_reply
        })

        entities = extract_entities(" ".join([m for _, m in st.session_state.chat_history]))
        st.session_state.fraud_stats["UPI IDs"] += len(entities["upi"])
        st.session_state.fraud_stats["Scam Links"] += len(entities["links"])
        st.session_state.fraud_stats["Phone Numbers"] += len(entities["phones"])
        st.session_state.fraud_stats["Bank Mentions"] += len(entities["bank"])

    for role, msg in st.session_state.chat_history:
        st.markdown(f"**{role}:** {msg}")

# =================================================
# =============== DASHBOARD =======================
# =================================================

st.markdown("## 📊 Fraud Intelligence Dashboard")

c1, c2 = st.columns(2)
c3, c4 = st.columns(2)

c1.metric("💳 Fake UPI IDs", st.session_state.fraud_stats["UPI IDs"])
c2.metric("🏦 Bank Mentions", st.session_state.fraud_stats["Bank Mentions"])
c3.metric("🔗 Scam Links", st.session_state.fraud_stats["Scam Links"])
c4.metric("📞 Phone Numbers", st.session_state.fraud_stats["Phone Numbers"])

# =================================================
# =============== INTERACTION LOG =================
# =================================================

if st.session_state.interaction_log:
    st.markdown("## 🕘 Honeypot Interaction Log")
    df = pd.DataFrame(st.session_state.interaction_log)
    st.dataframe(df, use_container_width=True)

# =================================================
# =============== FOOTER ==========================
# =================================================

st.markdown("""
<hr>
<p style='text-align:center;color:gray;font-size:14px;'>
FraudShield AI | Keyword-Based Honeypot Scam Defense 🇮🇳
</p>
""", unsafe_allow_html=True)
