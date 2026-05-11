BRANDS = {
    "google": ["google.com"],
    "microsoft": ["microsoft.com"],
    "apple": ["apple.com"],
    "amazon": ["amazon.com"],
    "paypal": ["paypal.com"],
    "linkedin": ["linkedin.com"]
}

async def analyze_brand_impersonation(text: str, sender_domain: str) -> dict:
    """
    Detect if the email mentions a brand but comes from a different domain.
    """
    result = {
        "impersonation_detected": False,
        "claimed_brand": None,
        "risk_score": 0
    }
    
    if not text or not sender_domain:
        return result
        
    text_lower = text.lower()
    
    for brand, domains in BRANDS.items():
        if brand in text_lower:
            # The brand is mentioned, check if the sender domain matches
            if sender_domain not in domains and not any(sender_domain.endswith("." + d) for d in domains):
                result["impersonation_detected"] = True
                result["claimed_brand"] = brand.capitalize()
                result["risk_score"] += 60
                break

    return result
