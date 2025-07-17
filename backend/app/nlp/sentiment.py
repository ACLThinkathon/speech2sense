from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

class SentimentAnalyzer:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")
        self.model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")
        self.labels = ['negative', 'neutral', 'positive']

    def analyze_sentiment(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
        outputs = self.model(**inputs)
        scores = F.softmax(outputs.logits, dim=1)[0].detach().cpu().numpy()
        max_idx = scores.argmax()
        return self.labels[max_idx]

# Usage
sentiment_analyzer = SentimentAnalyzer()

def analyze_sentiment(text):
    return sentiment_analyzer.analyze_sentiment(text)
