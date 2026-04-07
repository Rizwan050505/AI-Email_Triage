import json
import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from backend.config.settings import settings
from backend.database.database import SessionLocal
from backend.models.db_models import DBFeedback

def retrain_model():
    print("Fetching original dataset...")
    if not os.path.exists(settings.DATASET_PATH):
        raise FileNotFoundError("Original dataset not found. Please generate initially.")
        
    with open(settings.DATASET_PATH, 'r') as f:
        data = json.load(f)
        
    X_text = []
    y = []
    
    # Load base data
    for item in data:
        X_text.append(f"{item['subject']} {item['body']}")
        y.append(item['priority'])
        
    # Load feedback data
    print("Fetching feedback from database...")
    db = SessionLocal()
    feedbacks = db.query(DBFeedback).all()
    db.close()
    
    print(f"Found {len(feedbacks)} feedback records. Incorporating into dataset...")
    for fb in feedbacks:
        if fb.subject and fb.body: # Ensure we have text
            X_text.append(f"{fb.subject} {fb.body}")
            y.append(fb.correct_priority)
            
    # Retrain
    print("Retraining model...")
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
    X_vec = vectorizer.fit_transform(X_text)
    
    model = LogisticRegression(class_weight='balanced')
    model.fit(X_vec, y)
    
    # Save the models
    with open(settings.MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
        
    with open(settings.VECTORIZER_PATH, "wb") as f:
        pickle.dump(vectorizer, f)
        
    print(f"Retrained Model saved to {settings.MODEL_PATH}")
    print(f"Retrained Vectorizer saved to {settings.VECTORIZER_PATH}")

if __name__ == "__main__":
    retrain_model()
