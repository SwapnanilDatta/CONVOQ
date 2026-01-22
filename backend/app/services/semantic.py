import os
import json
from typing import List, Dict
from datetime import timedelta
from app.models.schema import Message
from app.services.sentiment import sia  # Reusing your existing VADER instance
from app.services.analysis import parse_timestamp # Reusing your timestamp parser
from groq import Groq

def analyze_semantics(messages: List[Message], gap_minutes: int = 20) -> Dict:
    """
    Production-grade semantic pipeline:
    1. Chunk messages by time gaps.
    2. FILTER: Run local heuristic (sentiment + keywords) to find "Suspicious" chunks.
    3. JUDGE: Send only suspicious chunks to Groq LLM for classification.
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
    
    # Keywords that might indicate conflict (Gen Z + Standard)
    trigger_words = {"hate", "blocking", "wtf", "rude", "stop", "whatever", "k", "fine", "dead", "bruh"}
    
    for chunk in chunks:
        # Skip noise: chunks too short are rarely deep semantic events
        if len(chunk) < 4:
            continue
            
        # Calculate Chunk Vibe
        text_blob = " ".join([m.message.lower() for m in chunk])
        scores = [sia.polarity_scores(m.message)['compound'] for m in chunk]
        avg_sentiment = sum(scores) / len(scores)
        
        # Count Trigger Words
        trigger_count = sum(1 for word in trigger_words if word in text_blob.split())
        
        # THE FILTER LOGIC
        # 1. High negative sentiment
        # 2. OR Multiple trigger words present
        is_suspicious = (avg_sentiment < -0.15) or (trigger_count >= 2)
        
        if is_suspicious:
            # Format for LLM: "User: Message"
            formatted_convo = [f"{m.sender}: {m.message}" for m in chunk]
            suspicious_chunks.append({
                "msgs": formatted_convo,
                "sentiment": avg_sentiment,
                "timestamp": chunk[0].timestamp
            })

    # Limit to top 3 most intense chunks to save API tokens
    suspicious_chunks = sorted(suspicious_chunks, key=lambda x: x['sentiment'])[:3]

    # --- Step 3: The "Expensive" Judge (Groq LLM) ---
    if not suspicious_chunks:
        return {"status": "Peaceful", "events": []}

    return batch_analyze_with_groq(suspicious_chunks)

def batch_analyze_with_groq(chunks: List[Dict]) -> Dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {"error": "No API Key"}

    client = Groq(api_key=api_key)

    # We pack multiple chunks into ONE prompt to save network calls
    prompt_content = json.dumps([{ "id": i, "convo": c["msgs"] } for i, c in enumerate(chunks)])

    system_prompt = """
    You are an expert semantic analyst. Analyze these conversation chunks. 
    For each chunk, determine if it is a "Quarrel", "Misunderstanding", "Vent", or "Banter" (Playful fighting).
    
    Output ONLY valid JSON in this format:
    [
      {
        "id": 0,
        "type": "Quarrel" | "Banter" | "Serious",
        "confidence": 0.9,
        "summary": "Brief 1-sentence explanation of what happened."
      }
    ]
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze these conversations: {prompt_content}"}
            ],
            temperature=0.0,
            response_format={"type": "json_object"} 
        )
        
        analysis_result = json.loads(completion.choices[0].message.content)
        
        # Merge LLM results back with timestamp data
        final_events = []
        # Handle case where LLM returns a dict with a key 'events' or just a list
        results_list = analysis_result if isinstance(analysis_result, list) else analysis_result.get("events", analysis_result.get("analysis", []))
        
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
        print(f"Semantic Analysis Error: {e}")
        return {"status": "Error", "events": []}