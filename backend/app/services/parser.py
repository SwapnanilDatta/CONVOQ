import re
from typing import List
from app.models.schema import Message

def parse_chat(text: str) -> List[Message]:
    """Parse WhatsApp chat export text into structured messages, ignoring seconds"""
    messages = []
    
    # regex: captures date, hours:minutes, optional seconds, ampm, sender, and message
    # The (?: :(\d{2}))? part matches seconds but we'll choose to ignore them
    pattern = re.compile(
        r'^\[?(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2})(?::\d{2})?\s*(AM|PM|am|pm)?\]?[\s\-]*([^:]+):\s*(.*)',
        re.MULTILINE | re.IGNORECASE
    )
    
    lines = text.strip().split('\n')
    current_message = None
    
    for line in lines:
        line = line.strip()
        if not line: continue
            
        match = pattern.match(line)
        
        if match:
            if current_message:
                messages.append(current_message)
            
            date_part = match.group(1)
            time_part = match.group(2) # This only captures HH:MM
            ampm = (match.group(3) or "").upper()
            sender = match.group(4).strip()
            message_text = match.group(5).strip()
            
            # Reconstruct to exactly match: '12/09/21 10:00 AM'
            timestamp = f"{date_part} {time_part} {ampm}".strip()
            
            current_message = Message(
                timestamp=timestamp,
                sender=sender,
                message=message_text
            )
        elif current_message:
            current_message.message += " " + line
    
    if current_message:
        messages.append(current_message)
    
    return messages