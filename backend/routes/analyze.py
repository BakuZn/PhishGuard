from fastapi import APIRouter
from backend.models.email import EmailPayload
from backend.models.analysis import AnalysisResult
from backend.services.risk_engine import analyze_email_risk

router = APIRouter()

@router.post("/analyze", response_model=AnalysisResult)
async def analyze_email(payload: EmailPayload):
    """
    Endpoint to analyze an incoming email from the PhishGuard Chrome extension.
    Runs the email through the multi-layered Risk Engine.
    """
    result = await analyze_email_risk(payload)
    return result
