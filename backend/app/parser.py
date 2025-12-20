"""
WhatsApp Chat Parser
Save this as: app/parser.py
"""
import re
from datetime import datetime
from typing import List
from app.schema import Message

def parse_chat(text: str) -> List[Message]:
    """Parse WhatsApp chat export text into structured messages"""
    messages = []
    
    # Regex patterns for WhatsApp formats
    patterns = [
        # 12/01/24, 10:41 pm - Sender: Message
        r'(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2})\s*(am|pm)\s*-\s*([^:]+):\s*(.+)',
        # [12/01/24, 10:41:23 PM] Sender: Message
        r'\[(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?)\s*(AM|PM)\]\s*([^:]+):\s*(.+)',
    ]
    
    lines = text.strip().split('\n')
    current_message = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        matched = False
        for pattern in patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                matched = True
                date_part = match.group(1)
                time_part = match.group(2)
                ampm = match.group(3).upper()
                sender = match.group(4).strip()
                message_text = match.group(5).strip()
                
                timestamp = f"{date_part} {time_part} {ampm}"
                
                if current_message:
                    messages.append(current_message)
                
                current_message = Message(
                    timestamp=timestamp,
                    sender=sender,
                    message=message_text
                )
                break
        
        if not matched and current_message:
            current_message.message += " " + line
    
    if current_message:
        messages.append(current_message)
    
    return messages