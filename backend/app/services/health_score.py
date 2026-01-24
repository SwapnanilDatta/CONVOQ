def compute_health_score(features):
    # Features: reply_time, initiation, sentiment_stability, msg_length, emoji_density
    base_score = (
        0.30 * features["reply_time_balance"] +
        0.25 * features["initiation_balance"] +
        0.20 * features["sentiment_stability"] +
        0.15 * features["msg_length_balance"] +
        0.10 * features["emoji_density"]
    )
    
    # NEW: Subtract toxicity impact (scale it so 10% toxicity = -10 points)
    toxicity_penalty = features.get("toxicity_impact", 0) * 100
    final_score = (base_score * 100) - toxicity_penalty

    return round(max(0, final_score), 2)