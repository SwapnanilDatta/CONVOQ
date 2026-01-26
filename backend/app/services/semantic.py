import os
import json
from typing import List, Dict, Optional
from datetime import timedelta
from groq import Groq
from app.models.schema import Message
from app.services.sentiment import sia
from app.services.analysis import parse_timestamp


GROQ_MODEL = "llama-3.1-8b-instant"


def analyze_semantics(
    messages: List[Message],
    gap_minutes: int = 20,
    toxicity_data: Optional[Dict] = None
) -> Dict:

    chunks = build_chunks(messages, gap_minutes)

    suspicious_chunks = filter_suspicious_chunks(chunks, toxicity_data)

    if not suspicious_chunks:
        return {"status": "Peaceful", "events": []}

    result = batch_analyze_with_groq(suspicious_chunks)

    if toxicity_data and toxicity_data.get("toxic_count", 0) > 0:
        result["status"] = "High Tension"

    return result


# ---------------------------
# Chunking
# ---------------------------
def build_chunks(messages: List[Message], gap_minutes: int) -> List[List[Message]]:
    chunks = []
    current = []

    for msg in messages:
        if not current:
            current.append(msg)
            continue

        try:
            curr_time = parse_timestamp(msg.timestamp)
            prev_time = parse_timestamp(current[-1].timestamp)

            if (curr_time - prev_time) > timedelta(minutes=gap_minutes):
                chunks.append(current)
                current = []

            current.append(msg)
        except Exception:
            continue

    if current:
        chunks.append(current)

    return chunks


# ---------------------------
# Cheap filter
# ---------------------------
def filter_suspicious_chunks(chunks: List[List[Message]], toxicity_data: Optional[Dict]) -> List[Dict]:

    trigger_words = {"hate", "wtf", "rude", "stop", "whatever", "bruh"}
    toxic_timestamps = set(m["timestamp"] for m in toxicity_data.get("toxic_messages", [])) if toxicity_data else set()

    suspicious = []

    for chunk in chunks:
        if len(chunk) < 2:
            continue

        messages_text = [m.message for m in chunk]
        blob = " ".join(messages_text).lower()

        sentiment_scores = [sia.polarity_scores(m.message)["compound"] for m in chunk]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)

        trigger_hits = sum(1 for w in trigger_words if w in blob.split())
        contains_known_toxic = any(m.timestamp in toxic_timestamps for m in chunk)

        if avg_sentiment < -0.15 or trigger_hits >= 2 or contains_known_toxic:
            suspicious.append({
                "msgs": [f"{m.sender}: {m.message}" for m in chunk],
                "sentiment": avg_sentiment,
                "timestamp": chunk[0].timestamp
            })

    return sorted(suspicious, key=lambda x: x["sentiment"])[:3]


# ---------------------------
# LLM Judge
# ---------------------------
def batch_analyze_with_groq(chunks: List[Dict]) -> Dict:

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {"status": "Error", "events": []}

    client = Groq(api_key=api_key)

    payload = json.dumps([
        {"id": i, "convo": c["msgs"]}
        for i, c in enumerate(chunks)
    ])

    system_prompt = """
You are a semantic conflict analyst.

For each conversation chunk:
1. Detect if there is abusive or hostile language.
2. Identify:
   - attacker (speaker who initiates hostility or null)
   - target (who it is directed at or null)
   - target_type: one of ["participant", "third_person", "self", "unknown"]
3. Classify interaction type:
   - "Quarrel" ONLY if target_type = participant
   - "Serious" if third_person venting
   - "Banter" if playful teasing

Output ONLY valid JSON:

{
  "events": [
    {
      "id": 0,
      "type": "Quarrel" | "Banter" | "Serious",
      "attacker": "Alice" | null,
      "target": "Bob" | null,
      "target_type": "participant" | "third_person" | "self" | "unknown",
      "confidence": 0.0,
      "summary": "One sentence explanation"
    }
  ]
}
"""

    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            temperature=0.0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze: {payload}"}
            ],
        )

        raw = completion.choices[0].message.content
        parsed = json.loads(raw)

        return build_final_events(parsed, chunks)

    except Exception as e:
        print("Groq error:", e)
        return {"status": "Error", "events": []}


# ---------------------------
# Post processing
# ---------------------------
def build_final_events(parsed: Dict, chunks: List[Dict]) -> Dict:
    final_events = []

    for res in parsed.get("events", []):
        chunk_id = res.get("id")
        if chunk_id is None or chunk_id >= len(chunks):
            continue

        target_type = res.get("target_type", "unknown")

        # 🚫 Downgrade third-person abuse
        if target_type == "third_person":
            event_type = "Serious"
        else:
            event_type = res.get("type", "Serious")

        final_events.append({
            "timestamp": chunks[chunk_id]["timestamp"],
            "type": event_type,
            "summary": res.get("summary"),
            "sentiment_score": chunks[chunk_id]["sentiment"],
            "attacker": res.get("attacker"),
            "target": res.get("target"),
            "target_type": target_type,
            "confidence": res.get("confidence", 0.0)
        })

    return {"status": "Analyzed", "events": final_events}
