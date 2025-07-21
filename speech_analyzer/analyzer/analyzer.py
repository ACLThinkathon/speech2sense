from groq import Groq

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

    system_prompt = (
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

    if domain:
        system_prompt += f"\n\nThis input is from a conversation in the '{domain}' domain. Take domain-specific language and tone into account."

    system_msg = {"role": "system", "content": system_prompt}

    few_shot_examples = [
        {"role": "user", "content": "The support was phenomenal! I couldn’t be happier."},
        {"role": "assistant", "content": '{"sentiment": "extreme positive", "score": 0.95, "reason": "Very enthusiastic and joyful tone"}'},
        {"role": "user", "content": "It's okay I guess. Nothing special."},
        {"role": "assistant", "content": '{"sentiment": "neutral", "score": 0.5, "reason": "Factual and indifferent tone"}'},
        {"role": "user", "content": "Thanks for your help, but I’m still waiting for a resolution."},
        {"role": "assistant", "content": '{"sentiment": "negative", "score": 0.4, "reason": "Underlying dissatisfaction despite politeness"}'},
        {"role": "user", "content": "This has been a horrible experience. I will never use this service again."},
        {"role": "assistant", "content": '{"sentiment": "extreme negative", "score": 0.9, "reason": "Strong frustration and refusal to return"}'},
        {"role": "user", "content": "Really appreciate the quick fix! Saved my day."},
        {"role": "assistant", "content": '{"sentiment": "positive", "score": 0.8, "reason": "Gratitude and satisfaction with service"}'}
    ]

    for speaker, sentence in utterances:
        user_msg = {"role": "user", "content": sentence}
        try:
            res = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[system_msg] + few_shot_examples + [user_msg],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            data = res.choices[0].message.content
            entry = eval(data)
        except Exception as e:
            entry = {
                "sentiment": "neutral",
                "score": 0.5,
                "reason": f"Error during analysis: {str(e)}"
            }

        results.append({
            "speaker": speaker,
            "sentence": sentence,
            "sentiment": entry["sentiment"],
            "score": entry["score"],
            "reason": entry["reason"]
        })

    return results
