from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, BackgroundTasks, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
import json
import logging
import tempfile
import os
from datetime import datetime, date
import traceback
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analyzer.analyzer import analyze_sentences
from analyzer.audio_processor import process_audio_file
from databaseLib.models import (
    Conversation, Utterance, AnalysisResult
)
from databaseLib.database import SessionLocal, init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI App
app = FastAPI(
    title="Speech2Sense Analytics API",
    description="Advanced conversation analytics with AI-powered insights supporting audio and text files",
    version="2.1.0"
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


# ✅ Health Check Endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "supported_formats": ["text/plain", "audio/wav", "audio/mp3", "audio/mp4", "audio/mpeg"]
    }


# Helper to serialize datetime values
def serialize_datetimes(obj):
    if isinstance(obj, dict):
        return {k: serialize_datetimes(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_datetimes(item) for item in obj]
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return obj


# Catch-all exception logger
@app.middleware("http")
async def log_exceptions(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Unhandled Exception: {str(e)}")
        logger.error(traceback.format_exc())
        raise e

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
                speaker=utterance_data.get('speaker_name', utterance_data.get('speaker')),
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
            analysis_version="2.1.0",
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

# Enhanced Analyze API supporting both audio and text files
@app.post("/analyze/", response_model=dict)
async def analyze_conversation(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        domain: Optional[str] = Form("general"),
        db: Session = Depends(get_db)
):
    try:
        content_type = file.content_type
        filename = file.filename.lower() if file.filename else ""

        logger.info(f"Processing file: {file.filename}, Content-Type: {content_type}")
        logger.info(f"File extension: {os.path.splitext(filename)[1]}")
        logger.info(f"MIME type: {content_type}")

        # Fallback: guess file type by extension if content_type is missing or generic
        if not content_type or content_type == "application/octet-stream":
            if filename.endswith(('.wav', '.mp3', '.mp4', '.m4a')):
                content_type = "audio/mpeg"
            elif filename.endswith('.txt'):
                content_type = "text/plain"
            logger.warning(f"Guessed content_type as '{content_type}' based on file extension")

        is_audio_file = (
                content_type in ["audio/wav", "audio/mp3", "audio/mp4", "audio/mpeg", "audio/x-wav"] or
                filename.endswith(('.wav', '.mp3', '.mp4', '.m4a'))
        )

        is_text_file = (
                content_type in ["text/plain", "application/octet-stream"] or
                filename.endswith('.txt')
        )

        if not (is_audio_file or is_text_file):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format '{content_type}' with extension '{filename}'. Only .txt, .wav, .mp3, .mp4 supported."
            )

            text_content = ""

        if is_audio_file:
            logger.info("Processing audio file...")
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
                temp_file.write(await file.read())
                temp_file_path = temp_file.name

            try:
                text_content = process_audio_file(temp_file_path)
                if not text_content or not text_content.strip():
                    raise HTTPException(status_code=400, detail="No speech detected in audio file")
                logger.info("Audio processing completed successfully")

            except Exception as audio_error:
                logger.error(f"Audio processing failed: {str(audio_error)}")
                logger.error(traceback.format_exc())
                raise HTTPException(
                    status_code=500,
                    detail=f"Audio processing failed: {str(audio_error)}"
                )
            finally:
                try:
                    os.unlink(temp_file_path)
                except:
                    pass

        else:
            logger.info("Processing text file...")
            content = await file.read()

            try:
                text_content = content.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    text_content = content.decode("latin-1")
                except UnicodeDecodeError:
                    raise HTTPException(status_code=400, detail="File encoding not supported. Please use UTF-8.")

        if not text_content.strip():
            raise HTTPException(status_code=400, detail="File contains no readable content")

        logger.info("Starting conversation analysis...")
        analysis_results = analyze_sentences(text_content, domain)

        if "error" in analysis_results:
            raise HTTPException(status_code=500, detail=analysis_results["error"])

        analysis_results['raw_text'] = text_content
        analysis_results['file_type'] = 'audio' if is_audio_file else 'text'
        analysis_results['original_filename'] = file.filename

        background_tasks.add_task(store_analysis_results, db, analysis_results)

        logger.info(f"Analysis completed successfully for file: {file.filename}")
        return json.loads(json.dumps({
            "status": "success",
            "message": "Analysis completed successfully",
            "file_type": 'audio' if is_audio_file else 'text',
            "data": serialize_datetimes(analysis_results)
        }))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analyze endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
