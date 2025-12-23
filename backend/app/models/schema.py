from pydantic import BaseModel
from typing import List, Dict, Optional

class Message(BaseModel):
    timestamp: str
    sender: str
    message: str

class UploadResponse(BaseModel):
    total_messages: int
    messages: List[Message]