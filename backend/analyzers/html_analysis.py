from bs4 import BeautifulSoup
import re

async def analyze_html(html_content: str) -> dict:
    """
    Detect obfuscation and hidden elements in HTML.
    """
    result = {
        "obfuscation_detected": False,
        "risk_score": 0
    }
    
    if not html_content:
        return result
        
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Check for hidden elements (often used benignly in responsive email templates, so low risk)
    hidden_elements = soup.find_all(style=re.compile(r'display:\s*none|visibility:\s*hidden'))
    if hidden_elements:
        result["obfuscation_detected"] = True
        result["risk_score"] += 5  # Reduced from 20
        
    # Check for forms (emails rarely need inline forms unless malicious)
    forms = soup.find_all('form')
    if forms:
        result["obfuscation_detected"] = True
        result["risk_score"] += 30
        
    # Check for base64 encoded images/blobs
    if 'data:image' in html_content or 'base64' in html_content:
        # Some are benign, but can be used for tracking/obfuscation
        result["risk_score"] += 5  # Reduced from 10
        
    return result
