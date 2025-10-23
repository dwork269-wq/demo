# Quantum Healing Meditation App - AI-Powered Personalized Meditations

A full-stack application that creates custom quantum healing meditations using AI. Users input their disease, symptoms, and additional instructions, and the app generates personalized meditation scripts based on quantum healing principles, converts them to speech, and creates a complete audio experience with background music.

## Features

- **AI-Powered Quantum Healing Meditations**: Uses OpenAI GPT-3.5 to create personalized meditation scripts based on quantum healing principles
- **Text-to-Speech**: Converts meditation text to natural speech using ElevenLabs v3 with specialized voice effects
- **ElevenLabs Tags Support**: Uses specialized tags like [inhale], [exhale], [pause], [whisper] for enhanced audio experience
- **Audio Processing**: Combines speech with background music and 1-minute silence breaks between chapters
- **3-Chapter Structure**: Automatically parses meditations into structured chapters using <break> tags
- **Modern UI**: Beautiful, responsive React frontend with glassmorphism design
- **Simple Authentication**: Password-protected access (no complex user management)

## Tech Stack

### Backend
- **Flask**: Python web framework
- **OpenAI API**: GPT-3.5 for meditation text generation
- **ElevenLabs API v3**: High-quality text-to-speech conversion with specialized voice effects and ElevenLabs tags support
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

### Important: Python Version Compatibility

The app includes a `runtime.txt` file specifying Python 3.11.9 for compatibility with `pydub`. If you encounter audio processing issues:

1. **Check Python Version**: Ensure Render is using Python 3.11.x
2. **Alternative**: If Python 3.13+ is used, the app will fall back to mock data mode
3. **System Dependencies**: Render may need additional system packages for audio processing

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
  "disease": "anxiety",
  "symptom": "racing thoughts",
  "additional_instruction": "focus on breathing and gentle guidance"
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

1. **User Input**: User provides disease, symptom, and additional instructions
2. **AI Generation**: OpenAI creates a personalized quantum healing meditation script with 3 chapters
3. **Text Parsing**: Script is parsed into 3 chapters using <break> tags
4. **Speech Synthesis**: Each chapter is converted to speech using ElevenLabs with specialized tags
5. **Audio Mixing**: Chapters are combined with 1-minute silence breaks and background music
6. **Delivery**: Final meditation is served to the user

## Customization

### Input Fields
- **Disease**: Any condition or disease the user wants to address (e.g., anxiety, chronic pain, insomnia)
- **Symptom**: Specific symptoms the user is experiencing (e.g., racing thoughts, muscle tension, difficulty sleeping)
- **Additional Instructions**: Any specific preferences or guidance (e.g., focus on breathing, gentle guidance, visualization preferences)

### Meditation Structure
The app follows a 5-section quantum healing meditation structure:
1. **Introduction**: Quantum healing topic introduction tied to user inputs
2. **Settling**: Initial relaxation techniques with <break> tag
3. **Further Relaxation**: Deeper relaxation with <break> tag  
4. **Visualization**: Healing visualization tied to user's condition
5. **Conclusion**: Gentle ending of meditation

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
