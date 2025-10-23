@echo off
echo 🧘 Custom Meditation App Setup
echo ==============================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not installed.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is required but not installed.
    pause
    exit /b 1
)

echo ✅ Python and Node.js are installed

REM Create virtual environment
echo 📦 Creating Python virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install Python dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

REM Install Node.js dependencies
echo 📦 Installing Node.js dependencies...
npm install

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file...
    copy env.example .env
    echo ⚠️  Please edit .env file with your API keys before running the app
)

echo.
echo 🎉 Setup complete!
echo.
echo Next steps:
echo 1. Edit .env file with your OpenAI and ElevenLabs API keys
echo 2. Run 'python app.py' to start the backend
echo 3. Run 'npm start' to start the frontend
echo 4. Visit http://localhost:3000
echo.
echo Default password: meditation2024
pause
