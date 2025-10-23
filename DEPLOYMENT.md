# Custom Meditation App - Deployment Guide

## Quick Start

1. **Get API Keys**:
   - OpenAI API key from https://platform.openai.com/api-keys
   - ElevenLabs API key from https://elevenlabs.io/app/settings/api-keys

2. **Set Environment Variables**:
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

3. **Run Locally**:
   ```bash
   # Backend
   pip install -r requirements.txt
   python app.py
   
   # Frontend (in another terminal)
   npm install
   npm start
   ```

## Render Deployment

### Backend (Flask API)

1. Create new **Web Service** on Render
2. Connect GitHub repository
3. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
4. Environment Variables:
   - `OPENAI_API_KEY`: Your OpenAI key
   - `ELEVENLABS_API_KEY`: Your ElevenLabs key
   - `APP_PASSWORD`: Your chosen password

### Frontend (React App)

1. Create new **Static Site** on Render
2. Connect GitHub repository
3. Settings:
   - **Build Command**: `npm run build`
   - **Publish Directory**: `build`
4. Environment Variables:
   - `REACT_APP_API_URL`: Your backend URL

## Testing

1. Visit your frontend URL
2. Enter the password you set
3. Fill out the meditation form
4. Wait for AI to generate your meditation
5. Listen to your custom meditation!

## Troubleshooting

- **API Errors**: Check your API keys are valid and have credits
- **Audio Issues**: Ensure ElevenLabs API key has sufficient characters
- **Build Errors**: Check all dependencies are properly installed
- **CORS Issues**: Verify frontend is pointing to correct backend URL
