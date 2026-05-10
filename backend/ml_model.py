import joblib
import os

# Load the trained model when this module is imported
model_path = os.path.join(os.path.dirname(__file__), 'phishguard_model.joblib')
try:
    model = joblib.load(model_path)
    print("✅ ML Model loaded successfully!")
except Exception as e:
    print(f"❌ Failed to load ML Model: {e}")
    model = None

def predict_email(text: str):
    if not model:
        return {"is_phishing": False, "confidence": 0.0, "message": "Model not loaded"}
        
    # Prevent empty or very short strings from defaulting to phishing 
    # (the model's intercept is positive, so 0 features = ~73% phishing)
    if len(text.strip()) < 10:
        return {"is_phishing": False, "confidence": 1.0, "message": "Email too short to analyze"}

    prediction = model.predict([text])[0]
    probabilities = model.predict_proba([text])[0]
    confidence = probabilities[prediction]
    
    return {
        "is_phishing": bool(prediction == 1),
        "confidence": round(float(confidence), 4)
    }
