from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from groq import Groq
import uvicorn
import logging
import json
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("analyzer_errors.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Enhanced Speech2Sense API", version="2.0.0")

# Enable CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq client
try:
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    client = Groq(api_key=groq_api_key)
    logger.info("Groq client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {str(e)}")
    client = None


def extract_speaker_utterances(text: str) -> List[Tuple[str, str]]:
    """Enhanced speaker utterance extraction with better error handling"""
    try:
        lines = text.strip().split("\n")
        utterances = []

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            if ":" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    speaker, message = parts
                    speaker = speaker.strip()
                    message = message.strip()

                    if speaker and message:
                        # Standardize speaker names
                        if any(word in speaker.lower() for word in ['agent', 'support', 'rep', 'staff']):
                            speaker = "Agent"
                        elif any(word in speaker.lower() for word in ['customer', 'client', 'user', 'caller']):
                            speaker = "Customer"

                        utterances.append((speaker, message))
                    else:
                        logger.warning(f"Empty speaker or message on line {line_num}: {line}")
            else:
                logger.warning(f"No speaker delimiter found on line {line_num}: {line}")

        logger.info(f"Extracted {len(utterances)} utterances from conversation")
        return utterances

    except Exception as e:
        logger.error(f"Error extracting speaker utterances: {str(e)}")
        return []


