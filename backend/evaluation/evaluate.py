import json
import os
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from backend.services.nlp_classifier import NLPClassifier
from backend.config.settings import settings

def evaluate():
    classifier = NLPClassifier()
    if classifier.model is None or classifier.vectorizer is None:
        print("Model not loaded. Ensure training script has run.")
        return
        
    if not os.path.exists(settings.DATASET_PATH):
        print("Dataset not found.")
        return
        
    with open(settings.DATASET_PATH, 'r') as f:
        data = json.load(f)
        
    y_true = []
    y_pred = []
    
    print("Evaluating model...")
    for item in data:
        y_true.append(item['priority'])
        y_pred.append(classifier.predict(item['subject'], item['body']))
        
    accuracy = accuracy_score(y_true, y_pred)
    # Using macro to average metrics across the classes equally since we have high/medium/low
    precision = precision_score(y_true, y_pred, average='macro', zero_division=0)
    recall = recall_score(y_true, y_pred, average='macro', zero_division=0)
    f1 = f1_score(y_true, y_pred, average='macro', zero_division=0)
    
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")

if __name__ == "__main__":
    evaluate()
