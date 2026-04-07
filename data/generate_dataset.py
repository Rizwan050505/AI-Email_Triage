import json
import random
from datetime import datetime, timedelta

def generate_dataset(num_samples=200):
    dataset = []
    
    urgent_senders = ["boss@company.com", "ceo@company.com", "client@important.com"]
    normal_senders = ["team@company.com", "hr@company.com", "colleague@company.com"]
    spam_senders = ["spammer@fake.com", "newsletter@marketing.com", "offers@shop.com"]
    
    urgent_subjects = ["URGENT: Project Deadline", "Critical Server Outage", "Immediate Action Required", "Meeting tomorrow at 8am"]
    urgent_bodies = [
        "Please look at the attached documents immediately. We need this for tomorrow's presentation.",
        "The production server is completely down. Fix this ASAP.",
        "Your attendance is required at the board meeting right now.",
        "Client is very angry, please call them back immediately to resolve the issue."
    ]
    
    normal_subjects = ["Weekly Team Meeting", "Lunch tomorrow?", "Project Update", "Holiday Schedule"]
    normal_bodies = [
        "Just a reminder about our weekly sync today at 2 PM.",
        "Are we still on for lunch tomorrow?",
        "Here is the status update for this week's sprint. We are on track.",
        "Please note the upcoming holiday schedule for December."
    ]
    
    spam_subjects = ["You Won a Lottery!", "Claim your FREE gift", "Special Offer Just For You", "Enlarge your business"]
    spam_bodies = [
        "Congratulations! You have been selected to receive a $1000 gift card. Click here to claim.",
        "Only today! Buy one get one free. Don't miss out on this exclusive online offer.",
        "We are offering a special discount on our premium services. Reply to know more.",
        "Increase your ROI by 200%. Read our marketing guide."
    ]
    
    now = datetime.now()
    
    for i in range(num_samples):
        rand_val = random.random()
        if rand_val < 0.3:  # 30% urgent
            sender = random.choice(urgent_senders)
            subject = random.choice(urgent_subjects)
            body = random.choice(urgent_bodies)
            priority = "high"
        elif rand_val < 0.7:  # 40% normal
            sender = random.choice(normal_senders)
            subject = random.choice(normal_subjects)
            body = random.choice(normal_bodies)
            priority = "medium"
        else:  # 30% spam
            sender = random.choice(spam_senders)
            subject = random.choice(spam_subjects)
            body = random.choice(spam_bodies)
            priority = "low"
            
        timestamp = (now - timedelta(hours=random.randint(0, 100), minutes=random.randint(0, 60))).isoformat()
        
        # Add some noise
        if random.random() < 0.05 and priority == "high": # Make some boss emails look normal
            body = "See you tomorrow."
        if random.random() < 0.05 and priority == "low": # Make some spam look important
            subject = "URGENT Offer"

        dataset.append({
            "id": i + 1,
            "sender": sender,
            "subject": subject,
            "body": body,
            "timestamp": timestamp,
            "priority": priority
        })
        
    # Introduce an edge case for boss
    dataset.append({
         "id": num_samples + 1,
         "sender": "boss@company.com",
         "subject": "Lunch?",
         "body": "Do you want to grab lunch today?",
         "timestamp": now.isoformat(),
         "priority": "low" # Even though it's low, decision engine should forward because of sender
    })

    with open("data/dataset.json", "w") as f:
        json.dump(dataset, f, indent=4)
        
    print(f"Generated {len(dataset)} samples in data/dataset.json")

if __name__ == "__main__":
    import os
    os.makedirs("data", exist_ok=True)
    generate_dataset()
