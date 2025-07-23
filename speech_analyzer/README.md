# Setup venv and install packages
python3 -m venv venv
source venv/bin/activate     # or venv\Scripts\activate on Windows
pip install --upgrade pip
pip install -r requirements.txt

#Update your groq key in analyzer.py file
GROQ_API_KEY="your_actual_api_key"

# Start backend API server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# In new terminal, activate venv and start Streamlit UI
cd webui:
 streamlit run app.py 
 