import tldextract
import re
from typing import List

SUSPICIOUS_TLDS = ['.xyz', '.top', '.club', '.online', '.vip']
URL_REGEX = re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+')

async def analyze_urls(text: str, html: str, provided_links: List[str]) -> dict:
    """
    Analyze URLs extracted from the email for suspicious patterns.
    """
    result = {
        "suspicious_urls": [],
        "risk_score": 0
    }
    
    all_text = (text or "") + " " + (html or "")
    found_urls = URL_REGEX.findall(all_text)
    
    # Combine with provided links
    urls_to_check = set(found_urls + (provided_links or []))
    
    for url in urls_to_check:
        ext = tldextract.extract(url)
        tld_with_dot = f".{ext.suffix}"
        
        # IP-based URL check
        if re.match(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', ext.domain):
            result["suspicious_urls"].append(url)
            result["risk_score"] += 40
            
        # Suspicious TLD check
        elif tld_with_dot in SUSPICIOUS_TLDS:
            result["suspicious_urls"].append(url)
            result["risk_score"] += 20
            
        # URL Shorteners
        elif ext.domain in ['bit', 'tinyurl', 't', 'goo']:
            result["suspicious_urls"].append(url)
            result["risk_score"] += 15

    return result
