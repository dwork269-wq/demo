# Custom Meditation App - AI-Powered Personalized Meditations

A full-stack application that creates custom meditations using AI. Users input their preferences, and the app generates personalized meditation scripts, converts them to speech, and creates a complete audio experience with background music.

## Features

- **AI-Powered Meditation Generation**: Uses OpenAI GPT-3.5 to create personalized meditation scripts
- **Text-to-Speech**: Converts meditation text to natural speech using ElevenLabs v3 with Priyanka Sogam's voice
- **SSML Support**: Uses Speech Synthesis Markup Language for pace, emphasis, and pauses
- **Audio Processing**: Combines speech with background music and silence intervals
- **3-Chapter Structure**: Automatically parses meditations into structured chapters
- **Modern UI**: Beautiful, responsive React frontend with glassmorphism design
- **Simple Authentication**: Password-protected access (no complex user management)

## Tech Stack

### Backend
- **Flask**: Python web framework
- **OpenAI API**: GPT-3.5 for meditation text generation
- **ElevenLabs API v3**: High-quality text-to-speech conversion with Priyanka Sogam's voice and SSML support
- **Pydub**: Audio processing and mixing
- **Gunicorn**: WSGI server for production

### Frontend
- **React**: Modern JavaScript framework
- **Axios**: HTTP client for API communication
- **CSS3**: Custom styling with glassmorphism effects

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API key
- ElevenLabs API key

### Backend Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables**:
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
   APP_PASSWORD=meditation2024
   ```

3. **Add background music**:
   - Replace `background_music.mp3` with your meditation background music file
   - Supported formats: MP3, WAV, M4A
   - Recommended: At least 30 minutes duration, normalized volume

4. **Run the Flask server**:
   ```bash
   python app.py
   ```

### Frontend Setup

1. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

2. **Start the React development server**:
   ```bash
   npm start
   ```

The app will be available at `http://localhost:3000`

## Deployment on Render

### Backend Deployment

1. **Create a new Web Service on Render**
2. **Connect your GitHub repository**
3. **Configure build settings**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`
4. **Add environment variables**:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `ELEVENLABS_API_KEY`: Your ElevenLabs API key
   - `APP_PASSWORD`: Your chosen password

### Frontend Deployment

1. **Create a new Static Site on Render**
2. **Connect your GitHub repository**
3. **Configure build settings**:
   - Build Command: `npm run build`
   - Publish Directory: `build`
4. **Add environment variable**:
   - `REACT_APP_API_URL`: Your backend URL (e.g., `https://your-app.onrender.com`)

### File Structure

The app creates MP3 files in `public/download/` directory:
- **Backend**: Creates files in `public/download/`
- **Frontend**: Serves files via `/download/<filename>` endpoint
- **Audio Player**: Uses full URL to access files

## API Endpoints

### `POST /api/generate-meditation`
Generates a custom meditation based on user inputs.

**Request Body**:
```json
{
  "password": "meditation2024",
  "focus_area": "stress relief",
  "duration": "10 minutes",
  "mood": "anxious and restless"
}
```

**Response**:
```json
{
  "success": true,
  "meditation_text": "Generated meditation script...",
  "chapters": ["Chapter 1 text", "Chapter 2 text", "Chapter 3 text"],
  "audio_url": "/api/download/filename.mp3"
}
```

### `GET /api/download/<filename>`
Downloads the generated meditation audio file.

### `GET /api/health`
Health check endpoint.

## How It Works

1. **User Input**: User selects focus area, duration, and mood
2. **AI Generation**: OpenAI creates a personalized meditation script with 3 chapters
3. **Text Parsing**: Script is parsed into 3 chapters using regex patterns
4. **Speech Synthesis**: Each chapter is converted to speech using ElevenLabs
5. **Audio Mixing**: Chapters are combined with 1-minute silence intervals and background music
6. **Delivery**: Final meditation is served to the user

## Customization

### Meditation Focus Areas
- Stress Relief
- Sleep Preparation
- Anxiety Management
- Mindfulness
- Self-Compassion
- Focus & Concentration
- Emotional Healing
- Gratitude Practice

### Duration Options
- 5 minutes
- 10 minutes
- 15 minutes
- 20 minutes
- 30 minutes

### Mood Options
- Calm & Peaceful
- Energized & Alert
- Tired & Drained
- Anxious & Restless
- Focused & Determined
- Emotional & Sensitive
- Neutral & Balanced

## Security Notes

- Simple password protection is implemented for demo purposes
- For production, implement proper user authentication
- API keys should be stored securely and never exposed in client-side code
- Consider rate limiting for API endpoints

## Future Enhancements

- User accounts and meditation history
- Multiple voice options
- Custom background music selection
- Meditation progress tracking
- Social sharing features
- Mobile app development

## License

This project is for demonstration purposes. Please ensure you have proper licenses for all APIs and services used.
