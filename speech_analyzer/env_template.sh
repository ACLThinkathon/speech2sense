# .env.template - Environment Variables Template
# Copy this file to .env and fill in your actual values

# =============================================================================
# API KEYS (REQUIRED)
# =============================================================================

# Groq API Key - Get from https://console.groq.com
GROQ_API_KEY=your_groq_api_key_here

# Hugging Face Token - Get from https://huggingface.co/settings/tokens
HF_TOKEN=your_huggingface_token_here

# =============================================================================
# APPLICATION SETTINGS
# =============================================================================

# API Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false

# Streamlit Configuration
UI_HOST=0.0.0.0
UI_PORT=8501

# Database Configuration
DATABASE_URL=sqlite:///./speech2sense.db

# =============================================================================
# PROCESSING SETTINGS
# =============================================================================

# Audio Processing
MAX_AUDIO_FILE_SIZE=104857600  # 100MB in bytes
AUDIO_PROCESSING_TIMEOUT=600   # 10 minutes
DEFAULT_SAMPLE_RATE=16000
DEFAULT_CHANNELS=1

# Text Processing
MAX_TEXT_FILE_SIZE=10485760    # 10MB in bytes
TEXT_PROCESSING_TIMEOUT=60     # 1 minute

# =============================================================================
# AI MODEL SETTINGS
# =============================================================================

# Groq Models
GROQ_CHAT_MODEL=llama3-8b-8192
GROQ_WHISPER_MODEL=whisper-large-v3-turbo

# Analysis Parameters
SENTIMENT_TEMPERATURE=0.2
INTENT_TEMPERATURE=0.2
TOPIC_TEMPERATURE=0.2

# =============================================================================
# SECURITY SETTINGS (Production)
# =============================================================================

# CORS Settings
CORS_ORIGINS=["*"]  # Restrict in production: ["https://yourdomain.com"]
CORS_CREDENTIALS=true
CORS_METHODS=["*"]
CORS_HEADERS=["*"]

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600  # 1 hour in seconds

# File Upload Security
ALLOWED_AUDIO_EXTENSIONS=["wav", "mp3"]
ALLOWED_TEXT_EXTENSIONS=["txt"]

# =============================================================================
# LOGGING SETTINGS
# =============================================================================

# Log Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO
LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Log Files
ERROR_LOG_FILE=analyzer_errors.log
ACCESS_LOG_FILE=access.log

# =============================================================================
# DOCKER SETTINGS
# =============================================================================

# Container Names
API_CONTAINER_NAME=speech2sense-api
UI_CONTAINER_NAME=speech2sense-ui
NGINX_CONTAINER_NAME=speech2sense-nginx

# Network
DOCKER_NETWORK=speech2sense-network

# =============================================================================
# OPTIONAL INTEGRATIONS
# =============================================================================

# Redis (for caching in production)
REDIS_URL=redis://redis:6379/0
REDIS_ENABLED=false

# Email Notifications (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_NOTIFICATIONS=false

# Webhook Notifications (optional)
WEBHOOK_URL=https://your-webhook-url.com/notify
WEBHOOK_ENABLED=false

# =============================================================================
# MONITORING & ANALYTICS
# =============================================================================

# Application Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090

# Usage Analytics
ANALYTICS_ENABLED=false
ANALYTICS_ENDPOINT=https://your-analytics-endpoint.com

# =============================================================================
# BACKUP SETTINGS
# =============================================================================

# Database Backup
BACKUP_ENABLED=false
BACKUP_SCHEDULE="0 2 * * *"  # Daily at 2 AM
BACKUP_RETENTION_DAYS=30

# =============================================================================
# DEVELOPMENT SETTINGS
# =============================================================================

# Debug Mode
DEBUG=false
RELOAD=false

# Testing
TEST_MODE=false
MOCK_AI_RESPONSES=false

# Performance
ENABLE_PROFILING=false
PROFILE_OUTPUT_DIR=./profiles