from backend.models.email import EmailPayload
from backend.models.analysis import AnalysisResult
from backend.analyzers import email_auth, reputation, url_analysis, domain_age, html_analysis, homoglyph, brand_impersonation, nlp_analysis, attachment_analysis
from backend.ml import ml_model
import asyncio

async def analyze_email_risk(payload: EmailPayload) -> AnalysisResult:
    """
    Orchestrator that runs all analyzers and the ML model concurrently,
    aggregates risk scores, and returns the final decision.
    """
    
    sender_domain = ""
    if payload.sender and "@" in payload.sender:
        sender_domain = payload.sender.split("@")[1].lower()
        
    combined_text = (payload.subject or "") + " " + (payload.body_text or "")
        
    # Run analyzers concurrently
    results = await asyncio.gather(
        email_auth.analyze_email_auth(sender_domain),
        reputation.analyze_reputation(payload.sender),
        url_analysis.analyze_urls(payload.body_text, payload.body_html, payload.links),
        domain_age.analyze_domain_age(sender_domain),
        html_analysis.analyze_html(payload.body_html),
        homoglyph.analyze_homoglyphs(sender_domain),
        brand_impersonation.analyze_brand_impersonation(combined_text, sender_domain),
        nlp_analysis.analyze_nlp(combined_text),
        attachment_analysis.analyze_attachments(payload.body_text, payload.body_html)
    )
    
    auth_res, rep_res, url_res, age_res, html_res, homo_res, brand_res, nlp_res, attach_res = results
    
    # Run ML Model (synchronous)
    ml_res = ml_model.predict_email(combined_text)
    
    # Aggregate Score
    total_risk_score = 0
    total_risk_score += auth_res.get("risk_score", 0)
    total_risk_score += url_res.get("risk_score", 0)
    total_risk_score += age_res.get("risk_score", 0)
    total_risk_score += html_res.get("risk_score", 0)
    total_risk_score += homo_res.get("risk_score", 0)
    total_risk_score += brand_res.get("risk_score", 0)
    total_risk_score += nlp_res.get("risk_score", 0)
    total_risk_score += attach_res.get("risk_score", 0)
    
    if rep_res.get("reputation_score", 50) < 20:
        total_risk_score += 40
        
    if ml_res.get("is_phishing"):
        total_risk_score += 80 * ml_res.get("confidence", 1.0)
        
    # Compile Reasons
    reasons = []
    if auth_res.get("spf") == "fail": reasons.append("SPF validation failed")
    if rep_res.get("reputation_score", 50) == 0: reasons.append("Sent from disposable email provider")
    if url_res.get("suspicious_urls"): reasons.append(f"Found {len(url_res.get('suspicious_urls'))} suspicious URLs")
    if age_res.get("domain_age_days", -1) != -1 and age_res.get("domain_age_days") < 30: reasons.append("Sender domain was registered recently")
    if html_res.get("obfuscation_detected"): reasons.append("HTML obfuscation detected")
    if homo_res.get("homoglyph_detected"): reasons.append(f"Homoglyph attack impersonating {homo_res.get('target_brand')}")
    if brand_res.get("impersonation_detected"): reasons.append(f"Impersonating brand: {brand_res.get('claimed_brand')}")
    if nlp_res.get("urgency_score", 0) > 0.6: reasons.append("High urgency language detected")
    if attach_res.get("dangerous_attachment"): reasons.append("Dangerous attachment type mentioned")
    if ml_res.get("is_phishing"): reasons.append("Machine Learning model predicts phishing")
    
    # Final Decision Logic
    prediction = "SAFE"
    confidence = 1.0
    
    # Normalize risk score to confidence loosely
    if total_risk_score >= 150:
        prediction = "CRITICAL"
        confidence = min(0.99, total_risk_score / 300.0)
    elif total_risk_score >= 80:
        prediction = "HIGH RISK"
        confidence = min(0.95, total_risk_score / 200.0)
    elif total_risk_score >= 30:
        prediction = "SUSPICIOUS"
        confidence = min(0.80, total_risk_score / 100.0)
    else:
        prediction = "SAFE"
        confidence = 0.90
        if not reasons:
            reasons.append("No suspicious indicators found.")
            
    # For safe emails from trusted domains
    if rep_res.get("trusted"):
        prediction = "SAFE"
        confidence = 0.99
        reasons = ["Sent from a trusted internal/verified domain"]

    return AnalysisResult(
        prediction=prediction,
        confidence=round(confidence, 2),
        severity=prediction,
        reasons=reasons,
        suspicious_links_count=len(url_res.get("suspicious_urls", [])),
        impersonated_brand=brand_res.get("claimed_brand"),
        sender_trust_score=rep_res.get("reputation_score", 50.0)
    )
