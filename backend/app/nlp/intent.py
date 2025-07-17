from transformers import pipeline

candidate_labels = ["complaint", "inquiry", "feedback"]
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def detect_intent(text):
    result = classifier(text, candidate_labels)
    threshold = 0.3
    intents = []
    for label, score in zip(result['labels'], result['scores']):
        if score > threshold:
            intents.append(label)
    if intents:
        return ", ".join(intents)
    return "unknown"
