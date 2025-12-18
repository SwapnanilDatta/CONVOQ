from pydantic import BaseModel
from typing import List

class ChatMessage(BaseModel):
    timestamp: str
    sender: str
    message: str

class UploadResponse(BaseModel):
    total_messages: int
    messages: List[ChatMessage]
