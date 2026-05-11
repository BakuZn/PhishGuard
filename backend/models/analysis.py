from pydantic import BaseModel, Field
from typing import List, Optional

class AnalysisResult(BaseModel):
    """
    Data model representing the final analysis output from the risk engine.
    """
    prediction: str = Field(..., description="The severity level: SAFE, SUSPICIOUS, HIGH RISK, CRITICAL")
    confidence: float = Field(..., description="The confidence score of the final prediction (0.0 to 1.0)")
    severity: str = Field(..., description="Severity matching prediction for UI mapping")
    reasons: List[str] = Field(default_factory=list, description="List of reasons for the final prediction")
    
    # Optional detailed metrics from sub-analyzers
    suspicious_links_count: Optional[int] = 0
    impersonated_brand: Optional[str] = None
    sender_trust_score: Optional[float] = 0.0
