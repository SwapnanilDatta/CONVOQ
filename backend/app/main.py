from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from app.parser import parse_chat
from app.schema import UploadResponse

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
        "messages": messages[:50]  # limit for now
    }
