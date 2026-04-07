import pickle
import json
import random
import os

class NLPChatbotAgent:
    def __init__(self, model_dir="chatbot/models", data_path="chatbot/data/intents.json"):
        self.vectorizer = None
        self.model = None
        self.intents_data = None
        
        # Load NLP models and intents
        try:
            with open(f"{model_dir}/vectorizer.pkl", "rb") as f:
                self.vectorizer = pickle.load(f)
            with open(f"{model_dir}/intent_model.pkl", "rb") as f:
                self.model = pickle.load(f)
            with open(data_path, "r") as f:
                self.intents_data = json.load(f)
        except Exception as e:
            print(f"Warning: Chatbot models not loaded. Please run 'python chatbot/train.py' first. Error: {e}")

    def predict_intent(self, text: str) -> str:
        """Predicts the intent tag of the user's input."""
        if not self.model or not self.vectorizer:
            return "unknown"
            
        X = self.vectorizer.transform([text])
        prediction = self.model.predict(X)[0]
        
        # Calculate confidence using probability
        prob = self.model.predict_proba(X).max()
        if prob < 0.2: # Low confidence threshold fallback
            return "unknown"
            
        return prediction

    def get_response(self, text: str, context: dict = None) -> str:
        """Takes user input and returns an NLP-driven agent response."""
        intent = self.predict_intent(text)
        
        if intent == "unknown":
            return "I am not quite sure I understand. I operate primarily as an Email AI Agent. You can ask me to summarize, draft replies, or query your inbox."
            
        # Retrieve random matched response from intents JSON
        for i in self.intents_data['intents']:
            if i['tag'] == intent:
                response = random.choice(i['responses'])
                
                # Context-aware logic can be injected here based on the intent
                if intent == "summarize" and context and 'email_body' in context:
                    # In a bigger system, integrate an LLM or extractive summarizer. For now, simulated rule:
                    response += f"\n\n**Brief Summary**: The email from {context.get('sender', 'Unknown')} is about: '{context.get('subject', '')}'. Length: {len(context['email_body'])} chars."
                elif intent == "query_inbox":
                    response += "\n\n(Agent Action: Searching SQLite database for emails tagged with 'high' priority...)"
                    
                return response
                
        return "Sorry, I ran into an error generating a response."

# Test the agent interactively if run directly
if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    agent = NLPChatbotAgent()
    print("AI Chatbot Agent initialized! Type 'quit' to exit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit']:
            break
            
        # Mocking context for testing
        mock_context = {
            "sender": "boss@company.com", 
            "subject": "Project Requirements", 
            "email_body": "We need the new specs by tomorrow 9am."
        }
        
        bot_response = agent.get_response(user_input, context=mock_context)
        print(f"Agent: {bot_response}\n")
