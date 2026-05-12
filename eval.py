import pandas as pd
import asyncio
from backend.models.email import EmailPayload
from backend.services.risk_engine import analyze_email_risk

async def evaluate_system():
    # 1. Load dataset and sample 50 random emails to evaluate (to save time)
    df = pd.read_csv("Phishing_Email.csv").dropna(subset=["Email Text"]).sample(50, random_state=42)
    
    print(f"Evaluating {len(df)} emails concurrently...")

    tasks = []
    actual_labels = []
    
    for index, row in df.iterrows():
        payload = EmailPayload(
            sender="user@untrusted-domain.com", 
            subject="",
            body_text=str(row['Email Text']),
            body_html="",
            links=[]
        )
        tasks.append(analyze_email_risk(payload))
        actual_labels.append(row['Email Type'] == "Phishing Email")
        
    results = await asyncio.gather(*tasks)
    
    correct = 0
    false_positives = 0
    false_negatives = 0
    
    for result, actually_phish in zip(results, actual_labels):
        engine_says_phish = result.prediction != "SAFE"
        if engine_says_phish == actually_phish:
            correct += 1
        elif engine_says_phish and not actually_phish:
            false_positives += 1
        elif not engine_says_phish and actually_phish:
            false_negatives += 1

    total = len(df)
    accuracy = (correct / total) * 100
    print(f"Overall Accuracy: {accuracy:.2f}%")
    print(f"False Positives (Safe flagged as Phish): {false_positives}")
    print(f"False Negatives (Phish flagged as Safe): {false_negatives}")

if __name__ == "__main__":
    asyncio.run(evaluate_system())
