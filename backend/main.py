from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.ml_model import predict_email

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
    text_to_analyze = (email.subject + " " + email.body).lower()
    
    # Run the text through Scikit-Learn
    result = predict_email(text_to_analyze)
    
    return {
        "status": "success",
        "is_phishing": result["is_phishing"],
        "confidence": result["confidence"],
        "message": "Phishing attempt detected by ML!" if result["is_phishing"] else "ML says it looks safe."
    }

@app.get("/")
async def root():
    return {"message": "PhishGuard Backend is running!"}
