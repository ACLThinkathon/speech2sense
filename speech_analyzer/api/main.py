from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
import json
import logging
from datetime import datetime

from analyzer.analyzer import analyze_sentences
from analyzer.models import (
    Conversation, Utterance, AnalysisResult
)
from api.database import SessionLocal, init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI App
app = FastAPI(
    title="Speech2Sense Analytics API",
    description="Advanced conversation analytics with AI-powered insights",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency: DB Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Startup Hook: Initialize DB
@app.on_event("startup")
def startup_event():
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")

# ✅ Health Check Endpoint (required by Streamlit dashboard)
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

# Store results in DB
def store_analysis_results(db: Session, analysis_data: dict) -> int:
    try:
        conversation = Conversation(
            conversation_id=analysis_data.get('conversation_id'),
            raw_text=analysis_data.get('raw_text', ''),
            domain=analysis_data.get('domain', 'general'),

            primary_topic=analysis_data.get('topic_analysis', {}).get('primary_topic'),
            topics=analysis_data.get('topic_analysis', {}).get('topics', []),
            topic_confidence=analysis_data.get('topic_analysis', {}).get('confidence'),
            topic_reasoning=analysis_data.get('topic_analysis', {}).get('reasoning'),

            csat_score=analysis_data.get('csat_analysis', {}).get('csat_score'),
            csat_rating=analysis_data.get('csat_analysis', {}).get('csat_rating'),
            csat_methodology=analysis_data.get('csat_analysis', {}).get('methodology'),

            agent_performance_score=analysis_data.get('agent_performance', {}).get('overall_score'),
            agent_performance_rating=analysis_data.get('agent_performance', {}).get('rating'),
            agent_sentiment_avg=analysis_data.get('agent_performance', {}).get('agent_sentiment_avg'),
            professionalism_score=analysis_data.get('agent_performance', {}).get('professionalism_score'),
            customer_sentiment_improvement=analysis_data.get('agent_performance', {}).get('customer_sentiment_improvement'),

            total_utterances=analysis_data.get('total_utterances'),
            speakers=analysis_data.get('speakers', [])
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        for utterance_data in analysis_data.get('utterances', []):
            utterance = Utterance(
                conversation_id=conversation.id,
                utterance_id=utterance_data.get('utterance_id'),
                speaker=utterance_data.get('speaker'),
                sentence=utterance_data.get('sentence'),
                sentiment=utterance_data.get('sentiment'),
                sentiment_score=utterance_data.get('score'),
                sentiment_reason=utterance_data.get('reason'),
                sentiment_keywords=utterance_data.get('keywords', []),
                sentiment_confidence=utterance_data.get('sentiment_confidence'),
                intent=utterance_data.get('intent'),
                secondary_intents=utterance_data.get('secondary_intents', []),
                intent_confidence=utterance_data.get('intent_confidence'),
                intent_reasoning=utterance_data.get('intent_reasoning')
            )
            db.add(utterance)

        analysis_result = AnalysisResult(
            conversation_id=conversation.id,
            analysis_version="2.0.0",
            model_used="llama3-8b-8192",
            analysis_success_rate=1.0,
            average_confidence_score=0.85
        )
        db.add(analysis_result)

        db.commit()
        logger.info(f"Analysis results stored for conversation {conversation.id}")
        return conversation.id

    except Exception as e:
        db.rollback()
        logger.error(f"Error storing analysis results: {str(e)}")
        raise

# Analyze API
@app.post("/analyze/", response_model=dict)
async def analyze_conversation(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    domain: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        if file.content_type not in ["text/plain", "application/octet-stream"]:
            raise HTTPException(status_code=400, detail="Only text files are supported")

        content = await file.read()
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = content.decode("latin-1")
            except UnicodeDecodeError:
                raise HTTPException(status_code=400, detail="File encoding not supported")

        if not text.strip():
            raise HTTPException(status_code=400, detail="File contains no readable text")

        analysis_results = analyze_sentences(text, domain)

        if "error" in analysis_results:
            raise HTTPException(status_code=500, detail=analysis_results["error"])

        analysis_results['raw_text'] = text

        background_tasks.add_task(store_analysis_results, db, analysis_results)

        logger.info(f"Analysis completed for file: {file.filename}")
        return {
            "status": "success",
            "message": "Analysis completed successfully",
            "data": analysis_results
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analyze endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
