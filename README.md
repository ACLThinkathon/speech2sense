# 🎯 Speech2Sense - Advanced Conversation Analytics

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/FastAPI-Latest-green.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/Streamlit-Latest-red.svg" alt="Streamlit">
  <img src="https://img.shields.io/badge/AI-Powered-purple.svg" alt="AI Powered">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License">
</div>

## 📋 Overview

Speech2Sense is an advanced AI-powered conversation analytics platform that transforms customer service interactions into actionable insights. Supporting both text and audio files, it provides comprehensive analysis including sentiment detection, intent classification, topic categorization, CSAT scoring, and agent performance evaluation.

### 🚀 Key Features
- **🎵 Audio Processing**: WAV, MP3 file support with automatic transcription
- **📁 Text Analysis**: Direct conversation text processing
- **🤖 AI-Powered**: LLaMA 3 and Whisper models for advanced analysis
- **👥 Speaker Diarization**: Automatic Agent/Customer role identification
- **📊 Comprehensive Analytics**: Sentiment, intent, topics, CSAT, and performance metrics
- **🌐 Interactive Dashboard**: Beautiful Streamlit web interface
- **🔄 RESTful API**: FastAPI backend with comprehensive endpoints
- **💾 Data Persistence**: SQLite database with full conversation history

### 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│  Streamlit UI   │───▶│   FastAPI        │───▶│  Analysis Engine    │
│  Port: 8501     │    │   Port: 8000     │    │  • Sentiment        │
│  • File Upload  │    │  • /analyze/     │    │  • Intent           │
│  • Visualizations│   │  • /transcribe/  │    │  • Topics           │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
                                 │
                       ┌─────────▼─────────┐
                       │  Audio Processor  │
                       │  • Whisper API    │
                       │  • PyAnnote       │
                       │  • FFmpeg         │
                       └───────────────────┘
```

## 📋 Prerequisites

### System Requirements
- **Operating System**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum (8GB recommended for audio processing)
- **Storage**: 2GB free space for dependencies and models
- **Network**: Internet connection for AI API calls

### Required Accounts
1. **Groq API Account**: Get free API key from [console.groq.com](https://console.groq.com)
2. **Hugging Face Account**: Free token from [huggingface.co](https://huggingface.co/settings/tokens)

## 🛠️ Installation Guide

### Step 1: System Dependencies

#### Windows Installation
```powershell
# Install Chocolatey (if not installed)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install FFmpeg
choco install ffmpeg

# Install Git (if not installed)
choco install git

# Verify installations
ffmpeg -version
git --version
python --version
```

#### Linux (Ubuntu/Debian) Installation
```bash
# Update package list
sudo apt update

# Install system dependencies
sudo apt install -y python3 python3-pip python3-venv git ffmpeg libsndfile1-dev

# Verify installations
ffmpeg -version
git --version
python3 --version
```

#### macOS Installation
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.11 git ffmpeg libsndfile

# Verify installations
ffmpeg -version
git --version
python3 --version
```

### Step 2: Project Setup

#### Clone Repository
```bash
# Clone the project
git clone <your-repository-url>
cd speech2sense

# Or download and extract ZIP file, then navigate to folder
```

#### Create Virtual Environment

**Windows:**
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Verify activation (should show (venv) prefix)
```

**Linux/macOS:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (should show (venv) prefix)
```

### Step 3: Install Python Dependencies

```bash
# Ensure you're in the project directory with activated virtual environment
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Verify critical installations
python -c "import fastapi, streamlit, groq; print('Core packages installed successfully')"
```

### Step 4: Environment Configuration

Create `.env` file in project root:

**Windows:**
```powershell
# Create .env file
echo GROQ_API_KEY=your_groq_api_key_here > .env
echo HF_TOKEN=your_huggingface_token_here >> .env
```

**Linux/macOS:**
```bash
# Create .env file
cat > .env << EOF
GROQ_API_KEY=your_groq_api_key_here
HF_TOKEN=your_huggingface_token_here
EOF
```

**Replace with your actual API keys:**
- Get Groq API key from: https://console.groq.com
- Get HuggingFace token from: https://huggingface.co/settings/tokens

### Step 5: Database Initialization

```bash
# Initialize database
python -c "from databaseLib.database import init_db; init_db()"

# Verify database creation
ls -la speech2sense.db  # Linux/macOS
dir speech2sense.db     # Windows
```

## 🚀 Running the Application

### Option 1: Automatic Startup (Recommended)

**Windows:**
```powershell
# Make sure you're in the project directory with activated virtual environment
.\start_all.bat
```

**Linux/macOS:**
```bash
# Make script executable and run
chmod +x start_all.sh
./start_all.sh
```

### Option 2: Manual Startup

#### Terminal 1 - Start FastAPI Backend
```bash
# Activate virtual environment
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

# Start API server
python main.py

# Alternative method:
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Terminal 2 - Start Streamlit Frontend
```bash
# Open new terminal and activate virtual environment
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

# Navigate to project directory
cd speech2sense

# Start Streamlit dashboard
streamlit run app.py
```

### 🌐 Access Application

Once both services are running:
- **Dashboard**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

## 📖 Usage Guide

### For Text Files
1. Select "📁 Text File (.txt)" in the dashboard
2. Upload conversation file with format:
   ```
   Customer: I'm having trouble with my order
   Agent: I'd be happy to help you with that
   Customer: Thank you, I appreciate it
   ```
3. Choose domain (general, ecommerce, healthcare, etc.)
4. Click "🔍 Analyze Conversation"

### For Audio Files
1. Select "🎵 Audio File (.wav, .mp3)" in the dashboard
2. Upload your audio recording (max 100MB recommended)
3. Choose processing mode:
   - **Full Analysis**: Complete transcription + sentiment analysis
   - **Transcribe Only**: Convert speech to text only
4. Select domain for analysis
5. Click "🔍 Analyze Audio" or "🎙️ Transcribe Audio"

### Audio File Requirements
- **Formats**: WAV, MP3
- **Quality**: Clear speech, minimal background noise
- **Duration**: Up to 60 minutes (shorter files process faster)
- **Speakers**: 2-3 speakers recommended for best diarization
- **Language**: English (primary support)

## 🔧 API Usage

### Analyze Endpoint
```bash
# Text file analysis
curl -X POST "http://localhost:8000/analyze/" \
  -F "file=@conversation.txt" \
  -F "domain=customer_support"

# Audio file analysis
curl -X POST "http://localhost:8000/analyze/" \
  -F "file=@recording.wav" \
  -F "domain=general"
```

### Python API Client
```python
import requests

# Analyze text file
with open('conversation.txt', 'rb') as f:
    files = {'file': ('conversation.txt', f, 'text/plain')}
    data = {'domain': 'customer_support'}
    response = requests.post('http://localhost:8000/analyze/', files=files, data=data)
    result = response.json()

# Analyze audio file
with open('recording.wav', 'rb') as f:
    files = {'file': ('recording.wav', f, 'audio/wav')}
    data = {'domain': 'general'}
    response = requests.post('http://localhost:8000/analyze/', files=files, data=data)
    result = response.json()
```

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)
```bash
# Build and start services
docker-compose up --build

# Run in background
docker-compose up -d --build

# Stop services
docker-compose down
```

### Manual Docker Build
```bash
# Build images
docker build -t speech2sense-api -f Dockerfile.api .
docker build -t speech2sense-ui -f Dockerfile.ui .

# Run containers
docker run -d --name speech2sense-api -p 8000:8000 speech2sense-api
docker run -d --name speech2sense-ui -p 8501:8501 speech2sense-ui
```

## 🛠️ Troubleshooting

### Common Issues

#### "FFmpeg not found" Error
**Windows:**
```powershell
# Reinstall FFmpeg
choco install ffmpeg -y

# Add to PATH manually if needed
$env:PATH += ";C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg\bin"
```

**Linux:**
```bash
# Reinstall FFmpeg
sudo apt install -y ffmpeg

# Verify installation
which ffmpeg
ffmpeg -version
```

#### "ModuleNotFoundError" for packages
```bash
# Ensure virtual environment is activated
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

#### "Connection refused" API Error
```bash
# Check if API server is running
curl http://localhost:8000/health

# If not running, start API server
python main.py
```

