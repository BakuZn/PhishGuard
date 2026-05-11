from transformers import pipeline
import os

print("⏳ Loading pre-trained Phishing BERT model (this may take a minute on first run)...")
try:
    # We use a lightweight fine-tuned BERT model for phishing/spam detection
    model_name = "ealvaradob/bert-finetuned-phishing"
    classifier = pipeline("text-classification", model=model_name, return_all_scores=False)
    print("✅ BERT Model loaded successfully!")
except Exception as e:
    print(f"❌ Failed to load BERT Model: {e}")
    classifier = None

def predict_email(text: str) -> dict:
    """
    Runs text through the BERT pipeline.
    The model returns LABEL_1 for phishing/spam and LABEL_0 for safe.
    """
    if not classifier:
        return {"is_phishing": False, "confidence": 0.0, "message": "Model not loaded"}
        
    if len(text.strip()) < 10:
        return {"is_phishing": False, "confidence": 1.0, "message": "Email too short to analyze"}

    # BERT has a maximum sequence length (usually 512 tokens). 
    # We truncate the string to roughly fit within that limit to avoid errors.
    truncated_text = text[:1500] 

    try:
        result = classifier(truncated_text)[0]
        label = result['label']
        score = result['score']
        
        # ealvaradob/bert-finetuned-phishing maps to 'phishing' or 'safe'
        is_phish = (label.lower() == "phishing" or label == "LABEL_1")
        
        return {
            "is_phishing": is_phish,
            "confidence": round(float(score), 4)
        }
    except Exception as e:
        print(f"Prediction Error: {e}")
        return {"is_phishing": False, "confidence": 0.0, "message": "Error during prediction"}

