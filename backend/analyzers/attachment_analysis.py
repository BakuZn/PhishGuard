# Placeholder for actual attachment analysis
# In a real scenario, this would parse MIME parts from a raw email.
# Since the Chrome Extension primarily sends text/html, we can look for suspicious links or base64 attachments.

async def analyze_attachments(text: str, html: str) -> dict:
    """
    Analyze for dangerous attachments or payload indicators.
    """
    result = {
        "dangerous_attachment": False,
        "risk_score": 0
    }
    
    combined = (text or "").lower() + " " + (html or "").lower()
    
    # Very basic heuristic looking for mentions of dangerous extensions
    dangerous_exts = ['.exe', '.scr', '.bat', '.vbs', '.js', '.jar']
    
    for ext in dangerous_exts:
        if f"attached{ext}" in combined or f"attachment{ext}" in combined:
            result["dangerous_attachment"] = True
            result["risk_score"] += 80
            break

    return result
