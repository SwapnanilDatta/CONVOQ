import os
import requests
from typing import List
from app.models.schema import Message
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/unitary/toxic-bert"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# Local backup for common hostile words used in the chat
RED_FLAG_WORDS = {"pathetic", "idiot", "loser", "shut up", "annoying", "suffocating", "hate", "toxic", "stfu"}

def query_toxicity_api(text: str):
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": text}, timeout=5)
        return response.json()
    except:
        return {"error": "connection failed"}

def detect_toxicity(messages: List[Message]):
    toxic_messages = []
    
    for msg in messages:
        text_lower = msg.message.lower()
        
        # FIX: Lowered limit from 5 to 2 to catch "k", "idk", "loser"
        if len(text_lower) < 2:
            continue
            
        # 1. Local Keyword Check (Instant fallback)
        local_toxic = any(word in text_lower for word in RED_FLAG_WORDS)
        
        # 2. API Check
        api_results = query_toxicity_api(msg.message)
        scores = {}
        api_toxic = False

        if isinstance(api_results, list) and len(api_results) > 0:
            scores = {item['label']: item['score'] for item in api_results[0]}
            api_toxic = any(score > 0.5 for score in scores.values())

        # Combine results
        if local_toxic or api_toxic:
            toxic_messages.append({
                "timestamp": msg.timestamp,
                "sender": msg.sender,
                "scores": scores,
                "severity": "high" if (scores.get('toxic', 0) > 0.7 or local_toxic) else "moderate"
            })
    
    return {
        "toxic_count": len(toxic_messages),
        "toxic_messages": toxic_messages,
        "toxicity_rate": round(len(toxic_messages) / len(messages) * 100, 2) if messages else 0
    }