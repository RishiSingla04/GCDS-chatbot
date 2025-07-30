@echo off
echo 🍁 GCDS Chatbot Setup Script
echo ==============================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not installed
    exit /b 1
)

REM Check if Ollama is installed
ollama --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama is required but not installed
    echo Please install Ollama from https://ollama.ai/
    exit /b 1
)

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv gcds-chatbot-env

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call gcds-chatbot-env\Scripts\activate

REM Install requirements
echo 📥 Installing Python dependencies...
pip install -r requirements.txt

REM Setup knowledge base
echo 🔍 Setting up knowledge base...
python setup_knowledge_base.py

REM Pull Ollama model
echo 🤖 Pulling Ollama model (llama3.2:3b)...
ollama pull llama3.2:3b

echo.
echo ✅ Setup complete!
echo.
echo To run the chatbot:
echo 1. Activate the virtual environment: gcds-chatbot-env\Scripts\activate
echo 2. Run the chatbot: python chatbot_gui.py
echo.
echo Or simply run: python run.py
pause