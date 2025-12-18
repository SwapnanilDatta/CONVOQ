import re
from typing import List
from app.schema import ChatMessage


# 12/01/24, 10:41 pm - John: hello bro
# mm/dd/yy, hh:mm am/pm - Sender: message

pattern = re.compile(
    r"(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}\s?[ap]m)\s-\s([^:]+):\s(.*)"
)

def parse_chat(text: str) -> List[ChatMessage]:
    messages = []

    for line in text.split("\n"):
        match = pattern.match(line)
        if match:
            date, time, sender, message = match.groups()
            messages.append(
                ChatMessage(
                    timestamp=f"{date} {time}",
                    sender=sender.strip(),
                    message=message.strip()
                )
            )

    return messages