#### Audio Processing Timeout
- Reduce audio file size (< 50MB recommended)
- Convert to WAV format beforehand
- Ensure stable internet connection for API calls

#### Poor Transcription Quality
- Use high-quality audio recordings
- Minimize background noise
- Ensure clear speaker separation
- Use headset/microphone recordings

### Performance Optimization

#### For Large Audio Files
```bash
# Convert audio to optimal format
ffmpeg -i input.mp3 -ar 16000 -ac 1 -f wav output.wav

# This reduces file size and processing time
```

#### Memory Issues
- Close unnecessary applications
- Process smaller audio segments
- Restart the application if memory usage is high

### Logs and Debugging

#### Check Application Logs
```bash
# API logs appear in terminal where you started main.py
# Error logs are saved to analyzer_errors.log

# View error log
# Windows: type analyzer_errors.log
# Linux/macOS: cat analyzer_errors.log
```

#### Enable Debug Mode
```bash
# Set environment variable for detailed logging
export DEBUG=true  # Linux/macOS
set DEBUG=true     # Windows

# Then restart the application
```

## 📊 Sample Files

### Download Sample Files
The dashboard includes sample conversation files for testing:
- Sample text conversation (customer service scenario)
- Processing examples and format guides

### Create Your Own Test Files

**Sample Text File** (`test_conversation.txt`):
```
Customer: Hi, I'm calling about my recent order. I haven't received it yet.
Agent: I'm sorry to hear about the delay. Let me look into this for you right away.
Customer: Thank you, I appreciate your help.
Agent: I can see your order was shipped yesterday. You should receive it by tomorrow.
Customer: That's great news! Thank you for checking on that.
```

## 🔐 Security Considerations

### API Key Management
- Never commit `.env` file to version control
- Use environment variables in production
- Rotate API keys regularly
- Monitor API usage and costs

### File Upload Security
- Files are processed in secure temporary directories
- Automatic cleanup after processing
- File type validation beyond MIME type checking
- Size limits to prevent abuse

## 📈 Performance Benchmarks

### Processing Times (Approximate)
- **Small text files (< 1KB)**: 2-5 seconds
- **Medium text files (1-10KB)**: 5-15 seconds
- **Small audio files (< 5MB)**: 30-60 seconds
- **Medium audio files (5-20MB)**: 1-3 minutes
- **Large audio files (20-50MB)**: 3-8 minutes

### Hardware Recommendations
- **Development**: 4GB RAM, 2 CPU cores
- **Production**: 8GB+ RAM, 4+ CPU cores
- **High Volume**: 16GB+ RAM, 8+ CPU cores, SSD storage

## 🆘 Support & Contributing

### Getting Help
1. Check this README for common solutions
2. Review error logs in `analyzer_errors.log`
3. Ensure all dependencies are correctly installed
4. Verify API keys in `.env` file

### Bug Reports
When reporting issues, please include:
- Operating system and Python version
- Full error message and stack trace
- Steps to reproduce the issue
- Sample files (if applicable)

### Feature Requests
We welcome suggestions for:
- Additional audio formats
- New analysis metrics
- UI/UX improvements
- Performance optimizations

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Groq**: For providing fast LLaMA 3 inference and Whisper transcription
- **Hugging Face**: For PyAnnote speaker diarization models
- **OpenAI**: For Whisper speech recognition technology
- **FastAPI**: For the excellent web framework
- **Streamlit**: For the interactive dashboard framework
- **SQLAlchemy**: For robust database ORM

---

## 🎉 Quick Start Summary

1. **Install System Dependencies**: FFmpeg, Python 3.8+
2. **Clone Repository**: `git clone <repo-url>`
3. **Setup Environment**: Create virtual environment and install requirements
4. **Configure API Keys**: Create `.env` file with Groq and HuggingFace tokens
5. **Initialize Database**: Run database setup command
6. **Start Services**: Use `start_all.bat` (Windows) or `start_all.sh` (Linux/macOS)
7. **Access Dashboard**: Open http://localhost:8501
8. **Upload & Analyze**: Choose text or audio files and get AI-powered insights!

**Need help? Check the troubleshooting section or review the logs for detailed error information.**