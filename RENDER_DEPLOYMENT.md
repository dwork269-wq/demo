# Render Deployment Troubleshooting

## Python 3.13 + pydub Issue

If you see this error on Render:
```
ModuleNotFoundError: No module named 'audioop'
ModuleNotFoundError: No module named 'pyaudioop'
```

### Solution 1: Use Python 3.11 (Recommended)
The app includes `runtime.txt` specifying Python 3.11.9. Render should automatically use this version.

### Solution 2: Manual Python Version Selection
1. In Render dashboard, go to your service settings
2. Under "Build & Deploy" → "Environment"
3. Set Python version to 3.11.x

### Solution 3: Alternative Audio Processing
If pydub still fails, the app will automatically:
- Fall back to mock data mode
- Still generate meditation text
- Skip audio processing (TTS will still work)

## Environment Variables Required

### Backend (.env)
```
OPENAI_API_KEY=your_openai_key
ELEVENLABS_API_KEY=your_elevenlabs_key
APP_PASSWORD=meditation2024
```

### Frontend (.env)
```
REACT_APP_API_URL=https://your-backend-app.onrender.com
```

## Build Commands

### Backend
- Build: `pip install -r requirements.txt`
- Start: `gunicorn app:app --bind 0.0.0.0:$PORT`

### Frontend
- Build: `npm run build`
- Publish: `build/` directory

## Common Issues

1. **Python Version**: Use Python 3.11.x
2. **Environment Variables**: Ensure all required vars are set
3. **Build Timeout**: Render has 15min build limit
4. **Memory**: Audio processing can be memory-intensive
5. **File Permissions**: Ensure `public/download/` is writable

## Testing Locally

1. Backend: `python app.py`
2. Frontend: `npm start`
3. Check: `http://localhost:3000`
