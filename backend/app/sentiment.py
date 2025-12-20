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
            # assuming format: "12/01/24 10:41 pm"
            date_str = item["timestamp"].split(" ")[0]
            date = datetime.strptime(date_str, "%d/%m/%y").date()
            daily[date].append(item["sentiment"])
        except:
            continue

    timeline = []
    for date, scores in daily.items():
        timeline.append({
            "date": str(date),
            "avg_sentiment": round(sum(scores) / len(scores), 3)
        })

    # sort by date
    timeline.sort(key=lambda x: x["date"])
    return timeline
