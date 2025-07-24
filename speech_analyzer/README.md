# Speech2Sense Audio Integration Setup Guide

## 🎯 Overview
This updated Speech2Sense system now supports both text and audio file analysis with the following new features:

- **Audio File Support**: WAV, MP3, MP4, M4A formats
- **Speech-to-Text**: Automatic transcription using Groq Whisper
- **Speaker Diarization**: Automatic Agent/Customer role identification
- **Enhanced UI**: File type selection and audio-specific processing options

## 📋 Prerequisites

### System Requirements
- Python 3.8 or higher
- FFmpeg (for audio processing)
- At least 4GB RAM (8GB recommended for audio processing)
- Internet connection (for AI API calls)

### Install System Dependencies

#### On Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install ffmpeg libsndfile1-dev
```

#### On macOS:
```bash
brew install ffmpeg libsndfile
```

#### On Windows:
1. Download FFmpeg from https://ffmpeg.org/download.html
2. Add FFmpeg to your system PATH
3. Install Microsoft Visual C++ Redistributable

## 🚀 Installation Steps

### 1. Clone and Setup Project
```bash
git clone <your-repo-url>
cd speech2sense
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
Create a `.env` file in the project root:
```bash
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Initialize Database
```bash
python -c "from api.database import init_db; init_db()"
```

## 🔧 File Structure

After integration, your project structure should look like:

```
speech2sense/
├── analyzer/
│   ├── __init__.py
│   ├── analyzer.py          # Main analysis engine
│   ├── audio_processor.py     # NEW: Audio processing module
├── api/
│   ├── __init__.py
│   └── main.py              # NEW: Updated FastAPI with audio support
├── database/
│   ├── __init__.py
│   ├── database.py          # Database configuration
│   └── models.py            # Database models
├── webui/
│   ├── app.py               # NEW: Updated Streamlit dashboard             
├── requirements.txt         # NEW: Updated dependencies
├── .env                     # Environment variables
└── README.md
```

## 🎵 Audio Processing Features

### Supported Audio Formats
- **WAV**: Uncompressed, best quality
- **MP3**: Compressed, good for phone calls
- **MP4/M4A**: Container format, versatile
- **Maximum file size**: 100MB recommended

### Audio Processing Pipeline
1. **File Upload**: Accepts audio files through web interface
2. **Format Conversion**: Converts to WAV using FFmpeg
3. **Speech-to-Text**: Transcribes using Groq Whisper API
4. **Speaker Diarization**: Identifies different speakers using PyAnnote
5. **Role Mapping**: Maps speakers to Agent/Customer roles
6. **Analysis**: Performs sentiment and intent analysis
7. **Results**: Generates comprehensive analytics

### Audio Quality Requirements
- Clear speech with minimal background noise
- 2-3 speakers maximum for best results
- English language (primary support)
- Avoid overlapping speech
- Phone/headset recordings preferred

## 🚀 Running the Application

### 1. Start the FastAPI Server
```bash
python api/main.py
# Or alternatively:
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Start the Streamlit Dashboard
```bash
streamlit run app.py
```

### 3. Access the Application
- **Dashboard**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🎯 Usage Instructions

### For Text Files
1. Select "📁 Text File (.txt)" option
2. Upload a conversation file with format:
   ```
   Customer: Message here
   Agent: Response here
   ```
3. Choose domain and analysis settings
4. Click "🔍 Analyze Conversation"

### For Audio Files
1. Select "🎵 Audio File (.wav, .mp3, .mp4)" option
2. Upload your audio recording
3. Choose processing option:
   - **Full Analysis**: Transcription + sentiment analysis
   - **Transcribe Only**: Just convert speech to text
4. Select domain (for full analysis)
5. Click "🔍 Analyze Audio" or "🎙️ Transcribe Audio"

## 🔍 API Endpoints

### New Endpoints
- `POST /analyze/` - Analyze both text and audio files
- `POST /transcribe/` - Transcribe audio files only
- `GET /conversations/` - Get conversation history
- `GET /conversations/{id}` - Get specific conversation details

### Example API Usage
```python
import requests

# Analyze audio file
files = {"file": ("recording.wav", open("recording.wav", "rb"), "audio/wav")}
data = {"domain": "customer_support"}
response = requests.post("http://localhost:8000/analyze/", files=files, data=data)

# Transcribe only
files = {"file": ("recording.mp3", open("recording.mp3", "rb"), "audio/mp3")}
response = requests.post("http://localhost:8000/transcribe/", files=files)
```

## 🛠️ Troubleshooting

### Common Issues

#### FFmpeg Not Found
```bash
# Error: FFmpeg not found
# Solution: Install FFmpeg and add to PATH
which ffmpeg  # Should return path to ffmpeg
```

#### Audio Processing Timeout
```bash
# Error: Request timed out
# Solution: Reduce file size or increase timeout
# Files larger than 50MB may timeout
```

#### PyAnnote Model Download
```bash
# First run may take time to download models
# Models are cached after first download
# Ensure stable internet connection
```

#### Memory Issues
```bash
# Error: Out of memory during audio processing
# Solution: 
# 1. Reduce audio file size
# 2. Convert to mono channel
# 3. Reduce sample rate to 16kHz
```

### Audio Quality Issues
- **Low transcription accuracy**: Improve audio quality, reduce background noise
- **Poor speaker diarization**: Ensure clear speaker separation, avoid overlapping speech
- **Incorrect role mapping**: Check if speakers use role-specific keywords

## 🔒 Security Considerations

### API Keys
- Store Groq API key in `.env` file
- Never commit API keys to version control
- Use environment variables in production

### File Upload Security
- Files are processed in temporary directories
- Temporary files are automatically cleaned up
- Maximum file size limits are enforced

## 📊 Performance Optimization

### Audio Processing Performance
- **Small files (< 5MB)**: ~30 seconds processing time
- **Medium files (5-20MB)**: ~1-2 minutes processing time
- **Large files (20-50MB)**: ~2-5 minutes processing time

### Optimization Tips
1. Convert audio to WAV format beforehand
2. Use mono channel audio (reduces processing time)
3. Optimize sample rate to 16kHz for speech
4. Process files during off-peak hours for better API response

## 🧪 Testing

### Test with Sample Files
1. Use the provided sample text conversation
2. Record a short 2-minute conversation for audio testing
3. Test both transcription-only and full analysis modes
4. Verify speaker diarization accuracy

### API Testing
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test with sample file
curl -X POST "http://localhost:8000/analyze/" \
  -F "file=@sample_conversation.txt" \
  -F "domain=general"
```

## 📈 Monitoring and Logs

### Log Files
- Application logs: Check console output
- Error logs: `analyzer_errors.log`
- API logs: FastAPI console output

### Monitoring API Health
- Health check endpoint provides system status
- Monitor API response times
- Check disk space for temporary file processing

## 🆘 Support

### Getting Help
1. Check this setup guide for common issues
2. Review application logs for error details
3. Ensure all dependencies are properly installed
4. Verify API keys and environment variables

### Performance Issues
1. Monitor system resources (CPU, RAM, disk)
2. Check network connectivity for API calls
3. Optimize audio file formats and sizes
4. Consider upgrading hardware for large-scale processing

---

## 🎉 You're Ready!

Your Speech2Sense system now supports both text and audio analysis. Upload your first audio file and experience AI-powered conversation analytics with automatic transcription and speaker identification!