from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

texts = [
    "share otp immediately",
    "your account is blocked",
    "hello how are you",
    "meeting at 5 pm"
]
labels = [1, 1, 0, 0]  # 1 = Scam, 0 = Normal

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)

model = LogisticRegression()
model.fit(X, labels)

def ml_predict(text):
    vec = vectorizer.transform([text])
    prob = model.predict_proba(vec)[0][1]
    return int(prob * 100)
