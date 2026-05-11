import unicodedata

# Common targets for homoglyph attacks
TARGET_BRANDS = ["google.com", "microsoft.com", "paypal.com", "amazon.com", "apple.com"]

async def analyze_homoglyphs(sender_domain: str) -> dict:
    """
    Detect homograph/homoglyph attacks using IDNA and unicode normalization.
    """
    result = {
        "homoglyph_detected": False,
        "target_brand": None,
        "risk_score": 0
    }
    
    if not sender_domain:
        return result
        
    # Unicode normalization
    normalized = unicodedata.normalize('NFKD', sender_domain).encode('ASCII', 'ignore').decode('ASCII')
    
    # Check if the domain is purely ASCII
    is_ascii = all(ord(c) < 128 for c in sender_domain)
    
    if not is_ascii or sender_domain.startswith("xn--"):
        result["homoglyph_detected"] = True
        result["risk_score"] += 80
        
    # Simple substitution check (0 for o, l for I)
    substituted = sender_domain.replace('0', 'o').replace('1', 'l').replace('I', 'l')
    
    for brand in TARGET_BRANDS:
        if substituted == brand and sender_domain != brand:
            result["homoglyph_detected"] = True
            result["target_brand"] = brand
            result["risk_score"] += 90
            break

    return result
