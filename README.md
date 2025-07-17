# Call Center Sentiment & Intent Analysis

## Overview
This project provides an analysis platform for call center conversations:
- Intent detection ("complaint", "inquiry", "feedback")
- Sentiment analysis (positive, neutral, negative)
- Topic modeling visualization
- Dialogue summarization

Built with FastAPI backend and Streamlit frontend, containerized with Docker.

## Requirements
- Docker & Docker Compose installed

## Running the Project

1. Clone or create this repository with given files.
2. From the root folder, run:
To run the Python backend code directly (without Docker), navigate to the backend directory and use the following command:

bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
This command launches the FastAPI server with auto-reload enabled for development.

For the frontend Streamlit app, navigate to the frontend directory and run:

bash
streamlit run app.py --server.port 3000 --server.address 0.0.0.0
change  server address to your ip address
