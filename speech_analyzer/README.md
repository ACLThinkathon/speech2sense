# speech2sense
Automation of sentiment anlysis 


Steps to execute code without using the docker:

# Setup venv and install packages
python3 -m venv venv
source venv/bin/activate     # or venv\Scripts\activate on Windows
pip install --upgrade pip
pip install -r requirements.txt

# Export Groq API key env variable
export GROQ_API_KEY="your_actual_api_key"

# Start backend API server
cd api
Run start_api.bat

# In new terminal, activate venv and start Streamlit UI
cd webui
streamlit run app.py