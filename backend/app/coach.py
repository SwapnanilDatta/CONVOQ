import os
from google import generativeai as genai 
genai.configure(api_key="YOUR_GEMINI_API_KEY")

def generate_relationship_narrative(metrics: dict):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Constructing the context-rich prompt
    prompt = f"""
    Analyze the following WhatsApp conversation metrics and provide a "Communication Vibe Check."
    
    METRICS:
    - Participants: {metrics['participants']}
    - Health Score: {metrics['health_score']}/100
    - Initiation: {metrics['initiations']}
    - Reply Time Balance: {metrics['features']['reply_time_balance']} (1.0 is perfect balance)
    - Sentiment Stability: {metrics['features']['sentiment_stability']}
    - Msg Length Balance: {metrics['features']['msg_length_balance']}
    
    TASK:
    1. Summarize the vibe (e.g., "The Supportive Bestie", "The One-Sided Pursuit", "The High-Energy Duo").
    2. Identify one "Green Flag" and one "Red Flag" based on the balance metrics.
    3. Give a 2-sentence advice for improving the connection.
    
    TONE: Gen-Z / Minimalist / Insightful. Do not be overly formal.
    """
    
    response = model.generate_content(prompt)
    return response.text