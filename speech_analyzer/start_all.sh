#!/bin/bash
echo "🚀 Starting FastAPI backend on port 8000..."
cd api
uvicorn main:app --reload --port 8000 &
cd ..

echo "🌐 Launching Streamlit frontend..."
cd webui
streamlit run app.py
