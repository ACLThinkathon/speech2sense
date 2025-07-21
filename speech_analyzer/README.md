# speech2sense
Automation of sentiment anlysis 

To run the app : streamlit run app.py


Steps to execute code without using the docker:

# Setup venv and install packages
python3 -m venv venv
source venv/bin/activate     # or venv\Scripts\activate on Windows
pip install --upgrade pip
pip install -r requirements.txt

# Export Groq API key env variable
export GROQ_API_KEY="your_actual_api_key"

# Start backend API server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# In new terminal, activate venv and start Streamlit UI

 streamlit run app.py --server.port 3000 --server.address 0.0.0.0
 Change 0.0.0.0 to your own ipv4 address
 