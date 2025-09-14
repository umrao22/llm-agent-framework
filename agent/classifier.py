import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

MODEL_PATH = "classifier.pkl"

class ToolClassifier:
    def __init__(self):
        self.vectorizer = None
        self.model = None

    def train(self, queries, labels):
        self.vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1,2))
        X = self.vectorizer.fit_transform(queries)

        self.model = LogisticRegression(max_iter=200)
        self.model.fit(X, labels)

        with open(MODEL_PATH, "wb") as f:
            pickle.dump((self.vectorizer, self.model), f)

    def load(self):
        if not os.path.exists(MODEL_PATH):
            return False
        with open(MODEL_PATH, "rb") as f:
            self.vectorizer, self.model = pickle.load(f)
        return True

    def predict_with_confidence(self, query, threshold=0.8):
        if not self.model or not self.vectorizer:
            raise ValueError("Model not trained or loaded.")
        X = self.vectorizer.transform([query])
        probs = self.model.predict_proba(X)[0]
        best_idx = probs.argmax()
        best_label = self.model.classes_[best_idx]
        confidence = probs[best_idx]

        if confidence >= threshold:
            return best_label, confidence
        return None, confidence


# Singleton
classifier = ToolClassifier()

def classify(query: str, threshold=0.8):
    if classifier.model is None:
        loaded = classifier.load()
        if not loaded:
            return None, 0.0
    return classifier.predict_with_confidence(query, threshold)
