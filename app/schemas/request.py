from pydantic import BaseModel
from typing import Optional

class AIRequest(BaseModel):
    text: str
    task: str  # "summarize", "classify", or "qa"
    question: Optional[str] = None # Only for "qa"