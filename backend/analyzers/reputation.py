import re

TRUSTED_DOMAINS = ["google.com", "microsoft.com", "linkedin.com", "joinsuperset.com", "manipal.edu"]
DISPOSABLE_DOMAINS = ["mailinator.com", "10minutemail.com", "guerrillamail.com"]

async def analyze_reputation(sender_email: str) -> dict:
    """
    Analyze sender reputation based on domain.
    """
    result = {
        "reputation_score": 0.0,
        "trusted": False
    }
    
    if not sender_email or "@" not in sender_email:
        return result
        
    domain = sender_email.split("@")[1].lower()
    
    if domain in TRUSTED_DOMAINS:
        result["trusted"] = True
        result["reputation_score"] = 100.0
    elif domain in DISPOSABLE_DOMAINS:
        result["reputation_score"] = 0.0
    else:
        # Default baseline for unknown domains
        result["reputation_score"] = 50.0

    return result
