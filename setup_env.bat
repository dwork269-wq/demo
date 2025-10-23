@echo off
echo Setting up Quantum Healing Meditation App...
echo.

echo Creating .env file...
echo OPENAI_API_KEY=your_openai_api_key_here > .env
echo ELEVENLABS_API_KEY=your_elevenlabs_api_key_here >> .env
echo APP_PASSWORD=meditation2024 >> .env

echo.
echo .env file created successfully!
echo.
echo IMPORTANT: Please edit the .env file and replace the placeholder values:
echo - Replace 'your_openai_api_key_here' with your actual OpenAI API key
echo - Replace 'your_elevenlabs_api_key_here' with your actual ElevenLabs API key
echo - The password is already set to 'meditation2024'
echo.
echo You can edit the .env file with any text editor.
echo.
pause
