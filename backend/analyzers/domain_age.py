import whois
from datetime import datetime

async def analyze_domain_age(sender_domain: str) -> dict:
    """
    Check the registration age of the sender's domain.
    """
    result = {
        "domain_age_days": -1,
        "risk_score": 0
    }
    
    if not sender_domain:
        return result
        
    try:
        import asyncio
        w = await asyncio.to_thread(whois.whois, sender_domain)
        creation_date = w.creation_date
        
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
            
        if creation_date:
            age_days = (datetime.now() - creation_date).days
            result["domain_age_days"] = age_days
            
            if age_days < 30:
                result["risk_score"] += 50
            elif age_days < 90:
                result["risk_score"] += 20
    except Exception:
        # Whois failed or domain not found
        pass

    return result
