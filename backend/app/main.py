from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.services.parser import parse_chat
from app.models.schema import UploadResponse, Message
from app.services.sentiment import analyze_sentiment, sentiment_timeline
from app.services.analysis import reply_time_analysis
from app.services.initiation_analysis import initiation_analysis
from app.services.health_score import compute_health_score
from typing import List
from collections import defaultdict
from app.services.toxicity import detect_toxicity

from app.services.cluster import ConversationClassifier
classifier = ConversationClassifier()
app = FastAPI(
    title="CONVOQ API",
    description="Conversation Quality Analysis Backend",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "CONVOQ API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.post("/upload", response_model=UploadResponse)
async def upload_chat(file: UploadFile = File(...)):

    try:
        content = await file.read()
        text = content.decode("utf-8")
        messages = parse_chat(text)
        
        if not messages:
            raise HTTPException(status_code=400, detail="No messages found in file")
        
        return {
            "total_messages": len(messages),
            "messages": messages[:50]  # Return first 50 for preview
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing file: {str(e)}")


# @app.post("/analyze/reply-time")
# async def analyze_reply_time_endpoint(file: UploadFile = File(...)):
#     """
#     Analyze reply times between conversation participants
#     Returns average reply times, fastest and slowest replies
#     """
#     try:
#         content = await file.read()
#         messages = parse_chat(content.decode("utf-8"))
        
#         if len(messages) < 2:
#             raise HTTPException(status_code=400, detail="Need at least 2 messages for analysis")
        
#         result = reply_time_analysis(messages)
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error analyzing reply times: {str(e)}")


# @app.post("/analyze/sentiment")
# async def sentiment_analysis_endpoint(file: UploadFile = File(...)):
#     """
#     Analyze sentiment of conversation over time
#     Returns daily sentiment trends
#     """
#     try:
#         content = await file.read()
#         messages = parse_chat(content.decode("utf-8"))
        
#         if not messages:
#             raise HTTPException(status_code=400, detail="No messages found")
        
#         sentiment_data = analyze_sentiment(messages)
#         timeline = sentiment_timeline(sentiment_data)
        
#         return {
#             "total_messages": len(sentiment_data),
#             "timeline": timeline
#         }
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error analyzing sentiment: {str(e)}")


# @app.post("/analyze/initiation")
# async def initiation_analysis_endpoint(file: UploadFile = File(...), gap_hours: int = 6):
#     """
#     Analyze who initiates conversations
#     gap_hours: Hours of silence to consider a new conversation start
#     """
#     try:
#         content = await file.read()
#         messages = parse_chat(content.decode("utf-8"))
        
#         if not messages:
#             raise HTTPException(status_code=400, detail="No messages found")
        
#         initiations = initiation_analysis(messages, gap_hours=gap_hours)
        
#         return {
#             "gap_hours": gap_hours,
#             "initiations": initiations,
#             "total_conversations": sum(initiations.values())
#         }
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error analyzing initiations: {str(e)}")


@app.post("/complete")
async def complete_analysis(file: UploadFile = File(...)):
    try:
        content = await file.read()
        text = content.decode("utf-8")
        messages = parse_chat(text)
        
        if not messages:
            raise HTTPException(status_code=400, detail="No messages found")
        
        # Run all analyses
        reply_analysis = reply_time_analysis(messages)
        toxicity_data = detect_toxicity(messages)
        sentiment_data = analyze_sentiment(messages)
        timeline = sentiment_timeline(sentiment_data)
        initiations = initiation_analysis(messages, gap_hours=6)
        
        features = calculate_features(messages, reply_analysis, sentiment_data, initiations)
        health_score = compute_health_score(features)

     
        persona = classifier.predict(features)
        
        # metrics_summary = { ... }
        # narrative = generate_relationship_narrative(metrics_summary)
        
        return {
            "total_messages": len(messages),
            "participants": list(set(msg.sender for msg in messages)),
            "toxicity": toxicity_data,
            "health_score": health_score,
            "persona_tag": persona, 
            "features": features,
            "reply_times": reply_analysis,
            "sentiment": {
                "total_messages": len(sentiment_data),
                "timeline": timeline
            },
            "initiations": initiations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in complete analysis: {str(e)}")


def calculate_features(messages: List[Message], reply_analysis: dict, sentiment_data: list, initiations: dict):
    """
    Calculate normalized features (0-1) for health score
    """
    # Reply time balance
    avg_replies = list(reply_analysis["avg_reply_time"].values())
    if len(avg_replies) >= 2:
        reply_balance = min(avg_replies) / max(avg_replies) if max(avg_replies) > 0 else 0.5
    else:
        reply_balance = 0.5
    
    # Initiation balance
    init_counts = list(initiations.values())
    if len(init_counts) >= 2:
        initiation_balance = min(init_counts) / max(init_counts) if max(init_counts) > 0 else 0.5
    else:
        initiation_balance = 0.5
    
    # Sentiment stability (lower variance = more stable)
    sentiments = [s["sentiment"] for s in sentiment_data]
    if sentiments:
        avg_sentiment = sum(sentiments) / len(sentiments)
        variance = sum((s - avg_sentiment) ** 2 for s in sentiments) / len(sentiments)
        sentiment_stability = max(0, 1 - variance)
    else:
        sentiment_stability = 0.5
    
    # Message length balance (simplified)
    msg_lengths = defaultdict(list)
    for msg in messages:
        msg_lengths[msg.sender].append(len(msg.message))
    
    avg_lengths = {sender: sum(lengths) / len(lengths) for sender, lengths in msg_lengths.items()}
    if len(avg_lengths) >= 2:
        length_vals = list(avg_lengths.values())
        msg_length_balance = min(length_vals) / max(length_vals) if max(length_vals) > 0 else 0.5
    else:
        msg_length_balance = 0.5
    
    # Emoji density (placeholder - could be improved)
    emoji_count = sum(1 for msg in messages if any(char in msg.message for char in ['😊', '😂', '❤️', '👍', '🎉']))
    emoji_density = min(emoji_count / len(messages), 1.0) if messages else 0
    
    return {
        "reply_time_balance": round(reply_balance, 3),
        "initiation_balance": round(initiation_balance, 3),
        "sentiment_stability": round(sentiment_stability, 3),
        "msg_length_balance": round(msg_length_balance, 3),
        "emoji_density": round(emoji_density, 3)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)