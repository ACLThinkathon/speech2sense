from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from groq import Groq
import uvicorn

app = FastAPI()

# Enable CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key="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")


def extract_speaker_utterances(text):
    lines = text.strip().split("\n")
    utterances = []
    for line in lines:
        if ":" in line:
            speaker, message = line.split(":", 1)
            speaker = speaker.strip()
            message = message.strip()
            if speaker and message:
                utterances.append((speaker, message))
    return utterances


def analyze_sentences(text, domain=None):
    utterances = extract_speaker_utterances(text)
    results = []

    sentiment_prompt = (
        "You are an expert sentiment analysis system trained across multiple industries "
        "including ecommerce, healthcare, real estate, and customer support.\n\n"
        "Your task is to analyze each sentence and classify the sentiment into one of the following:\n"
        "- \"extreme positive\": highly enthusiastic, delighted, grateful\n"
        "- \"positive\": satisfied, content, pleased\n"
        "- \"neutral\": factual, polite, or emotionally flat\n"
        "- \"negative\": unsatisfied, concerned, or mildly critical\n"
        "- \"extreme negative\": angry, highly critical, frustrated, or alarmed\n\n"
        "Classify based on **emotional tone**, even if wording is polite. For example, "
        "'I guess it's fine' might still be negative depending on tone. Interpret sarcasm and indirect emotions.\n\n"
        "Return ONLY in this exact JSON format:\n"
        "{"
        "\"sentiment\": \"extreme positive|positive|neutral|negative|extreme negative\", "
        "\"score\": float between 0 and 1, "
        "\"reason\": \"Short explanation why this sentiment applies\""
        "}"
    )

    intent_prompt = (
        "You are an intelligent system designed to identify the **intent** behind customer service messages.\n\n"
        "Your task is to classify the intent into one or more of the following categories:\n"
        "- \"complaint\": expressing dissatisfaction, reporting issues\n"
        "- \"inquiry\": asking for information, clarifying something\n"
        "- \"feedback\": giving opinions, suggestions, praise, or critique\n\n"
        "Return ONLY in this JSON format:\n"
        "{\"intent\": \"complaint|inquiry|feedback|multiple|unknown\"}"
    )

    system_msg_sentiment = {"role": "system", "content": sentiment_prompt}
    system_msg_intent = {"role": "system", "content": intent_prompt}

    few_shot_examples = [
        {"role": "user", "content": "The support was phenomenal! I couldn’t be happier."},
        {"role": "assistant",
         "content": '{"sentiment": "extreme positive", "score": 0.95, "reason": "Very enthusiastic and joyful tone"}'},
        {"role": "user", "content": "It's okay I guess. Nothing special."},
        {"role": "assistant",
         "content": '{"sentiment": "neutral", "score": 0.5, "reason": "Factual and indifferent tone"}'},
        {"role": "user", "content": "Thanks for your help, but I’m still waiting for a resolution."},
        {"role": "assistant",
         "content": '{"sentiment": "negative", "score": 0.4, "reason": "Underlying dissatisfaction despite politeness"}'},
        {"role": "user", "content": "This has been a horrible experience. I will never use this service again."},
        {"role": "assistant",
         "content": '{"sentiment": "extreme negative", "score": 0.9, "reason": "Strong frustration and refusal to return"}'},
        {"role": "user", "content": "Really appreciate the quick fix! Saved my day."},
        {"role": "assistant",
         "content": '{"sentiment": "positive", "score": 0.8, "reason": "Gratitude and satisfaction with service"}'}
    ]

    for speaker, sentence in utterances:
        sentiment_result = {}
        intent_result = {}

        try:
            sentiment_response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[system_msg_sentiment] + few_shot_examples + [{"role": "user", "content": sentence}],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            sentiment_result = eval(sentiment_response.choices[0].message.content)
        except Exception as e:
            sentiment_result = {
                "sentiment": "neutral",
                "score": 0.5,
                "reason": f"Error during sentiment analysis: {str(e)}"
            }

        try:
            intent_response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[system_msg_intent, {"role": "user", "content": sentence}],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            intent_result = eval(intent_response.choices[0].message.content)
        except Exception as e:
            intent_result = {"intent": "unknown"}

        results.append({
            "speaker": speaker,
            "sentence": sentence,
            "sentiment": sentiment_result["sentiment"],
            "score": sentiment_result["score"],
            "reason": sentiment_result["reason"],
            "intent": intent_result["intent"],
            # "intent_reason": intent_result.get("reason", "Detected intent via classifier.")
        })

    return results


@app.post("/analyze/")
async def analyze(file: UploadFile = File(...), domain: str = Form(None)):
    content = await file.read()
    text = content.decode("utf-8")
    results = analyze_sentences(text, domain)
    return JSONResponse({"results": results})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
