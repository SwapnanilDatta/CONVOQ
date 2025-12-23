from nltk.sentiment.vader import SentimentIntensityAnalyzer
from collections import defaultdict
from datetime import datetime

sia = SentimentIntensityAnalyzer()

def analyze_sentiment(messages):
    sentiment_data = []

    for msg in messages:
        score = sia.polarity_scores(msg.message)["compound"]

        sentiment_data.append({
            "timestamp": msg.timestamp,
            "sender": msg.sender,
            "sentiment": score
        })

    return sentiment_data


def sentiment_timeline(sentiment_data):
    daily = defaultdict(list)

    for item in sentiment_data:
        try:
            timestamp = item["timestamp"]
            date_str = timestamp.split(" ")[0]
            
            # Try both MM/DD/YY and DD/MM/YY formats
            date = None
            for fmt in ["%m/%d/%y", "%d/%m/%y"]:
                try:
                    date = datetime.strptime(date_str, fmt).date()
                    break
                except ValueError:
                    continue
            
            if date:
                daily[date].append(item["sentiment"])
        except:
            continue

    timeline = []
    for date, scores in daily.items():
        timeline.append({
            "date": str(date),
            "avg_sentiment": round(sum(scores) / len(scores), 3)
        })

    timeline.sort(key=lambda x: x["date"])
    return timeline