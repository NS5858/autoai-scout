from pydantic import BaseModel
from typing import Optional, Dict

class AnalyzeRequest(BaseModel):
    url: str

class AnalyzeResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict] = None
