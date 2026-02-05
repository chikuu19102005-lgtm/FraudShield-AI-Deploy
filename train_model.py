import pandas as pd
import re
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# ---------- Load Dataset ----------
df = pd.read_csv("spam.csv", encoding="latin1")

# Keep only useful columns
df = df[["v1", "v2"]]
df.columns = ["label", "text"]

# Convert labels: spam = 1, ham = 0
df["label"] = df["label"].map({"spam": 1, "ham": 0})

# ---------- Clean Text ----------
def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"\d+", "", text)
    text = re.sub(r"[^\w\s]", "", text)
    return text

df["text"] = df["text"].apply(clean_text)

# ---------- Train/Test Split ----------
X_train, X_test, y_train, y_test = train_test_split(
    df["text"], df["label"], test_size=0.2, random_state=42
)

# ---------- Vectorization ----------
vectorizer = TfidfVectorizer(
    stop_words="english",
    ngram_range=(1,2),
    max_features=5000
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# ---------- Train Model ----------
model = LogisticRegression(
    class_weight="balanced",
    max_iter=1000
)
model.fit(X_train_vec, y_train)

# ---------- Evaluate ----------
y_pred = model.predict(X_test_vec)
accuracy = accuracy_score(y_test, y_pred)

print(f"✅ Training completed")
print(f"📊 Accuracy: {accuracy * 100:.2f}%")

# ---------- Save Model ----------
with open("model.pkl", "wb") as f:
    pickle.dump((vectorizer, model), f)

print("💾 Model saved as model.pkl")
