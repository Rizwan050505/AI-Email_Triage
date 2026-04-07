import json
from typing import List, Dict, Any, Tuple
from backend.services.nlp_classifier import classifier
from backend.services.decision_engine import decision_engine

class EmailEnv:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.inbox: List[Dict[str, Any]] = []
        self.processed_emails: List[Dict[str, Any]] = []
        self.current_index = 0
        self.reset()
        
    def reset(self):
        try:
            with open(self.data_path, "r") as f:
                self.inbox = json.load(f)
        except FileNotFoundError:
            self.inbox = []
        self.processed_emails = []
        self.current_index = 0
        return self.state()
        
    def state(self):
        if self.current_index < len(self.inbox):
            return self.inbox[self.current_index]
        return None

    def step(self, action: str) -> Tuple[Dict[str, Any], float, bool]:
        """
        Reward system:
        +2 correct action
        +1 correct classification
        -1 wrong action
        -2 ignoring high priority
        """
        if self.current_index >= len(self.inbox):
            return None, 0.0, True
            
        current_email = self.inbox[self.current_index]
        true_priority = current_email['priority']
        
        # Determine the target correct action for reward calculation
        # The true optimal policy given the ground truth
        correct_action = decision_engine.decide(true_priority, current_email['sender'], current_email['timestamp'])
        
        # Predict priority to calculate if classification was right
        predicted_priority = classifier.predict(current_email['subject'], current_email['body'])
        
        reward = 0.0
        
        if action == correct_action:
            reward += 2.0
        else:
            reward -= 1.0
            
        if predicted_priority == true_priority:
            reward += 1.0
            
        if true_priority == "high" and action != "forward": # Interpreting ignoring as not forwarding
            reward -= 2.0
            
        self.processed_emails.append({
            "email_id": current_email['id'],
            "action_taken": action,
            "reward": reward
        })
        
        self.current_index += 1
        done = self.current_index >= len(self.inbox)
        next_state = self.state()
        
        return next_state, reward, done
