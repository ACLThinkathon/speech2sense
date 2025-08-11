from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Conversation(Base):
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, unique=True, index=True)  # External conversation ID
    raw_text = Column(Text)
    domain = Column(String, default="general")

    # Topic analysis
    primary_topic = Column(String)
    topics = Column(JSON)  # Store list of topics
    topic_confidence = Column(Float)
    topic_reasoning = Column(Text)

    # CSAT metrics
    csat_score = Column(Float)
    csat_rating = Column(String)
    csat_methodology = Column(Text)

    # Agent performance metrics
    agent_performance_score = Column(Float)
    agent_performance_rating = Column(String)
    agent_sentiment_avg = Column(Float)
    professionalism_score = Column(Float)
    customer_sentiment_improvement = Column(Float)

    # Metadata
    total_utterances = Column(Integer)
    speakers = Column(JSON)  # Store list of speakers
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    utterances = relationship("Utterance", back_populates="conversation", cascade="all, delete-orphan")
    analysis_results = relationship("AnalysisResult", back_populates="conversation", cascade="all, delete-orphan")


class Utterance(Base):
    __tablename__ = 'utterances'

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id', ondelete='CASCADE'))
    utterance_id = Column(Integer)  # Sequential ID within conversation

    # Speaker and content
    speaker = Column(String, index=True)
    sentence = Column(Text)

    # Sentiment analysis
    sentiment = Column(String, index=True)
    sentiment_score = Column(Float)
    sentiment_reason = Column(Text)
    sentiment_keywords = Column(JSON)  # Store list of keywords
    sentiment_confidence = Column(Float)

    # Intent analysis
    intent = Column(String, index=True)
    secondary_intents = Column(JSON)  # Store list of secondary intents
    intent_confidence = Column(Float)
    intent_reasoning = Column(Text)

    # Metadata
    processed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", back_populates="utterances")


class AnalysisResult(Base):
    __tablename__ = 'analysis_results'

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id', ondelete='CASCADE'))

    # Analysis metadata
    analysis_version = Column(String, default="2.0.0")
    model_used = Column(String, default="llama3-8b-8192")
    processing_time_seconds = Column(Float)

    # Quality metrics
    analysis_success_rate = Column(Float)  # Percentage of successful utterance analyses
    average_confidence_score = Column(Float)

    # Error tracking
    errors_encountered = Column(JSON)  # Store list of errors
    warnings_encountered = Column(JSON)  # Store list of warnings

    # Performance benchmarks
    sentiment_analysis_accuracy = Column(Float)
    intent_analysis_accuracy = Column(Float)
    topic_detection_accuracy = Column(Float)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", back_populates="analysis_results")


class AgentPerformanceMetrics(Base):
    __tablename__ = 'agent_performance_metrics'

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id', ondelete='CASCADE'))

    # Agent identification
    agent_name = Column(String)  # If available in conversation
    agent_id = Column(String)  # If available in conversation

    # Performance scores
    overall_performance_score = Column(Float)
    performance_rating = Column(String)

    # Detailed metrics
    response_time_avg = Column(Float)  # If timestamps available
    resolution_achieved = Column(Boolean)
    customer_satisfaction_impact = Column(Float)

    # Communication metrics
    empathy_score = Column(Float)
    clarity_score = Column(Float)
    professionalism_score = Column(Float)

    # Issue handling
    first_call_resolution = Column(Boolean)
    escalation_required = Column(Boolean)
    follow_up_needed = Column(Boolean)

    # Improvement suggestions
    improvement_areas = Column(JSON)  # Store list of areas for improvement
    strengths = Column(JSON)  # Store list of strengths

    # Timestamps
    evaluated_at = Column(DateTime, default=datetime.utcnow)


class ConversationSummary(Base):
    __tablename__ = 'conversation_summaries'

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id', ondelete='CASCADE'))

    # Executive summary
    executive_summary = Column(Text)
    key_points = Column(JSON)  # Store list of key discussion points

    # Outcome tracking
    issue_resolved = Column(Boolean)
    resolution_method = Column(String)
    customer_satisfaction = Column(String)

    # Follow-up requirements
    follow_up_required = Column(Boolean)
    follow_up_date = Column(DateTime)
    follow_up_reason = Column(Text)

    # Tags and categorization
    conversation_tags = Column(JSON)  # Store list of tags
    priority_level = Column(String)  # high, medium, low
    business_impact = Column(String)  # high, medium, low

    # Quality assurance
    qa_score = Column(Float)
    qa_notes = Column(Text)
    reviewed_by = Column(String)
    review_date = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DashboardMetrics(Base):
    __tablename__ = 'dashboard_metrics'

    id = Column(Integer, primary_key=True, index=True)

    # Time period for metrics
    date = Column(DateTime, index=True)
    period_type = Column(String)  # daily, weekly, monthly

    # Volume metrics
    total_conversations = Column(Integer)
    total_utterances = Column(Integer)
    avg_conversation_length = Column(Float)

    # Sentiment metrics
    avg_customer_sentiment = Column(Float)
    avg_agent_sentiment = Column(Float)
    sentiment_improvement_rate = Column(Float)

    # Intent distribution
    complaint_percentage = Column(Float)
    inquiry_percentage = Column(Float)
    feedback_percentage = Column(Float)
    request_percentage = Column(Float)

    # Topic distribution
    top_topics = Column(JSON)  # Store top 10 topics with counts
    trending_topics = Column(JSON)  # Store trending topics

    # Performance metrics
    avg_csat_score = Column(Float)
    avg_agent_performance = Column(Float)
    resolution_rate = Column(Float)

    # Quality metrics
    analysis_accuracy = Column(Float)
    processing_errors = Column(Integer)

    # Timestamps
    calculated_at = Column(DateTime, default=datetime.utcnow)

    # Indexes for better query performance
    __table_args__ = (
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )
