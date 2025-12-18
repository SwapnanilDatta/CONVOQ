from datetime import datetime
from collections import defaultdict

def reply_time_analysis(messages):
    sender_times = defaultdict(list)
    prev_sender = None
    prev_time = None

    for msg in messages:
        try:
            current_time = datetime.strptime(
                msg.timestamp.replace("pm", "PM").replace("am", "AM"),
                "%m/%d/%y %I:%M %p" 
            )
        except Exception as e:
            
            print(f"Error parsing: {msg.timestamp} -> {e}")
            continue

        if prev_sender and msg.sender != prev_sender:
            diff = (current_time - prev_time).total_seconds() / 60
           
            if diff >= 0:
                sender_times[msg.sender].append(diff)

        prev_sender = msg.sender
        prev_time = current_time

    avg_reply = {
        sender: round(sum(times) / len(times), 2)
        for sender, times in sender_times.items()
        if times
    }

    return avg_reply