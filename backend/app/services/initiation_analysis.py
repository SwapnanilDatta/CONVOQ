from datetime import datetime
from collections import defaultdict
from app.services.analysis import parse_timestamp

def initiation_analysis(messages, gap_hours=6):
    initiations = defaultdict(int)

    prev_time = None

    for i, msg in enumerate(messages):
        try:
            current_time = parse_timestamp(msg.timestamp)
        except ValueError:
            continue

        # First message always initiates
        if i == 0:
            initiations[msg.sender] += 1
        else:
            gap = (current_time - prev_time).total_seconds() / 3600
            if gap >= gap_hours:
                initiations[msg.sender] += 1

        prev_time = current_time

    return dict(initiations)
