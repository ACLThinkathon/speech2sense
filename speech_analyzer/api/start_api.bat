@echo off
echo Starting Speech2Sense API...

:: Go to the project root
cd /d "%~dp0\.."

:: Set Python path to include root folder (so imports like analyzer.analyzer work)
set PYTHONPATH=%cd%

:: Start FastAPI server with main.py
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

pause
