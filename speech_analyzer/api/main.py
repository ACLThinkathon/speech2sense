from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from analyzer.analyzer import analyze_sentences
from analyzer.models import Conversation, Utterance
from api.database import SessionLocal, init_db

app = FastAPI(title="Speech2Sense API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def startup_event():
    init_db()


@app.post("/analyze/", response_model=dict)
async def analyze_conversation(file: UploadFile = File(...), domain: str = None, db: Session = Depends(get_db)):
    if file.content_type != "text/plain":
        raise HTTPException(status_code=400, detail="Only text files are supported")
    content = await file.read()
    text = content.decode("utf-8")

    # Store conversation
    conv = Conversation(raw_text=text)
    db.add(conv)
    db.commit()
    db.refresh(conv)

    # Analyze
    results = analyze_sentences(text, domain)

    # Store utterances with sentiments and intents
    for res in results:
        utterance = Utterance(
            conversation_id=conv.id,
            speaker=res["speaker"],
            sentence=res["sentence"],
            sentiment=res["sentiment"],
            score=res["score"],
            reason=res["reason"],
            intent=res.get("intent", "unknown"),
            intent_reason=res.get("intent_reason", "")
        )
        db.add(utterance)
    db.commit()

    return {
        "conversation_id": conv.id,
        "results": results
    }


@app.get("/conversations/{conversation_id}", response_model=dict)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    utterances = [{
        "speaker": u.speaker,
        "sentence": u.sentence,
        "sentiment": u.sentiment,
        "score": u.score,
        "reason": u.reason,
        "intent": getattr(u, "intent", "unknown"),
        "intent_reason": getattr(u, "intent_reason", "")
    } for u in conv.utterances]
    return {
        "conversation_id": conv.id,
        "raw_text": conv.raw_text,
        "utterances": utterances
    }
