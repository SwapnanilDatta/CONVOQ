import os
from groq import Groq


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
