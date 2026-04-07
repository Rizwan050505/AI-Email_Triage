import json
import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

class ChatbotTrainer:
    def __init__(self, data_path="chatbot/data/intents.json", model_dir="chatbot/models"):
        self.data_path = data_path
        self.model_dir = model_dir
        self.vectorizer = TfidfVectorizer(lowercase=True, stop_words='english')
        self.model = LogisticRegression(max_iter=200)
    
    def train(self):
        print(f"Loading chatbot intents from {self.data_path}...")
        with open(self.data_path, 'r') as f:
            data = json.load(f)
            
        X_train = []
        y_train = []
        
        # Parse intents and patterns
        for intent in data['intents']:
            for pattern in intent['patterns']:
                X_train.append(pattern)
                y_train.append(intent['tag'])
                
        print("Training NLP models for Chatbot Agent...")
        X_vec = self.vectorizer.fit_transform(X_train)
        self.model.fit(X_vec, y_train)
        
        os.makedirs(self.model_dir, exist_ok=True)
        
        with open(f"{self.model_dir}/vectorizer.pkl", "wb") as f:
            pickle.dump(self.vectorizer, f)
            
        with open(f"{self.model_dir}/intent_model.pkl", "wb") as f:
            pickle.dump(self.model, f)
            
        print("Chatbot NLP Training Complete! Models saved in chatbot/models/")

if __name__ == "__main__":
    import os
    # Ensure current directory context is correct
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    trainer = ChatbotTrainer()
    trainer.train()
