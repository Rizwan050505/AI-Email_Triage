import json
import os
import random
from typing import Optional, List, Tuple, Dict, Any
from pydantic import BaseModel

class EmailModel(BaseModel):
    id: int
    sender: str
    subject: str
    body: str
    timestamp: str

class Observation(BaseModel):
    task_id: str
    current_email: Optional[EmailModel]
    emails_remaining: int
    history_so_far: int

class Action(BaseModel):
    predicted_priority: str  # low, normal, high (or mapping to the dataset categories)
    predicted_action: Optional[str] = None # e.g. "ignore", "auto-reply", "escalate"
    drafted_response: Optional[str] = None

class Reward(BaseModel):
    step_reward: float
    total_reward: float
    message: str

class EmailTriageEnv:
    def __init__(self, dataset_path: str = "data/dataset.json"):
        self.dataset_path = dataset_path
        self.dataset: List[Dict[str, Any]] = []
        self.load_dataset()
        self.current_task = None
        self.current_index = 0
        self.emails_to_process: List[Dict[str, Any]] = []
        self.total_reward_val = 0.0
        
    def load_dataset(self):
        if os.path.exists(self.dataset_path):
            with open(self.dataset_path, "r") as f:
                self.dataset = json.load(f)
        else:
            self.dataset = [
                {"id": 1, "sender": "boss@company.com", "subject": "Urgent Request", "body": "Need this done ASAP.", "timestamp": "2023-01-01T09:00:00Z", "priority": "high", "action": "escalate"},
                {"id": 2, "sender": "newsletter@spam.com", "subject": "Weekly Update", "body": "Here is what happened...", "timestamp": "2023-01-01T10:00:00Z", "priority": "low", "action": "ignore"},
                {"id": 3, "sender": "client@domain.com", "subject": "Question about product", "body": "How do I do X?", "timestamp": "2023-01-01T11:00:00Z", "priority": "normal", "action": "auto-reply"}
            ]

    def reset(self, task_id: str = "email-triage-easy") -> Observation:
        self.current_task = task_id
        self.total_reward_val = 0.0
        
        # Select a mixed subset of emails for the episode
        random.seed(42)  # for reproducibility on tasks
        sample_size = min(5, len(self.dataset))
        self.emails_to_process = random.sample(self.dataset, sample_size)
        self.current_index = 0
        
        return self.state()

    def state(self) -> Observation:
        if self.current_index < len(self.emails_to_process):
            raw_email = self.emails_to_process[self.current_index]
            current_email = EmailModel(
                id=raw_email.get("id", 0),
                sender=raw_email.get("sender", ""),
                subject=raw_email.get("subject", ""),
                body=raw_email.get("body", ""),
                timestamp=raw_email.get("timestamp", "")
            )
        else:
            current_email = None
            
        return Observation(
            task_id=self.current_task,
            current_email=current_email,
            emails_remaining=len(self.emails_to_process) - self.current_index,
            history_so_far=self.current_index
        )
        
    def step(self, action: Action) -> Tuple[Observation, Reward, bool, Dict[str, Any]]:
        raw_email = self.emails_to_process[self.current_index]
        
        # Rely solely on the extracted attributes from the dataset, removing hardcoded logic strings.
        true_priority = raw_email.get("priority", "low") 
        true_action = raw_email.get("action", "ignore")

        step_reward = 0.0
        message = ""
        
        if self.current_task == "email-triage-easy":
            if action.predicted_priority.lower() == true_priority.lower():
                step_reward = 1.0
                message = "Correct priority."
            else:
                step_reward = 0.0
                message = f"Incorrect priority. Expected {true_priority}."
                
        elif self.current_task == "email-triage-medium":
            score = 0.0
            if action.predicted_priority.lower() == true_priority.lower(): 
                score += 0.5
            else:
                score -= 0.1 # Penalty for hallucination
                
            action_pred = action.predicted_action.lower() if action.predicted_action else ""
            if action_pred == true_action.lower(): 
                score += 0.5
            else:
                score -= 0.1 # Penalty for hallucination
                
            step_reward = max(0.0, score) # Ensure non-negative bounds unless critical failure
            message = "Medium task graded with strict penalties."
            
        elif self.current_task == "email-triage-hard":
            score = 0.0
            if action.predicted_priority.lower() == true_priority.lower(): score += 0.33
            action_pred = action.predicted_action.lower() if action.predicted_action else ""
            if action_pred == true_action.lower(): score += 0.33
            
            if action_pred == "auto-reply":
                if action.drafted_response and len(action.drafted_response) > 10:
                    score += 0.34
            else:
                score += 0.34 # no response needed, but got points for correct action
                
            step_reward = score
            message = "Hard task graded."
            
        # Scale step_reward into bounded range to ensure total task score is within strictly (0, 1)
        n_emails = len(self.emails_to_process)
        if n_emails > 0:
            step_reward = (step_reward * 0.98 / n_emails) + (0.01 / n_emails)

        self.total_reward_val += step_reward
        self.current_index += 1
        done = (self.current_index >= len(self.emails_to_process))
        
        obs = self.state()
        reward = Reward(step_reward=step_reward, total_reward=self.total_reward_val, message=message)
        
        info = {
            "true_priority": true_priority,
            "true_action": true_action
        }
        
        return obs, reward, done, info

    def close(self):
        pass
