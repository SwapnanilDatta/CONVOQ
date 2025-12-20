from datetime import datetime
from collections import defaultdict
from typing import List
from app.schema import Message

def parse_timestamp(timestamp: str) -> datetime:
    """Parse timestamp with multiple format support"""
    formats = [
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
    
    for i in range(1, len(messages)):
        current_msg = messages[i]
        prev_msg = messages[i-1]
        
        if current_msg.sender != prev_msg.sender:
            try:
                current_time = parse_timestamp(current_msg.timestamp)
                prev_time = parse_timestamp(prev_msg.timestamp)
                
                time_diff = (current_time - prev_time).total_seconds() / 60
                
                if time_diff > 0:
                    reply_times[current_msg.sender].append({
                        "minutes": round(time_diff, 2),
                        "timestamp": current_msg.timestamp
                    })
            except:
                continue
    
    avg_reply_time = {}
    for sender, times in reply_times.items():
        if times:
            avg_minutes = sum(t["minutes"] for t in times) / len(times)
            avg_reply_time[sender] = round(avg_minutes, 2)
    
    all_replies = []
    for sender, times in reply_times.items():
        for t in times:
            all_replies.append({
                "sender": sender,
                "minutes": t["minutes"],
                "timestamp": t["timestamp"]
            })
    
    fastest = min(all_replies, key=lambda x: x["minutes"]) if all_replies else None
    slowest = max(all_replies, key=lambda x: x["minutes"]) if all_replies else None
    
    return {
        "avg_reply_time": avg_reply_time,
        "fastest_reply": fastest,
        "slowest_reply": slowest,
        "total_replies_analyzed": len(all_replies)
    }