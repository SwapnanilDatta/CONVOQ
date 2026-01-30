import os
from groq import Groq
import json

def generate_relationship_narrative(metrics: dict) -> str:
    """
    Generates a Gen-Z style communication vibe check based on conversation metrics.
    Metrics-only analysis (no message content).
    """

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Coach offline. Drop a GROQ_API_KEY to wake me up."

    client = Groq(api_key=api_key)

    prompt = f"""
    You are analyzing conversation dynamics using quantitative metrics only.

    METRICS:
    - Participants: {metrics.get('participants', 'Unknown')}
    - Health Score: {metrics.get('health_score', 'N/A')}/100
      (Below 50 = unhealthy, 50–70 = mixed, above 70 = healthy)
    - Initiation Balance: {metrics.get('initiations', 'N/A')}
    - Reply Time Balance: {metrics.get('features', {}).get('reply_time_balance', 'N/A')}
      (1.0 = perfectly balanced)
    - Sentiment Stability: {metrics.get('features', {}).get('sentiment_stability', 'N/A')}
      (Lower = volatile emotions)
    - Message Length Balance: {metrics.get('features', {}).get('msg_length_balance', 'N/A')}
      (Lower = one person carrying the convo)

    TASK:
    1. Name the vibe in 3–6 words (e.g., "One-Sided Emotional Labor").
    2. List any Green Flags and Red Flags based on the metrics.
       - If no clear green flag exists, say "No strong green flags detected."
    3. Give exactly 2 sentences of advice focused on healthier communication.

    CONSTRAINTS:
    - Be honest, not polite.
    - Do not force balance if the metrics show imbalance.
    - Do not blame both sides equally if the imbalance is clearly one-sided.

    TONE:
    Gen-Z, concise, insightful. No corporate therapy-speak.
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0.6,
            max_tokens=250,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a blunt but fair relationship coach who calls out "
                        "emotional avoidance, low effort, and imbalance when present."
                    )
                },
                {"role": "user", "content": prompt},
            ],
        )

        return completion.choices[0].message.content.strip()

    except Exception as e:
        print(f"Groq API Error: {e}")
        return "Coach dipped due to an API issue. Check the logs."

def generate_decision_advice(trend_data: dict, recent_messages: list = None) -> dict:
    """
    Generates specific advice and reply suggestions based on the trend decision.
    """
    api_key = os.getenv("GROQ_API_KEY")
    # Default fallback
    fallback = {
        "advice": ["Reflect on your boundaries.", "Consider taking a break."],
        "reply_suggestions": ["Hey, I need some space.", "Can we talk later?", "I've been feeling a bit off about our chats."]
    }

    if not api_key:
        return fallback

    client = Groq(api_key=api_key)

    decision = trend_data.get("decision", "Unknown")
    
    if decision == "Not Enough Data":
        return {
            "advice": [],
            "reply_suggestions": []
        }

    reasons = trend_data.get("reasons", [])
    
    # Format recent messages for context
    msg_context = ""
    if recent_messages:
        msg_context = "RECENT MESSAGES (Use only for tone/style matching, do not analyze content deeply):\n"
        for msg in recent_messages:
            sender = msg.get("sender", "Unknown")
            text = msg.get("message", "")
            msg_context += f"- {sender}: {text}\n"

    prompt = f"""
    The analysis system has output the following decision for a relationship chat history:
    
    DECISION: {decision}
    REASONS DETECTED: {', '.join(reasons)}
    
    {msg_context}
    
    TASK:
    1. Provide 3 specific, actionable bullet points of advice for the user.
    2. Provide 3 specific outcome-oriented text message reply examples the user could send to address the situation.
    
    OUTPUT FORMAT:
    Return valid JSON only:
    {{
        "advice": ["tip 1", "tip 2", "tip 3"],
        "reply_suggestions": ["text 1", "text 2", "text 3"]
    }}
    
    TONE:
    Direct, helpful, and realistic. 
    Crucial: Mimic the user's chatting style (length, capitalization, vibe) from the RECENT MESSAGES for the 'reply_suggestions'.
    If the decision is "Pause/Reconsider", the texts should be firm boundary-setting but still sound like the user.
    If "Continue", they should be engaging and natural.
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=400,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system", 
                    "content": "You are a relationship strategy expert. Return valid JSON only."
                },
                {"role": "user", "content": prompt}
            ]
        )
        
        return json.loads(completion.choices[0].message.content)
        
    except Exception as e:
        print(f"Groq Advice Error: {e}")
        return fallback
