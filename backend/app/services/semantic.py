import os
import json
from typing import List, Dict, Optional
from datetime import timedelta
from app.models.schema import Message
from app.services.sentiment import sia 
from app.services.analysis import parse_timestamp 
from groq import Groq

def analyze_semantics(messages: List[Message], gap_minutes: int = 20, toxicity_data: Optional[Dict] = None) -> Dict:
    """
    Production-grade semantic pipeline with Toxicity integration.
    """
    
    # --- Step 1: Create Interaction Windows (Chunks) ---
    chunks = []
    current_chunk = []
    
    for i, msg in enumerate(messages):
        if not current_chunk:
            current_chunk.append(msg)
            continue
            
        try:
            curr_time = parse_timestamp(msg.timestamp)
            prev_time = parse_timestamp(current_chunk[-1].timestamp)
            
            if (curr_time - prev_time) > timedelta(minutes=gap_minutes):
                chunks.append(current_chunk)
                current_chunk = []
            
            current_chunk.append(msg)
        except:
            continue
            
    if current_chunk:
        chunks.append(current_chunk)

    # --- Step 2: The "Cheap" Filter (Local) ---
    suspicious_chunks = []
    trigger_words = {"hate", "blocking", "wtf", "rude", "stop", "whatever", "k", "fine", "dead", "bruh"}
    
    # Extract timestamps of messages flagged as toxic by toxicity.py
    toxic_timestamps = set()
    if toxicity_data and "toxic_messages" in toxicity_data:
        toxic_timestamps = {m["timestamp"] for m in toxicity_data["toxic_messages"]}
    
    for chunk in chunks:
        if len(chunk) < 2: # Lowered limit to catch short but toxic interactions
            continue
            
        text_blob = " ".join([m.message.lower() for m in chunk])
        scores = [sia.polarity_scores(m.message)['compound'] for m in chunk]
        avg_sentiment = sum(scores) / len(scores)
        trigger_count = sum(1 for word in trigger_words if word in text_blob.split())
        
        # Check if this chunk contains any message already flagged as toxic
        contains_known_toxicity = any(m.timestamp in toxic_timestamps for m in chunk)
        
        # FILTER LOGIC:
        # 1. High negative sentiment OR trigger words
        # 2. OR Known toxicity detected by the Toxic-BERT/Keyword model
        is_suspicious = (avg_sentiment < -0.15) or (trigger_count >= 2) or contains_known_toxicity
        
        if is_suspicious:
            formatted_convo = [f"{m.sender}: {m.message}" for m in chunk]
            suspicious_chunks.append({
                "msgs": formatted_convo,
                "sentiment": avg_sentiment,
                "timestamp": chunk[0].timestamp
            })

    # Sort by intensity and limit to top 3
    suspicious_chunks = sorted(suspicious_chunks, key=lambda x: x['sentiment'])[:3]

    # --- Step 3: The "Expensive" Judge ---
    if not suspicious_chunks:
        return {"status": "Peaceful", "events": []}

    # If toxicity exists but no "events" were categorized yet, we force an "Analyzed" status
    # to prevent the Frontend from showing the "Immaculate" green box.
    result = batch_analyze_with_groq(suspicious_chunks)
    
    if toxicity_data and toxicity_data.get("toxic_count", 0) > 0:
        result["status"] = "High Tension" # This overrides "Peaceful"
        
    return result

def batch_analyze_with_groq(chunks: List[Dict]) -> Dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {"error": "No API Key"}

    client = Groq(api_key=api_key)
    prompt_content = json.dumps([{ "id": i, "convo": c["msgs"] } for i, c in enumerate(chunks)])

    system_prompt = """
    You are an expert semantic analyst. Analyze these conversation chunks. 
    Classify as "Quarrel", "Banter", or "Serious".
    
    Output ONLY valid JSON:
    {
      "events": [
        {
          "id": 0,
          "type": "Quarrel" | "Banter" | "Serious",
          "confidence": 0.9,
          "summary": "Brief 1-sentence explanation."
        }
      ]
    }
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze: {prompt_content}"}
            ],
            temperature=0.0,
            response_format={"type": "json_object"} 
        )
        
        raw_content = completion.choices[0].message.content
        analysis_result = json.loads(raw_content)
        
        final_events = []
        results_list = analysis_result.get("events", [])
        
        for res in results_list:
            chunk_id = res.get("id")
            if chunk_id is not None and chunk_id < len(chunks):
                final_events.append({
                    "timestamp": chunks[chunk_id]["timestamp"],
                    "type": res.get("type"),
                    "summary": res.get("summary"),
                    "sentiment_score": chunks[chunk_id]["sentiment"]
                })
                
        return {"status": "Analyzed", "events": final_events}

    except Exception as e:
        print(f"Groq Error: {e}")
        return {"status": "Error", "events": []}