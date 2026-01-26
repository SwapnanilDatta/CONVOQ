from pydantic import BaseModel
from typing import List, Dict, Optional, Union

class Message(BaseModel):
    timestamp: str
    sender: str
    message: str

class UploadResponse(BaseModel):
    total_messages: int
    messages: List[Message]

class DeepAnalysisRequest(BaseModel):
    cache_key: str
    analysis_id: Union[str, int]