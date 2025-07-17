from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.nlp.intent import detect_intent
from app.nlp.sentiment import analyze_sentiment
from app.nlp.summarizer import summarize_text
from app.nlp.topic_modeling import get_topic_distribution
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    sender: str
    text: str


class ConversationRequest(BaseModel):
    messages: List[Message]


@app.post("/analyze/")
async def analyze_conversation(data: ConversationRequest):
    messages_text = [msg.text for msg in data.messages]

    analysis = []
    intents_all = []
    sentiments_all = []
    for msg in data.messages:
        intent = detect_intent(msg.text)
        sentiment = analyze_sentiment(msg.text)
        analysis.append({"sender": msg.sender, "text": msg.text, "intent": intent, "sentiment": sentiment})
        intents_all.append(intent)
        sentiments_all.append(sentiment)

    topic_dist = get_topic_distribution(messages_text)
    dialogue_text = " ".join(messages_text)
    summary = summarize_text(dialogue_text)

    from collections import Counter
    intent_dist = dict(Counter(intents_all))
    sentiment_dist = dict(Counter(sentiments_all))

    return {
        "analysis": analysis,
        "intent_distribution": intent_dist,
        "sentiment_distribution": sentiment_dist,
        "topic_distribution": topic_dist,
        "summary": summary,
    }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
