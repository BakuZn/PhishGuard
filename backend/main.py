from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="PhishGuard API")

# VERY IMPORTANT: Allow Chrome extension to communicate with this local server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, change this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the data structure we expect from the extension
class EmailData(BaseModel):
    subject: str
    body: str

@app.post("/analyze")
async def analyze_email(email: EmailData):
    # TODO: Connect this to our Scikit-Learn ML model later!
    
    # For now, let's create a very basic placeholder logic
    text_to_analyze = (email.subject + " " + email.body).lower()
    
    # Simple hardcoded rules for our baseline test
    suspicious_words = ["urgent", "password", "bank", "account suspended", "click here"]
    
    is_phishing = any(word in text_to_analyze for word in suspicious_words)
    
    return {
        "status": "success",
        "is_phishing": is_phishing,
        "confidence": 0.85 if is_phishing else 0.99, # Dummy confidence scores
        "message": "Phishing attempt detected!" if is_phishing else "Looks safe."
    }

@app.get("/")
async def root():
    return {"message": "PhishGuard Backend is running!"}
