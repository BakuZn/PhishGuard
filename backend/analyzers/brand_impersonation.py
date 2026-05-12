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
        
    from backend.analyzers.reputation import TRUSTED_DOMAINS
    is_globally_trusted = any(sender_domain == td or sender_domain.endswith("." + td) for td in TRUSTED_DOMAINS)
    if is_globally_trusted:
        return result

    text_lower = text.lower()
    
    for brand, domains in BRANDS.items():
        if brand in text_lower:
            # The brand is mentioned. Check if the sender domain matches the brand name
            # i.e., domain is "amazon.in", "amazon.co.uk", "bounces.amazon.com"
            is_valid_brand_domain = False
            
            # Check explicit domains
            if sender_domain in domains or any(sender_domain.endswith("." + d) for d in domains):
                is_valid_brand_domain = True
            # Check if brand name is the main part of the domain (e.g., brand.com, brand.in)
            elif sender_domain.startswith(brand + ".") or f".{brand}." in sender_domain:
                is_valid_brand_domain = True
                
            if not is_valid_brand_domain:
                result["impersonation_detected"] = True
                result["claimed_brand"] = brand.capitalize()
                result["risk_score"] += 60
                break

    return result
