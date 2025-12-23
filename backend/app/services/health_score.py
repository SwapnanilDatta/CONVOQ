def compute_health_score(features):
    """
    features (normalized 0–1):
    {
      "reply_time_balance": float,
      "initiation_balance": float,
      "sentiment_stability": float,
      "msg_length_balance": float,
      "emoji_density": float
    }
    """

    score = (
        0.30 * features["reply_time_balance"] +
        0.25 * features["initiation_balance"] +
        0.20 * features["sentiment_stability"] +
        0.15 * features["msg_length_balance"] +
        0.10 * features["emoji_density"]
    )

    return round(score * 100, 2)
