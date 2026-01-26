import os
import uuid
from typing import List
from collections import defaultdict
from dotenv import load_dotenv
from jose import jwt
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from cachetools import TTLCache

from app.services.parser import parse_chat
from app.models.schema import UploadResponse, Message, DeepAnalysisRequest
from app.services.sentiment import analyze_sentiment, sentiment_timeline
from app.services.analysis import reply_time_analysis
from app.services.initiation_analysis import initiation_analysis
from app.services.health_score import compute_health_score
from app.services.toxicity import detect_toxicity
from app.services.cluster import ConversationClassifier
from app.services.coach import generate_relationship_narrative, generate_decision_advice
from app.services.semantic import analyze_semantics
from app.services.trend_analysis import evaluate_trends
from app.utils.rate_limiter import RateLimiter
from app.utils.token_counter import TokenCounter

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

classifier = ConversationClassifier()
security = HTTPBearer()

# Cache for storing parsed messages. ID -> Message List. TTL=600s (10 min)
message_cache = TTLCache(maxsize=100, ttl=600)

# Initialize rate limiter and token counter
rate_limiter = RateLimiter(requests_per_minute=3, requests_per_day=50)
token_counter = TokenCounter(daily_token_limit=10000)

app = FastAPI(title="CONVOQ API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.get_unverified_claims(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return user_id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

def calculate_features(messages: List[Message], reply_analysis: dict, sentiment_data: list, initiations: dict, toxicity_data: dict):
    avg_replies = list(reply_analysis["avg_reply_time"].values())
    reply_balance = min(avg_replies) / max(avg_replies) if len(avg_replies) >= 2 and max(avg_replies) > 0 else 0.5
    
    init_counts = list(initiations.values())
    initiation_balance = min(init_counts) / max(init_counts) if len(init_counts) >= 2 and max(init_counts) > 0 else 0.5
    
    sentiments = [s["sentiment"] for s in sentiment_data]
    if sentiments:
        avg_sentiment = sum(sentiments) / len(sentiments)
        variance = sum((s - avg_sentiment) ** 2 for s in sentiments) / len(sentiments)
        sentiment_stability = max(0, 1 - variance)
    else:
        sentiment_stability = 0.5
    
    msg_lengths = defaultdict(list)
    for msg in messages:
        msg_lengths[msg.sender].append(len(msg.message))
    
    avg_lengths = {s: sum(l)/len(l) for s, l in msg_lengths.items()}
    if len(avg_lengths) >= 2:
        l_vals = list(avg_lengths.values())
        msg_length_balance = min(l_vals) / max(l_vals) if max(l_vals) > 0 else 0.5
    else:
        msg_length_balance = 0.5
    
    emoji_count = sum(1 for m in messages if any(c in m.message for c in ['😊', '😂', '❤️', '👍', '🎉']))
    emoji_density = min(emoji_count / len(messages), 1.0) if messages else 0
    tox_rate = toxicity_data.get("toxicity_rate", 0) / 100
    return {
        "reply_time_balance": round(reply_balance, 3),
        "initiation_balance": round(initiation_balance, 3),
        "sentiment_stability": round(sentiment_stability, 3),
        "msg_length_balance": round(msg_length_balance, 3),
        "emoji_density": round(emoji_density, 3),
        "toxicity_impact": round(tox_rate, 3)
    }

@app.get("/")
def root():
    return {"status": "online"}

def get_db_user_uuid(clerk_id: str) -> str:
    user_query = supabase.table("users").select("id").eq("clerk_id", clerk_id).execute()
    if not user_query.data:
        new_user = supabase.table("users").insert({"clerk_id": clerk_id}).execute()
        return new_user.data[0]["id"]
    return user_query.data[0]["id"]

@app.post("/analyze/fast")
async def analyze_fast(file: UploadFile = File(...), user_id: str = Depends(verify_token)):
    try:
        # Rate Limit
        # Rate Limit
        # allowed, rate_msg = rate_limiter.is_allowed(user_id)
        # if not allowed:
        #     raise HTTPException(status_code=429, detail=rate_msg)
        
        content = await file.read()
        messages = parse_chat(content.decode("utf-8"))
        
        if not messages:
            raise HTTPException(status_code=400, detail="No messages found")
        
        # Token Check
        estimated_tokens = token_counter.estimate_messages_tokens(messages)
        can_process, token_msg = token_counter.can_process(user_id, estimated_tokens)
        if not can_process:
            raise HTTPException(status_code=429, detail=token_msg)

        # --- FAST ANALYSIS ---
        reply_analysis = reply_time_analysis(messages)
        # Skip Toxicity: just return empty placeholder
        toxicity_data = {"toxicity_rate": 0.0, "toxic_messages": [], "status": "locked"} 
        
        sentiment_data = analyze_sentiment(messages)
        timeline = sentiment_timeline(sentiment_data)
        initiations = initiation_analysis(messages, gap_hours=6)
        semantic_data = analyze_semantics(messages, toxicity_data=toxicity_data) # Might be weak without toxic info
        
        features = calculate_features(messages, reply_analysis, sentiment_data, initiations, toxicity_data)
        health_score = compute_health_score(features)
        persona = classifier.predict(features)

        # Placeholders for deep analysis
        coach_narrative = "Locked. Click 'Unlock Deep Insights' to generate."
        trend_results = {"decision": "Locked", "status": "locked"}
        decision_advice = {"advice": [], "reply_suggestions": []}

        # --- RECORD USAGE ---
        # rate_limiter.record_request(user_id)
        token_counter.record_tokens(user_id, estimated_tokens)
        
        rate_usage = rate_limiter.get_usage(user_id)
        token_usage = token_counter.get_today_usage(user_id)

        # DB operations
        db_uuid = get_db_user_uuid(user_id)
        
        full_data = {
            "total_messages": len(messages),
            "participants": list(set(msg.sender for msg in messages)),
            "toxicity": toxicity_data,
            "health_score": health_score,
            "persona_tag": persona, 
            "features": features,
            "reply_times": reply_analysis,
            "sentiment": {"total_messages": len(sentiment_data), "timeline": timeline},
            "initiations": initiations,
            "semantic_analysis": semantic_data,
            "coach_summary": coach_narrative,
            "trend_analysis": trend_results,
            "decision_advice": decision_advice,
            "usage_stats": {
                "rate_limiting": rate_usage,
                "token_counting": token_usage
            },
            "analysis_status": "pending_deep"
        }
        
        insert_resp = supabase.table("analyses").insert({
            "user_id": db_uuid,
            "total_messages": len(messages),
            "health_score": health_score,
            "persona_tag": persona,
            "full_data": full_data
        }).execute()
        
        analysis_id = insert_resp.data[0]["id"]
        
        # --- CACHE MESSAGES ---
        cache_key = str(uuid.uuid4())
        message_cache[cache_key] = messages
        
        full_data["cache_key"] = cache_key
        full_data["analysis_id"] = analysis_id
        
        return full_data

    except Exception as e:
        print(f"Fast Analysis Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Fast Analysis Failed")

@app.post("/analyze/deep")
async def analyze_deep(request: DeepAnalysisRequest, user_id: str = Depends(verify_token)):
    try:
        messages = message_cache.get(request.cache_key)
        if not messages:
            raise HTTPException(status_code=400, detail="Session expired. Please re-upload the file.")
            
        # --- DEEP ANALYSIS ---
        toxicity_data = detect_toxicity(messages) # Slow HP request
        
        # Need to reconstruct some features with real toxicity
        # We need features to run coach/trend correctly if they depend on toxicity
        # Re-fetch fast data? Or just recalculate needed parts.
        # Let's recalculate features.
        
        # ... We need existing data from DB to merge? Or just recalculate features. 
        # Easier to just run the specialized functions.
        
        reply_analysis = reply_time_analysis(messages) # Fast enough to re-run
        sentiment_data = analyze_sentiment(messages)   # Fast enough
        initiations = initiation_analysis(messages, gap_hours=6)
        
        features = calculate_features(messages, reply_analysis, sentiment_data, initiations, toxicity_data)
        health_score = compute_health_score(features) # Might change due to toxicity
        
        # Trends
        db_uuid = get_db_user_uuid(user_id)
        history_query = supabase.table("analyses") \
            .select("id, total_messages, health_score, full_data, created_at") \
            .eq("user_id", db_uuid) \
            .neq("id", request.analysis_id) .order("created_at", desc=True) \
            .limit(5) \
            .execute()
            
        past_history = history_query.data if history_query.data else []
        
        trend_results = evaluate_trends(
            current_stats={
                "health_score": health_score, 
                "toxicity": toxicity_data, 
                "features": features
            },
            history=past_history
        )
        
        coach_narrative = generate_relationship_narrative({
            "participants": list(set(msg.sender for msg in messages)),
            "health_score": health_score,
            "initiations": initiations,
            "features": features
        })
        
        decision_advice = generate_decision_advice(trend_results)
        
        # --- UPDATE DB ---
        update_payload = {
            "toxicity": toxicity_data,
            "health_score": health_score,
            "features": features,
            "trend_analysis": trend_results,
            "coach_summary": coach_narrative,
            "decision_advice": decision_advice,
            "analysis_status": "complete"
        }
        
        # Fetch current record to merge deep fields... or simple merge in frontend?
        # Ideally we update the JSON in DB. Supabase handles JSON updates but replacing the whole object is safer/easier here.
        # We need the full object.
        
        # Let's get the current record
        curr_rec = supabase.table("analyses").select("full_data").eq("id", request.analysis_id).execute()
        if not curr_rec.data:
             raise HTTPException(status_code=404, detail="Analysis not found")
             
        full_data = curr_rec.data[0]["full_data"]
        full_data.update(update_payload)
        
        supabase.table("analyses").update({
            "health_score": health_score,
            "full_data": full_data
        }).eq("id", request.analysis_id).execute()
        
        return full_data

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Deep Analysis Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Deep Analysis Failed: {str(e)}")

@app.get("/history")
async def get_analysis_history(user_id: str = Depends(verify_token)):
    try:
        db_uuid = get_db_user_uuid(user_id)
        history = supabase.table("analyses") \
            .select("id, total_messages, health_score, persona_tag, created_at, full_data") \
            .eq("user_id", db_uuid) \
            .order("created_at", desc=True) \
            .execute()
        return history.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")

@app.get("/usage")
async def get_usage_stats(user_id: str = Depends(verify_token)):
    """Get current rate limit and token usage stats for authenticated user."""
    try:
        rate_usage = rate_limiter.get_usage(user_id)
        token_usage = token_counter.get_today_usage(user_id)
        
        return {
            "user_id": user_id,
            "rate_limiting": {
                "requests_this_minute": rate_usage["requests_this_minute"],
                "requests_today": rate_usage["requests_today"],
                "minute_limit": rate_usage["minute_limit"],
                "daily_limit": rate_usage["daily_limit"],
                "remaining_requests_today": rate_usage["remaining_today"],
                "status": "⚠️ Limited" if rate_usage["requests_this_minute"] >= rate_usage["minute_limit"] else "✅ OK"
            },
            "token_counting": {
                "tokens_used_today": token_usage["tokens_used_today"],
                "tokens_remaining": token_usage["remaining_tokens"],
                "daily_limit": token_usage["daily_limit"],
                "usage_percentage": token_usage["percentage_used"],
                "status": "⚠️ Critical" if token_usage["percentage_used"] > 85 else ("⚠️ Warning" if token_usage["percentage_used"] > 70 else "✅ OK")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch usage: {str(e)}")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)