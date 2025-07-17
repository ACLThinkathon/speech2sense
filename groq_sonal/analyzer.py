from groq import Groq
import re

# Use your actual Groq API key here
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

def analyze_sentences(text):
    utterances = extract_speaker_utterances(text)
    results = []

    for speaker, sentence in utterances:
        system_msg = {
            "role": "system",
            "content": (
                "You are a sentiment analysis expert. Given a sentence, classify the sentiment as "
                "\"positive\", \"neutral\", or \"negative\" based on the emotional content, even if it is polite. "
                "For example, a polite sentence expressing frustration is still negative.\n\n"
                "Return output in JSON with: "
                "{\"sentiment\": \"positive/neutral/negative\", \"score\": float (0–1), \"reason\": \"...\"}"
            )
        }
        user_msg = {"role": "user", "content": sentence}

        try:
            res = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[system_msg, user_msg],
                response_format={"type": "json_object"}
            )
            data = res.choices[0].message.content
            entry = eval(data)
        except Exception as e:
            entry = {"sentiment": "neutral", "score": 0.5, "reason": "Error during analysis"}

        results.append({
            "speaker": speaker,
            "sentence": sentence,
            "sentiment": entry["sentiment"],
            "score": entry["score"],
            "reason": entry["reason"]
        })

    return results
