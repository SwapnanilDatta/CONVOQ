from datetime import datetime
from collections import defaultdict
def initiation_analysis(messages, gap_hours=6):
    initiations = defaultdict(int)

    prev_time = None

    for i, msg in enumerate(messages):
        current_time = datetime.strptime(
            msg.timestamp.replace("pm", "PM").replace("am", "AM"),
            "%m/%d/%y %I:%M %p"
        )

        # First message always initiates
        if i == 0:
            initiations[msg.sender] += 1
        else:
            gap = (current_time - prev_time).total_seconds() / 3600
            if gap >= gap_hours:
                initiations[msg.sender] += 1

        prev_time = current_time

    return dict(initiations)