def detect_topics(text: str) -> Dict:
    """Enhanced topic detection using LLM"""
    try:
        if not client:
            return {"topics": ["general"], "primary_topic": "general", "confidence": 0.5}

        topic_prompt = """
        You are an expert topic classifier for customer service conversations.

        Analyze the conversation and identify relevant topics from these categories:
        - "billing": payment issues, charges, invoices, refunds
        - "technical_support": software/hardware problems, troubleshooting, setup
        - "product_inquiry": questions about features, specifications, availability
        - "account_management": login issues, profile changes, account settings
        - "shipping": delivery, tracking, shipping methods, delays
        - "returns_exchanges": product returns, exchanges, warranty claims
        - "complaint": service issues, dissatisfaction, negative experiences
        - "compliment": praise, positive feedback, satisfaction
        - "general_inquiry": general questions, information requests
        - "cancellation": service termination, subscription cancellation

        Return ONLY in this exact JSON format:
        {
            "topics": ["list", "of", "relevant", "topics"],
            "primary_topic": "most_relevant_topic",
            "confidence": 0.85,
            "reasoning": "Brief explanation of topic classification"
        }
        """

        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": topic_prompt},
                {"role": "user", "content": f"Conversation text: {text}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )

        result = json.loads(response.choices[0].message.content)
        logger.info(f"Topic detection successful: {result.get('primary_topic', 'unknown')}")
        return result

    except Exception as e:
        logger.error(f"Error in topic detection: {str(e)}")
        return {
            "topics": ["general"],
            "primary_topic": "general",
            "confidence": 0.5,
            "reasoning": f"Error during topic analysis: {str(e)}"
        }


def normalize_sentiment_score(sentiment_label: str, raw_score: float) -> float:
    """Normalize sentiment score to match the sentiment label"""
    sentiment_label = sentiment_label.lower()

    # Map sentiment labels to appropriate score ranges
    if sentiment_label == "extreme positive":
        return max(0.85, min(1.0, raw_score)) if raw_score > 0.5 else 0.9
    elif sentiment_label == "positive":
        return max(0.65, min(0.84, raw_score)) if raw_score > 0.5 else 0.75
    elif sentiment_label == "neutral":
        return max(0.45, min(0.64, raw_score)) if abs(raw_score - 0.5) < 0.15 else 0.5
    elif sentiment_label == "negative":
        return min(0.35, max(0.15, raw_score)) if raw_score < 0.5 else 0.25
    elif sentiment_label == "extreme negative":
        return min(0.14, max(0.0, raw_score)) if raw_score < 0.5 else 0.1
    else:
        return raw_score  # fallback to original score


def calculate_csat_score(utterances: List[Dict]) -> Dict:
    """Calculate CSAT score based on customer sentiment and resolution indicators"""
    try:
        customer_utterances = [u for u in utterances if u.get('speaker', '').lower() == 'customer']

        if not customer_utterances:
            return {"csat_score": 0, "csat_rating": "No customer data", "methodology": "No customer utterances found"}

        # Calculate weighted score with proper recency bias and normalized scores
        total_weighted_score = 0
        total_weight = 0

        for i, utterance in enumerate(customer_utterances):
            # Progressive weighting: later utterances get more weight (1.0 to 2.5)
            weight = 1.0 + (i / max(1, len(customer_utterances) - 1)) * 1.5

            # Get normalized score based on sentiment label
            sentiment_label = utterance.get('sentiment', 'neutral')
            raw_score = utterance.get('score', 0.5)
            normalized_score = normalize_sentiment_score(sentiment_label, raw_score)

            total_weighted_score += normalized_score * weight
            total_weight += weight

        # Calculate final CSAT score (0-100 scale)
        if total_weight > 0:
            avg_score = total_weighted_score / total_weight
            csat_score = avg_score * 100
        else:
            csat_score = 50

        # Determine CSAT rating with appropriate thresholds
        if csat_score >= 80:
            csat_rating = "Excellent"
        elif csat_score >= 65:
            csat_rating = "Good"
        elif csat_score >= 50:
            csat_rating = "Satisfactory"
        elif csat_score >= 30:
            csat_rating = "Poor"
        else:
            csat_rating = "Very Poor"

        # Additional analysis for context
        sentiment_distribution = {}
        for utterance in customer_utterances:
            sentiment = utterance.get('sentiment', 'neutral')
            sentiment_distribution[sentiment] = sentiment_distribution.get(sentiment, 0) + 1

        return {
            "csat_score": round(csat_score, 1),
            "csat_rating": csat_rating,
            "methodology": f"Weighted average of {len(customer_utterances)} customer sentiment scores with recency "
                           f"bias and normalization",
            "customer_utterances_count": len(customer_utterances),
            "sentiment_distribution": sentiment_distribution,
            "final_customer_sentiment": customer_utterances[-1].get('sentiment',
                                                                    'neutral') if customer_utterances else 'none'
        }

    except Exception as e:
        logger.error(f"Error calculating CSAT score: {str(e)}")
        return {"csat_score": 0, "csat_rating": "Error", "methodology": f"Error: {str(e)}"}


def calculate_agent_performance(utterances: List[Dict]) -> Dict:
    """Calculate comprehensive agent performance metrics"""
    try:
        agent_utterances = [u for u in utterances if u.get('speaker', '').lower() == 'agent']
        customer_utterances = [u for u in utterances if u.get('speaker', '').lower() == 'customer']

        if not agent_utterances:
            return {"error": "No agent utterances found for performance analysis"}

        # 1. Agent sentiment consistency (normalized scores)
        agent_normalized_scores = []
        for utterance in agent_utterances:
            sentiment_label = utterance.get('sentiment', 'neutral')
            raw_score = utterance.get('score', 0.5)
            normalized_score = normalize_sentiment_score(sentiment_label, raw_score)
            agent_normalized_scores.append(normalized_score)

        avg_agent_sentiment = sum(agent_normalized_scores) / len(agent_normalized_scores)

        # 2. Response quality indicators (professional keywords)
        positive_keywords = ['help', 'assist', 'solve', 'resolve', 'understand', 'sorry', 'apologize',
                             'thank', 'please', 'certainly', 'absolutely', 'definitely', 'glad', 'happy',
                             'everything', 'right', 'fix', 'support']
        professional_responses = 0

        for utterance in agent_utterances:
            text = utterance.get('sentence', '').lower()
            if any(keyword in text for keyword in positive_keywords):
                professional_responses += 1

        professionalism_score = (professional_responses / len(agent_utterances)) * 100

        # 3. Customer sentiment improvement using normalized scores
        customer_improvement = 0
        if len(customer_utterances) >= 2:
            # Get normalized scores for first and last customer utterances
            first_sentiment = customer_utterances[0].get('sentiment', 'neutral')
            first_raw_score = customer_utterances[0].get('score', 0.5)
            first_normalized = normalize_sentiment_score(first_sentiment, first_raw_score)

            last_sentiment = customer_utterances[-1].get('sentiment', 'neutral')
            last_raw_score = customer_utterances[-1].get('score', 0.5)
            last_normalized = normalize_sentiment_score(last_sentiment, last_raw_score)

            # Calculate improvement as absolute change
            customer_improvement = (last_normalized - first_normalized) * 100

        elif len(customer_utterances) == 1:
            # Single customer utterance - penalize if negative
            sentiment = customer_utterances[0].get('sentiment', 'neutral')
            if sentiment in ['negative', 'extreme negative']:
                customer_improvement = -25
            else:
                customer_improvement = 0

        # 4. Issue resolution indicator based on final customer sentiment
        resolution_score = 50  # Default neutral
        if customer_utterances:
            final_customer_sentiment = customer_utterances[-1].get('sentiment', 'neutral')

            if final_customer_sentiment == 'extreme positive':
                resolution_score = 95
            elif final_customer_sentiment == 'positive':
                resolution_score = 80
            elif final_customer_sentiment == 'neutral':
                resolution_score = 60
            elif final_customer_sentiment == 'negative':
                resolution_score = 25
            else:  # extreme negative
                resolution_score = 10

        # 5. Calculate overall performance score with balanced weighting
        agent_component = avg_agent_sentiment * 100 * 0.30  # Agent professionalism (30%)
        professional_component = professionalism_score * 0.30  # Professional language (30%)
        improvement_component = max(0, 50 + customer_improvement) * 0.20  # Customer improvement (20%)
        resolution_component = resolution_score * 0.20  # Issue resolution (20%)

        performance_score = agent_component + professional_component + improvement_component + resolution_component

        # Ensure score is within bounds
        performance_score = max(0, min(100, int(performance_score)))

        # Performance rating with adjusted thresholds
        if performance_score >= 80:
            rating = "Excellent"
        elif performance_score >= 65:
            rating = "Good"
        elif performance_score >= 50:
            rating = "Satisfactory"
        elif performance_score >= 35:
            rating = "Needs Improvement"
        else:
            rating = "Poor"

        return {
            "overall_score": round(performance_score, 1),
            "rating": rating,
            "agent_sentiment_avg": round(avg_agent_sentiment, 2),
            "professionalism_score": round(professionalism_score, 1),
            "customer_sentiment_improvement": round(customer_improvement, 1),
            "resolution_score": round(resolution_score, 1),
            "total_responses": len(agent_utterances),
            "professional_responses": professional_responses,
            "metrics_breakdown": {
                "agent_professionalism": round(agent_component, 1),
                "professional_language": round(professional_component, 1),
                "customer_improvement": round(improvement_component, 1),
                "issue_resolution": round(resolution_component, 1)
            }
        }

    except Exception as e:
        logger.error(f"Error calculating agent performance: {str(e)}")
        return {"error": f"Performance calculation failed: {str(e)}"}


def analyze_sentences(text: str, domain: Optional[str] = None) -> Dict:
    """Enhanced sentence analysis with comprehensive error handling"""
    try:
        if not text or not text.strip():
            raise ValueError("Empty or invalid text provided")

        # Extract utterances
        utterances = extract_speaker_utterances(text)
        if not utterances:
            raise ValueError("No valid speaker utterances found in the text")

        # Detect topics
        topic_analysis = detect_topics(text)

        results = []

        # Enhanced prompts
        sentiment_prompt = """
        You are an expert sentiment analysis system trained across multiple industries.

        Analyze each sentence and classify sentiment into:
        - "extreme positive": highly enthusiastic, delighted, grateful
        - "positive": satisfied, content, pleased  
        - "neutral": factual, polite, emotionally flat
        - "negative": unsatisfied, concerned, mildly critical
        - "extreme negative": angry, highly critical, frustrated

        Consider context, tone, and domain-specific language.

        Classify based on **emotional tone**, even if wording is polite. For example, 
        'I guess it's fine' might still be negative depending on tone. Interpret sarcasm and indirect emotions.

        Return ONLY in this exact JSON format:
        {
            "sentiment": "extreme positive|positive|neutral|negative|extreme negative",
            "score": float between 0 and 1,
            "reason": "Detailed explanation of sentiment classification",
            "keywords": ["key", "emotional", "words"],
            "confidence": float between 0 and 1
        }
        """

        # Few-shot examples for better grounding
        few_shot_examples = [
            {"role": "user", "content": "The support was phenomenal! I couldn't be happier."},
            {"role": "assistant",
             "content": '{"sentiment": "extreme positive", "score": 0.95, "reason": "Very enthusiastic '
                        'and joyful tone"}'},
            {"role": "user", "content": "It's okay I guess. Nothing special."},
            {"role": "assistant",
             "content": '{"sentiment": "neutral", "score": 0.5, "reason": "Factual and indifferent tone"}'},
            {"role": "user", "content": "Thanks for your help, but I'm still waiting for a resolution."},
            {"role": "assistant",
             "content": '{"sentiment": "negative", "score": 0.4, "reason": "Underlying dissatisfaction despite '
                        'politeness"}'},
            {"role": "user", "content": "This has been a horrible experience. I will never use this service again."},
            {"role": "assistant",
             "content": '{"sentiment": "extreme negative", "score": 0.9, "reason": "Strong frustration and refusal '
                        'to return"}'},
            {"role": "user", "content": "Really appreciate the quick fix! Saved my day."},
            {"role": "assistant",
             "content": '{"sentiment": "positive", "score": 0.8, "reason": "Gratitude and satisfaction with service"}'}
        ]

        intent_prompt = """
        You are an intelligent intent classification system.

        Classify the intent into one or more categories:
        - "complaint": expressing dissatisfaction, reporting issues
        - "inquiry": asking for information, clarifying something  
        - "feedback": giving opinions, suggestions, praise, critique
        - "request": asking for action, service, or assistance
        - "acknowledgment": confirming, agreeing, thanking
        - "escalation": demanding supervisor, threatening action

        Return ONLY in this JSON format:
        {
            "intent": "primary_intent",
            "secondary_intents": ["list", "of", "secondary"],
            "confidence": float between 0 and 1,
            "reasoning": "Explanation of intent classification"
        }
        """

        # System messages
        system_msg_sentiment = {"role": "system", "content": sentiment_prompt}
        system_msg_intent = {"role": "system", "content": intent_prompt}

        # Process each utterance
        for i, (speaker, sentence) in enumerate(utterances):
            try:
                logger.info(f"Processing utterance {i + 1}/{len(utterances)} from {speaker}")

                # Sentiment analysis
                sentiment_result = {"sentiment": "neutral", "score": 0.5, "reason": "Default", "keywords": [],
                                    "confidence": 0.5}
                if client:
                    try:
                        sentiment_response = client.chat.completions.create(
                            model="llama3-8b-8192",
                            messages=[system_msg_sentiment] + few_shot_examples + [
                                {"role": "user", "content": sentence}],
                            response_format={"type": "json_object"},
                            temperature=0.2
                        )
                        sentiment_result = json.loads(sentiment_response.choices[0].message.content)
                    except Exception as e:
                        logger.warning(f"Sentiment analysis failed for utterance {i + 1}: {str(e)}")

                # Intent analysis
                intent_result = {"intent": "unknown", "secondary_intents": [], "confidence": 0.5,
                                 "reasoning": "Default"}
                if client:
                    try:
                        intent_response = client.chat.completions.create(
                            model="llama3-8b-8192",
                            messages=[system_msg_intent, {"role": "user", "content": sentence}],
                            response_format={"type": "json_object"},
                            temperature=0.2
                        )
                        intent_result = json.loads(intent_response.choices[0].message.content)
                    except Exception as e:
                        logger.warning(f"Intent analysis failed for utterance {i + 1}: {str(e)}")

                # Compile results
                results.append({
                    "utterance_id": i + 1,
                    "speaker": speaker,
                    "sentence": sentence,
                    "sentiment": sentiment_result.get("sentiment", "neutral"),
                    "score": sentiment_result.get("score", 0.5),
                    "reason": sentiment_result.get("reason", "Analysis unavailable"),
                    "keywords": sentiment_result.get("keywords", []),
                    "sentiment_confidence": sentiment_result.get("confidence", 0.5),
                    "intent": intent_result.get("intent", "unknown"),
                    "secondary_intents": intent_result.get("secondary_intents", []),
                    "intent_confidence": intent_result.get("confidence", 0.5),
                    "intent_reasoning": intent_result.get("reasoning", "Analysis unavailable")
                })

            except Exception as e:
                logger.error(f"Error processing utterance {i + 1}: {str(e)}")
                results.append({
                    "utterance_id": i + 1,
                    "speaker": speaker,
                    "sentence": sentence,
                    "sentiment": "neutral",
                    "score": 0.5,
                    "reason": f"Error: {str(e)}",
                    "keywords": [],
                    "sentiment_confidence": 0.0,
                    "intent": "unknown",
                    "secondary_intents": [],
                    "intent_confidence": 0.0,
                    "intent_reasoning": f"Error: {str(e)}"
                })

        # Calculate performance metrics
        csat_data = calculate_csat_score(results)
        agent_performance = calculate_agent_performance(results)

        # Compile comprehensive analysis
        analysis_summary = {
            "conversation_id": f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "total_utterances": len(results),
            "speakers": list(set([r['speaker'] for r in results])),
            "topic_analysis": topic_analysis,
            "csat_analysis": csat_data,
            "agent_performance": agent_performance,
            "utterances": results,
            "analysis_timestamp": datetime.now().isoformat(),
            "domain": domain or "general"
        }

        logger.info(f"Analysis completed successfully for {len(results)} utterances")
        return analysis_summary

    except Exception as e:
        logger.error(f"Critical error in analyze_sentences: {str(e)}", exc_info=True)
        return {
            "error": f"Analysis failed: {str(e)}",
            "conversation_id": f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "total_utterances": 0,
            "speakers": [],
            "topic_analysis": {"topics": ["error"], "primary_topic": "error", "confidence": 0.0},
            "csat_analysis": {"csat_score": 0, "csat_rating": "Error", "methodology": "Error occurred"},
            "agent_performance": {"error": "Analysis failed"},
            "utterances": [],
            "analysis_timestamp": datetime.now().isoformat(),
            "domain": domain or "general"
        }


@app.post("/analyze/")
async def analyze_conversation(file: UploadFile = File(...), domain: str = Form(None)):
    """Enhanced analysis endpoint with comprehensive error handling"""
    try:
        # Validate file
        if not file:
            raise HTTPException(status_code=400, detail="No file provided")

        if file.content_type not in ["text/plain", "application/octet-stream"]:
            raise HTTPException(status_code=400, detail="Only text files (.txt) are supported")

        # Read and validate content
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file provided")

        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = content.decode("latin-1")
            except UnicodeDecodeError:
                raise HTTPException(status_code=400, detail="File encoding not supported. Please use UTF-8.")

        if not text.strip():
            raise HTTPException(status_code=400, detail="File contains no readable text")

        # Perform analysis
        results = analyze_sentences(text, domain)

        if "error" in results:
            raise HTTPException(status_code=500, detail=results["error"])

        logger.info(f"Analysis completed for file: {file.filename}")
        return JSONResponse({"status": "success", "data": results})

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analyze endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "groq_client": "available" if client else "unavailable"
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
