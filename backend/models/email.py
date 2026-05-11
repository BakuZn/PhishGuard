from pydantic import BaseModel, Field
from typing import List, Optional

class EmailPayload(BaseModel):
    """
    Data model representing the incoming email payload from the Chrome extension.
    """
    sender: str = Field(..., description="The sender's email address")
    subject: str = Field(..., description="The subject line of the email")
    body_text: str = Field(..., description="The plain text content of the email body")
    body_html: Optional[str] = Field(None, description="The raw HTML content of the email body")
    links: Optional[List[str]] = Field(default_factory=list, description="List of all URLs found in the email")
