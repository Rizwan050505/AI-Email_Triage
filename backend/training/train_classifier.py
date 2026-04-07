import json
import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from backend.config.settings import settings

def train_model():
    print(f"Loading dataset from {settings.DATASET_PATH}")
    if not os.path.exists(settings.DATASET_PATH):
        raise FileNotFoundError(f"Dataset not found at {settings.DATASET_PATH}. Please generate it first.")

    with open(settings.DATASET_PATH, 'r') as f:
        data = json.load(f)
        
    X = []
    y = []
    for item in data:
        # Preprocess by combining subject and body
        X.append(f"{item['subject']} {item['body']}")
        y.append(item['priority'])
        
    print("Training TF-IDF Vectorizer and Logistic Regression...")
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
    X_vec = vectorizer.fit_transform(X)
    
    model = LogisticRegression(class_weight='balanced')
    model.fit(X_vec, y)
    
    # Save the models
    os.makedirs(os.path.dirname(settings.MODEL_PATH), exist_ok=True)
    
    with open(settings.MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
        
    with open(settings.VECTORIZER_PATH, "wb") as f:
        pickle.dump(vectorizer, f)
        
    print(f"Model saved to {settings.MODEL_PATH}")
    print(f"Vectorizer saved to {settings.VECTORIZER_PATH}")

if __name__ == "__main__":
    train_model()
