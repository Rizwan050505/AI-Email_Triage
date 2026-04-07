class DecisionEngine:
    @staticmethod
    def decide(predicted_priority: str, sender: str, timestamp: str) -> str:
        """
        Rules:
        * High priority → forward
        * Medium → reply
        * Low → archive
        * If sender is "boss", always forward
        """
        sender_lower = sender.lower()
        if "boss" in sender_lower or "ceo" in sender_lower: # capturing both boss/ceo to be safe for generated data
            return "forward"
            
        if predicted_priority == "high":
            return "forward"
        elif predicted_priority == "medium":
            return "reply"
        else:
            return "archive"

decision_engine = DecisionEngine()
