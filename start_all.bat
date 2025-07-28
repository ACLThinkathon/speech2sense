@echo off
echo Starting FastAPI backend on port 8000...
start cmd /k "cd api && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 30

echo Launching Streamlit frontend...
cd webui
streamlit run app.py
