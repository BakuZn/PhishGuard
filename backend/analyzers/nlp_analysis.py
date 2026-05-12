import re

URGENCY_KEYWORDS = [
    "verify immediately", "account suspended", "click now", 
    "limited time", "urgent action required", "act now",
    "before it's too late", "update your account"
]

CREDENTIAL_KEYWORDS = [
    "password", "login", "credential", "ssn", "social security",
    "credit card", "bank account", "routing number"
]

async def analyze_nlp(text: str) -> dict:
    """
    Heuristic NLP analysis for urgency and credential harvesting.
    """
    result = {
        "urgency_score": 0.0,
        "credential_harvest_score": 0.0,
        "is_promotional": False,
        "risk_score": 0
    }
    
    if not text:
        return result
        
    text_lower = text.lower()
    
    # Detect if this is likely a legitimate promotional or mass-mailing email
    promo_keywords = ["unsubscribe", "opt out", "manage preferences", "view in browser", "privacy policy"]
    if any(kw in text_lower for kw in promo_keywords):
        result["is_promotional"] = True
    
    urgency_hits = sum(1 for kw in URGENCY_KEYWORDS if kw in text_lower)
    cred_hits = sum(1 for kw in CREDENTIAL_KEYWORDS if kw in text_lower)
    
    # Cap scores at 1.0 (100%)
    result["urgency_score"] = min(1.0, urgency_hits * 0.2)
    result["credential_harvest_score"] = min(1.0, cred_hits * 0.25)
    
    result["risk_score"] += int(result["urgency_score"] * 30)
    result["risk_score"] += int(result["credential_harvest_score"] * 40)

    return result
