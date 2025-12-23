import requests
from typing import List
from app.models.schema import Message
from dotenv import load_dotenv
import os
load_dotenv()
# Get your free token at: huggingface.co/settings/tokens
HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/unitary/toxic-bert"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def query_toxicity_api(text: str):
    """Sends a single request to the HF Inference API"""
    response = requests.post(API_URL, headers=headers, json={"inputs": text})
    return response.json()

def detect_toxicity(messages: List[Message]):
    toxic_messages = []
    
    for msg in messages:
        if len(msg.message) < 5:
            continue
            
        # The API returns a list of lists: [[{'label': 'toxic', 'score': 0.9}, ...]]
        api_results = query_toxicity_api(msg.message)
        
        # Check if the API returned an error (like model loading)
        if isinstance(api_results, dict) and "error" in api_results:
            continue

        # Convert list of dicts to a single dictionary for easy lookup
        # The API output looks like: [{'label': 'toxic', 'score': 0.98}, ...]
        scores = {item['label']: item['score'] for item in api_results[0]}
        
        is_toxic = any(score > 0.5 for score in scores.values())
        
        if is_toxic:
            toxic_messages.append({
                "timestamp": msg.timestamp,
                "sender": msg.sender,
                "message": msg.message[:100],
                "scores": scores,
                "severity": "high" if scores.get('toxic', 0) > 0.7 else "moderate"
            })
    
    return {
        "toxic_count": len(toxic_messages),
        "toxic_messages": toxic_messages,
        "toxicity_rate": round(len(toxic_messages) / len(messages) * 100, 2) if messages else 0
    }