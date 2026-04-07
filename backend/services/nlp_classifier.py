import pickle
import os
from backend.config.settings import settings

class NLPClassifier:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.load_model()

    def load_model(self):
        if os.path.exists(settings.MODEL_PATH) and os.path.exists(settings.VECTORIZER_PATH):
            with open(settings.MODEL_PATH, "rb") as f:
                self.model = pickle.load(f)
            with open(settings.VECTORIZER_PATH, "rb") as f:
                self.vectorizer = pickle.load(f)
        else:
            print("Warning: Model or vectorizer not found. Please train the model first.")

    def preprocess(self, subject: str, body: str) -> str:
        return f"{subject} {body}"

    def predict(self, subject: str, body: str) -> str:
        if self.model is None or self.vectorizer is None:
            return "medium" # Fallback if model isn't loaded
            
        text = self.preprocess(subject, body)
        X = self.vectorizer.transform([text])
        prediction = self.model.predict(X)
        return prediction[0]

classifier = NLPClassifier()
