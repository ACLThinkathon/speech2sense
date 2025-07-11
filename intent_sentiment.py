from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

# Intent model
intent_model = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
intent_labels = ["complaint", "inquiry", "feedback"]

# Sentiment model
sentiment_checkpoint = "cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(sentiment_checkpoint)
model = AutoModelForSequenceClassification.from_pretrained(sentiment_checkpoint)
sentiment_model = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# Map label IDs to friendly labels
label_map = {
    "LABEL_0": "negative",
    "LABEL_1": "neutral",
    "LABEL_2": "positive"
}


def analyze_message(message):
    intent_result = intent_model(message, candidate_labels=intent_labels, multi_label=True)
    top_intents = {label: round(score, 2) for label, score in zip(intent_result["labels"], intent_result["scores"])}

    sentiment_raw = sentiment_model(message)[0]
    sentiment = {
        "label": label_map.get(sentiment_raw["label"], sentiment_raw["label"]),
        "score": round(sentiment_raw["score"], 2)
    }

    return {
        "message": message,
        "intents": top_intents,
        "sentiment": sentiment
    }
