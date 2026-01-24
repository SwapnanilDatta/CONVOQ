import os
from typing import List
from collections import defaultdict
from dotenv import load_dotenv
from jose import jwt
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client

from app.services.parser import parse_chat
from app.models.schema import UploadResponse, Message
from app.services.sentiment import analyze_sentiment, sentiment_timeline
from app.services.analysis import reply_time_analysis
from app.services.initiation_analysis import initiation_analysis
from app.services.health_score import compute_health_score
from app.services.toxicity import detect_toxicity
from app.services.cluster import ConversationClassifier
from app.services.coach import generate_relationship_narrative
from app.services.semantic import analyze_semantics

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

classifier = ConversationClassifier()
security = HTTPBearer()

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

@app.post("/complete")
async def complete_analysis(file: UploadFile = File(...), user_id: str = Depends(verify_token)):
    try:
        content = await file.read()
        messages = parse_chat(content.decode("utf-8"))
        
        if not messages:
            raise HTTPException(status_code=400, detail="No messages found")
        
        reply_analysis = reply_time_analysis(messages)
        toxicity_data = detect_toxicity(messages)
        sentiment_data = analyze_sentiment(messages)
        timeline = sentiment_timeline(sentiment_data)
        initiations = initiation_analysis(messages, gap_hours=6)
        semantic_data = analyze_semantics(messages, toxicity_data=toxicity_data)
        
        features = calculate_features(messages, reply_analysis, sentiment_data, initiations, toxicity_data)
        health_score = compute_health_score(features)
        persona = classifier.predict(features)
        
        coach_narrative = generate_relationship_narrative({
            "participants": list(set(msg.sender for msg in messages)),
            "health_score": health_score,
            "initiations": initiations,
            "features": features
        })


        # --- CORRECTED SUPABASE LOGIC ---
        
        # 1. Check if user exists
        user_query = supabase.table("users").select("id").eq("clerk_id", user_id).execute()
        
        if not user_query.data:
            # 2. Insert new user and get the returned UUID (id)
            new_user = supabase.table("users").insert({"clerk_id": user_id}).execute()
            db_uuid = new_user.data[0]["id"]
        else:
            # 2. Get the existing UUID
            db_uuid = user_query.data[0]["id"]
        
        # 3. Insert analysis using the UUID, NOT the Clerk string
        full_data = {
            "total_messages": len(messages),
            "participants": list(set(msg.sender for msg in messages)),
            "toxicity": toxicity_data,
            "health_score": health_score,
            "persona_tag": persona, 
            "features": features,
            "reply_times": reply_analysis,
            "reply_times": reply_analysis,
            "sentiment": {"total_messages": len(sentiment_data), "timeline": timeline},
            "initiations": initiations,
            "semantic_analysis": semantic_data,
            "coach_summary": coach_narrative,
        }
        
        supabase.table("analyses").insert({
            "user_id": db_uuid,  # This matches your UUID REFERENCES users(id)
            "total_messages": len(messages),
            "health_score": health_score,
            "persona_tag": persona,
            "full_data": full_data
        }).execute()
        
        return full_data
    except Exception as e:
        print(f"Error Detail: {str(e)}") # This will show in your terminal
        raise HTTPException(status_code=500, detail="Database or Analysis Error")
    
@app.get("/history")
async def get_analysis_history(user_id: str = Depends(verify_token)):
    try:
        # 1. Get the internal UUID for this clerk_id
        user_query = supabase.table("users").select("id").eq("clerk_id", user_id).execute()
        
        if not user_query.data:
            return [] # New user, no history yet

        db_uuid = user_query.data[0]["id"]

        # 2. Fetch all analyses for this UUID, sorted by newest first
        history = supabase.table("analyses") \
            .select("id, total_messages, health_score, persona_tag, created_at, full_data") \
            .eq("user_id", db_uuid) \
            .order("created_at", desc=True) \
            .execute()

        return history.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)