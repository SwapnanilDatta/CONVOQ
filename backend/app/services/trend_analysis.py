from typing import List, Dict, Any

def evaluate_trends(current_stats: Dict[str, Any], history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluates trends across the last N uploads to provide a decision signal.
    
    Returns:
        {
            "decision": "Continue" | "Continue with Changes" | "Pause / Reconsider",
            "decision_color": "green" | "yellow" | "red",
            "reasons": ["Reason 1", "Reason 2"],
            "metrics_delta": { "health_score": -5, "toxicity": +2 ... }
        }
    """
    # 1. Prepare Data
    # We want chronological order: [Oldest, ..., Newest (Current)]
    # History comes in as DESC usually (newest first). Let's sort it.
    
    past_snapshots = []
    
    # helper to safely extract metrics from nested structures if needed, 
    # but based on main.py, history items have "health_score", "full_data" etc.
    for item in history:
        # Extract relevant metrics from history item
        # Structure from history query: id, total_messages, health_score, persona_tag, created_at, full_data
        data = item.get("full_data", {}) or {}
        
        # SKIP pending fast analyses (health score is provisional/0)
        if data.get("analysis_status") == "pending_deep":
            continue

        features = data.get("features", {})
        
        snapshot = {
            "health_score": item.get("health_score", 0),
            "toxicity": data.get("toxicity", {}).get("toxicity_rate", 0),
            "reply_balance": features.get("reply_time_balance", 0.5),
            "initiation_balance": features.get("initiation_balance", 0.5),
            "sentiment_stability": features.get("sentiment_stability", 0.5)
        }
        past_snapshots.append(snapshot)
    
    # Sort past to be Oldest -> Newest
    past_snapshots.reverse()
    
    # Add current
    current_features = current_stats.get("features", {})
    current_snapshot = {
        "health_score": current_stats.get("health_score", 0),
        "toxicity": current_stats.get("toxicity", {}).get("toxicity_rate", 0),
        "reply_balance": current_features.get("reply_time_balance", 0.5),
        "initiation_balance": current_features.get("initiation_balance", 0.5),
        "sentiment_stability": current_features.get("sentiment_stability", 0.5)
    }
    
    all_snapshots = past_snapshots + [current_snapshot]
    
    # If not enough data (needs at least 2 points to show ANY trend, preferably 3)
    if len(all_snapshots) < 2:
        return {
            "decision": "Not Enough Data",
            "decision_color": "gray",
            "reasons": ["Upload more chats over time to track trends."],
            "metrics_delta": {}
        }

    # 2. Compute Trends (Last 3-5 uploads)
    # Focus on the tail (most recent 3)
    recent_window = all_snapshots[-3:]
    
    # Delta: Current - Previous (or Average of previous)
    # Simple check: Compare Current vs (Average of previous in window)
    prev_window = recent_window[:-1]
    avg_prev_health = sum(s["health_score"] for s in prev_window) / len(prev_window)
    avg_prev_tox = sum(s["toxicity"] for s in prev_window) / len(prev_window)
    
    health_delta = current_snapshot["health_score"] - avg_prev_health
    toxicity_delta = current_snapshot["toxicity"] - avg_prev_tox
    
    reasons = []
    
    # 3. Decision Logic
    
    # Critical Flags
    health_declining = health_delta < -5 # dropped by more than 5 points
    health_improving = health_delta > 5
    toxicity_rising = toxicity_delta > 5 # rose by 5%
    
    # Effort Imbalance (Threshold 0.35 means one person does < 35% of work, so other > 65%)
    # Balance score is 0..1 (1 is perfect balance)
    severe_imbalance = current_snapshot["initiation_balance"] < 0.3 or current_snapshot["reply_balance"] < 0.3
    
    decision = "Continue" # Default
    color = "green"
    
    # Logic Tree
    if (health_declining and toxicity_rising) or (current_snapshot["health_score"] < 40 and health_declining):
        decision = "Pause / Reconsider"
        color = "red"
        reasons.append("Relationship health is actively declining.")
        reasons.append("Toxicity levels are rising.")
    
    elif severe_imbalance and current_snapshot["health_score"] < 60:
         decision = "Pause / Reconsider"
         color = "red"
         reasons.append("Severe effort imbalance detected.")
         reasons.append("One person is carrying the conversation.")
         
    elif health_declining:
        decision = "Continue with Changes"
        color = "yellow"
        reasons.append("Health score has dropped recently.")
        
    elif toxicity_rising:
        decision = "Continue with Changes"
        color = "yellow"
        reasons.append("Toxicity is creeping up.")
        
    elif severe_imbalance:
        decision = "Continue with Changes"
        color = "yellow"
        reasons.append("Effort is very one-sided.")
        
    elif health_improving:
        decision = "Continue"
        color = "green"
        reasons.append("Relationship health is improving!")
        
    else:
        # Stable
        decision = "Continue"
        color = "green"
        reasons.append("Relationship appears stable.")
        
    return {
        "decision": decision,
        "decision_color": color,
        "reasons": reasons,
        "metrics_delta": {
            "health_change": round(health_delta, 1),
            "toxicity_change": round(toxicity_delta, 1)
        }
    }
