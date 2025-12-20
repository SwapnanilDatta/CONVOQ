from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from app.parser import parse_chat
from app.schema import UploadResponse
from app.sentiment import analyze_sentiment, sentiment_timeline
from app.analysis import reply_time_analysis
app = FastAPI(title="CONVOQ API")

# CORS (VERY IMPORTANT for React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.post("/upload", response_model=UploadResponse)
async def upload_chat(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8")

    messages = parse_chat(text)

    return {
        "total_messages": len(messages),
        "messages": messages[:50] 
    }

@app.post("/analyze/reply-time")
async def analyze_reply_time(file: UploadFile = File(...)):
    content = await file.read()
    messages = parse_chat(content.decode("utf-8"))

    result = reply_time_analysis(messages)
    return result

@app.post("/analyze/sentiment")
async def sentiment_analysis(file: UploadFile = File(...)):
    content = await file.read()
    messages = parse_chat(content.decode("utf-8"))

    sentiment_data = analyze_sentiment(messages)
    timeline = sentiment_timeline(sentiment_data)

    return {
        "total_messages": len(sentiment_data),
        "timeline": timeline
    }