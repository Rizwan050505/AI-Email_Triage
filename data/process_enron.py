import csv
import json
import re
import os
import sys

# Increase CSV parser limit for massive files
csv.field_size_limit(sys.maxsize)

INPUT_CSV = os.path.abspath("archive/emails.csv")
OUTPUT_JSON = os.path.abspath("data/dataset.json")
TARGET_COUNT = 5000

def process_emails():
    if not os.path.exists(INPUT_CSV):
        print(f"Error: {INPUT_CSV} not found.")
        return
        
    extracted_data = []
    
    print(f"Starting to process emails from {INPUT_CSV}...")
    
    with open(INPUT_CSV, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        
        try:
            # Skip header row
            next(reader)
        except StopIteration:
            print("Empty file")
            return

        for row in reader:
            if len(row) < 2:
                continue
                
            message = row[1]
            
            # Extract headers and body
            # Headers and body are separated by the first empty line.
            sections = message.split("\n\n", 1)
            
            if len(sections) < 2:
                continue
                
            header_text = sections[0]
            raw_body = sections[1]
            
            sender = ""
            subject = ""
            date_str = ""
            
            # Basic parsing across headers
            for line in header_text.split("\n"):
                if line.startswith("From: "):
                    sender = line[6:].strip()
                elif line.startswith("Subject: "):
                    subject = line[9:].strip()
                elif line.startswith("Date: "):
                    date_str = line[6:].strip()
            
            # Clean body
            body = re.sub(r'\s+', ' ', raw_body).strip()
            
            # Skip empty emails or those missing a sender
            if not body or not sender:
                continue
                
            # Limit body length
            body = body[:2000]
            
            # Apply labeling logic
            combined_text = (subject + " " + body).lower()
            
            if "urgent" in combined_text or "asap" in combined_text:
                priority = "high"
                action = "escalate"
            elif "invoice" in combined_text or "payment" in combined_text:
                priority = "high"
                action = "reply"
            elif "meeting" in combined_text:
                priority = "medium"
                action = "notify"
            else:
                priority = "low"
                action = "ignore"
                
            email_record = {
                "id": str(len(extracted_data) + 1),
                "sender": sender,
                "subject": subject,
                "body": body,
                "timestamp": date_str,
                "priority": priority,
                "action": action
            }
            
            extracted_data.append(email_record)
            
            if len(extracted_data) >= TARGET_COUNT:
                break
                
    # Save as JSON
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as out_f:
        json.dump(extracted_data, out_f, indent=2)
        
    print(f"Successfully processed and saved {len(extracted_data)} emails to {OUTPUT_JSON}")

if __name__ == '__main__':
    process_emails()
