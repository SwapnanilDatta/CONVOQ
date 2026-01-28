from datetime import datetime
from collections import defaultdict
from typing import List
from app.models.schema import Message

def parse_timestamp(timestamp: str) -> datetime:
    """Parse timestamp with multiple format support"""
    formats = [
        "%Y-%m-%d %H:%M:%S", # ISO 8601 (Parsed Standard)
        "%m/%d/%y %I:%M %p",
        "%d/%m/%y %I:%M %p",
        "%m/%d/%Y %I:%M %p",
        "%d/%m/%Y %I:%M %p",
        "%m/%d/%y %I:%M:%S %p",
        "%d/%m/%y %I:%M:%S %p",
    ]
    
    timestamp = timestamp.replace("am", "AM").replace("pm", "PM")
    
    for fmt in formats:
        try:
            return datetime.strptime(timestamp, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse timestamp: {timestamp}")

def reply_time_analysis(messages: List[Message]):
    """Analyze reply times between senders"""
    reply_times = defaultdict(list)
    all_gaps = []
    
    for i in range(1, len(messages)):
        current_msg = messages[i]
        prev_msg = messages[i-1]
        
        try:
            current_time = parse_timestamp(current_msg.timestamp)
            prev_time = parse_timestamp(prev_msg.timestamp)
            time_diff = (current_time - prev_time).total_seconds() / 60
            
            if time_diff > 0:
                gap_data = {
                    "minutes": round(time_diff, 2),
                    "timestamp": current_msg.timestamp,
                    "from": prev_msg.sender,
                    "to": current_msg.sender
                }
                all_gaps.append(gap_data)
                
                if current_msg.sender != prev_msg.sender:
                    reply_times[current_msg.sender].append(gap_data)
        except:
            continue
    avg_reply_time = {}
    for sender, times in reply_times.items():
        if times:
            avg_minutes = sum(t["minutes"] for t in times) / len(times)
            avg_reply_time[sender] = round(avg_minutes, 2)
    
    # Find longest ghosting period
    longest_ghost = max(all_gaps, key=lambda x: x["minutes"]) if all_gaps else None
    
    # Peak conversation hours
    hours_count = defaultdict(int)
    for i, msg in enumerate(messages):
        try:
            dt = parse_timestamp(msg.timestamp)
            hours_count[dt.hour] += 1
        except:
            continue
    
    peak_hours = sorted(hours_count.items(), key=lambda x: x[1], reverse=True)[:3]
    
    return {
        "avg_reply_time": avg_reply_time,
        "fastest_reply": min(all_gaps, key=lambda x: x["minutes"]) if all_gaps else None,
        "slowest_reply": max(all_gaps, key=lambda x: x["minutes"]) if all_gaps else None,
        "longest_ghosting": longest_ghost,
        "peak_hours": [{"hour": h, "count": c} for h, c in peak_hours],
        "total_replies_analyzed": len(all_gaps)
    }