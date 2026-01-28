import re
from typing import List
from datetime import datetime
from app.models.schema import Message

def parse_chat(text: str, date_format: str = "auto") -> List[Message]:
    """
    Parse WhatsApp chat export text into structured messages.
    Converts timestamps to ISO 8601 (YYYY-MM-DD HH:MM:SS) to avoid ambiguity.
    """
    messages = []
    
    # regex: captures date, hours:minutes, optional seconds, ampm, sender, and message
    # The (?: :(\d{2}))? part matches seconds but we'll choose to ignore them
    pattern = re.compile(
        r'^\[?(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2})(?::\d{2})?\s*(AM|PM|am|pm)?\]?[\s\-]*([^:]+):\s*(.*)',
        re.MULTILINE | re.IGNORECASE
    )
    
    lines = text.strip().split('\n')
    current_message = None
    
    # Mapping frontend format strings to python strptime pattern
    # "mm/dd/yyyy" -> "%m/%d/%Y"
    # "dd/mm/yyyy" -> "%d/%m/%Y"
    # "mm/dd/yy"   -> "%m/%d/%y"
    # "dd/mm/yy"   -> "%d/%m/%y"
    
    format_map = {
        "mm/dd/yyyy": "%m/%d/%Y",
        "dd/mm/yyyy": "%d/%m/%Y", 
        "mm/dd/yy": "%m/%d/%y",
        "dd/mm/yy": "%d/%m/%y"
    }
    
    py_date_fmt = format_map.get(date_format)

    for line in lines:
        line = line.strip()
        if not line: continue
            
        match = pattern.match(line)
        
        if match:
            if current_message:
                messages.append(current_message)
            
            date_part = match.group(1)
            time_part = match.group(2) # HH:MM
            ampm = (match.group(3) or "").upper()
            sender = match.group(4).strip()
            message_text = match.group(5).strip()
            
            # Construct the raw timestamp string from regex
            raw_ts = f"{date_part} {time_part} {ampm}".strip()
            
            # Timestamp normalization to ISO 8601
            final_ts = raw_ts # Default fallback
            
            if py_date_fmt:
                try:
                    # Construct full format string for strptime
                    # If AM/PM exists, appending %I:%M %p. If not, %H:%M
                    full_fmt = f"{py_date_fmt} %I:%M %p" if ampm else f"{py_date_fmt} %H:%M"
                    
                    dt = datetime.strptime(raw_ts, full_fmt)
                    final_ts = dt.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    # Fallback or error - keeping raw might be safer if user selected wrong format
                    # but downstream analysis expects standard or specific formats.
                    # We'll leave it as raw so analysis.py can try its fallback list if needed
                    pass

            current_message = Message(
                timestamp=final_ts,
                sender=sender,
                message=message_text
            )
        elif current_message:
            current_message.message += " " + line
    
    if current_message:
        messages.append(current_message)
    
    return messages