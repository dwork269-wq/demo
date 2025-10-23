import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from openai import OpenAI
from elevenlabs import generate, save, set_api_key
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
    print("✅ pydub imported successfully")
except ImportError as e:
    print(f"⚠️ Warning: pydub not available: {e}")
    PYDUB_AVAILABLE = False
    AudioSegment = None
import tempfile
import re
from dotenv import load_dotenv
import logging

# Configure FFmpeg path for pydub (only if pydub is available)
if PYDUB_AVAILABLE:
    ffmpeg_path = os.path.join(os.environ.get('LOCALAPPDATA', ''), 
                              'Microsoft', 'WinGet', 'Packages', 
                              'Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe', 
                              'ffmpeg-8.0-full_build', 'bin', 'ffmpeg.exe')
    if os.path.exists(ffmpeg_path):
        AudioSegment.converter = ffmpeg_path
        AudioSegment.ffmpeg = ffmpeg_path
        AudioSegment.ffprobe = ffmpeg_path.replace('ffmpeg.exe', 'ffprobe.exe')
        print("✅ FFmpeg configured for pydub")
    else:
        print("⚠️ FFmpeg not found, pydub will use system defaults")

load_dotenv()

app = Flask(__name__, static_folder='public')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# ElevenLabs API key
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
set_api_key(ELEVENLABS_API_KEY)

# Simple password protection
APP_PASSWORD = os.getenv('APP_PASSWORD', 'meditation2024')

# Toggle between mock and real APIs
USE_MOCK_DATA = True  # Set to False when you have API keys

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Meditation App API is running"})

@app.route('/download/<filename>')
def serve_download_file(filename):
    """Serve download files as static content"""
    try:
        file_path = os.path.join('public', 'download', filename)
        
        if os.path.exists(file_path):
            logger.info(f"Serving static file: {file_path}")
            return send_file(file_path, as_attachment=True, download_name=f"meditation_{filename}")
        else:
            logger.warning(f"File not found: {file_path}")
            return jsonify({"error": "File not found"}), 404
            
    except Exception as e:
        logger.error(f"Error serving static file: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-meditation', methods=['POST'])
def generate_meditation():
    try:
        data = request.get_json()
        # Validate password
        if data.get('password') != APP_PASSWORD:
            return jsonify({"error": "Invalid password"}), 401
        
        # Extract user inputs
        focus_area = data.get('focus_area', '')
        duration = data.get('duration', '')
        mood = data.get('mood', '')
        
        if not all([focus_area, duration, mood]):
            return jsonify({"error": "Missing required fields"}), 400
        
        logger.info(f"Generating meditation for: focus={focus_area}, duration={duration}, mood={mood}")
        
        if USE_MOCK_DATA:
            # MOCK RESPONSE - Use when API keys are not available
            logger.info("Using mock data (API keys not available)")
            
            mock_meditation_text = f"""[CHAPTER_1_START]
**Welcome to Your Personal {focus_area.title()} Journey**

Take a moment to settle into this space. <break time="3s"/> Feel the weight of your body supported by the surface beneath you. <prosody rate="slow">Breathe deeply and allow yourself to arrive fully in this moment.</prosody>

As we begin this {duration} meditation focused on {focus_area}, notice how you're feeling right now. <emphasis level="strong">There's no need to change anything</emphasis> - simply observe with gentle curiosity.

<prosody pitch="low">Let your breathing become your anchor</prosody> to this present moment. <break time="2s"/> Inhale slowly through your nose, <break time="1s"/> and exhale gently through your mouth.
[CHAPTER_1_END]

[CHAPTER_2_START]
**Deepening Your Practice**

Now, as we move deeper into this meditation, imagine a warm, golden light surrounding your body. <prosody rate="slow">This light represents the calm and peace you're cultivating within.</prosody>

*Feel this light gently penetrating every cell of your being*, bringing with it a sense of {mood.replace(' and ', ' and ').lower()}. <break time="3s"/>

<emphasis level="strong">With each breath, you're creating space</emphasis> for whatever you need most right now. Whether that's rest, healing, clarity, or simply being present with what is.

<prosody rate="x-slow">Allow any thoughts or sensations to arise and pass like clouds in a vast sky.</prosody> You are the sky - vast, open, and unchanging.
[CHAPTER_2_END]

[CHAPTER_3_START]
**Integration and Gratitude**

As we gently bring this meditation to a close, take a moment to appreciate yourself for showing up. <break time="2s"/> *You've given yourself the gift of presence and mindfulness.*

<prosody pitch="low">Feel gratitude for your body</prosody> - for your breath, your heartbeat, your ability to experience this moment. <emphasis level="strong">You are exactly where you need to be.</emphasis>

Slowly begin to wiggle your fingers and toes. <break time="1s"/> Gently move your head from side to side. <break time="1s"/> When you're ready, open your eyes and carry this sense of peace with you into your day.

*Remember, this calm is always available to you* - you can return to this feeling anytime by simply taking a few conscious breaths.
[CHAPTER_3_END]"""

            # Parse chapters from the mock text
            chapters = parse_chapters(mock_meditation_text)
            
            # Create a mock audio file
            download_dir = os.path.join('public', 'download')
            os.makedirs(download_dir, exist_ok=True)
            
            import uuid
            mock_filename = f"meditation_{uuid.uuid4().hex[:8]}.mp3"
            mock_file_path = os.path.join(download_dir, mock_filename)
            
            # Create a simple audio file (1 minute of silence with a gentle tone)
            try:
                mock_audio = AudioSegment.sine(440).apply_gain(-30)  # Gentle A note
                mock_audio = mock_audio[:60000]  # 1 minute duration
                mock_audio.export(mock_file_path, format="mp3")
                logger.info(f"Mock audio file created: {mock_file_path}")
            except Exception as e:
                logger.warning(f"Could not create mock audio file: {e}")
                with open(mock_file_path, 'w') as f:
                    f.write("Mock audio file")
            
            logger.info("Mock meditation generated successfully")
            
            return jsonify({
                "success": True,
                "meditation_text": mock_meditation_text,
                "chapters": chapters,
                "audio_url": f"/download/{mock_filename}"
            })
        
        else:
            # REAL API CALLS - Use when you have API keys
            logger.info("Using real APIs (OpenAI + ElevenLabs)")
            
            # Create meditation prompt with SSML support
            prompt = f"""
            Create a personalized meditation script with the following specifications:
            - Focus Area: {focus_area}
            - Duration: {duration}
            - Mood/Energy: {mood}
            
            Please structure the meditation into exactly 3 chapters, each marked with clear tags:
            
            [CHAPTER_1_START]
            [CHAPTER_1_END]
            
            [CHAPTER_2_START]
            [CHAPTER_2_END]
            
            [CHAPTER_3_START]
            [CHAPTER_3_END]
            
            Each chapter should be approximately {int(duration.split()[0]) // 3} minutes long when spoken at a calm pace.
            Make the meditation deeply personal and tailored to the user's needs.
            Include breathing exercises, visualization, and mindfulness techniques.
            
            IMPORTANT: Use SSML tags for speech control:
            - Use <prosody rate="slow">text</prosody> for slower speech
            - Use <prosody rate="x-slow">text</prosody> for very slow speech
            - Use <emphasis level="strong">text</emphasis> for emphasis
            - Use <break time="2s"/> for pauses
            - Use <prosody pitch="low">text</prosody> for lower pitch
            
            Example: "Take a deep breath <break time="3s"/> and <emphasis level="strong">feel</emphasis> the calm <prosody rate="slow">flowing through your body</prosody>."
            """
        
            # Generate meditation text using OpenAI
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert meditation guide who creates personalized, transformative meditation experiences."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            meditation_text = response.choices[0].message.content
            logger.info("Meditation text generated successfully")
            
            # Parse chapters from the generated text
            chapters = parse_chapters(meditation_text)
            
            if len(chapters) != 3:
                return jsonify({"error": "Failed to parse exactly 3 chapters"}), 500
            
            # Convert chapters to speech
            audio_files = []
            for i, chapter in enumerate(chapters):
                logger.info(f"Converting chapter {i+1} to speech...")
                audio_file = text_to_speech(chapter, f"chapter_{i+1}")
                audio_files.append(audio_file)
            
            # Create final meditation audio
            final_audio_path = create_final_meditation(audio_files)
            
            # Debug logging
            logger.info(f"Final audio path: {final_audio_path}")
            logger.info(f"Basename: {os.path.basename(final_audio_path)}")
            
            return jsonify({
                "success": True,
                "meditation_text": meditation_text,
                "chapters": chapters,
                "audio_url": f"/download/{os.path.basename(final_audio_path)}"
            })
        
    except Exception as e:
        logger.error(f"Error generating meditation: {str(e)}")
        return jsonify({"error": str(e)}), 500

def parse_chapters(text):
    """Parse meditation text into 3 chapters based on tags"""
    chapters = []
    
    # Find all chapter sections
    chapter_pattern = r'\[CHAPTER_(\d+)_START\](.*?)\[CHAPTER_\d+_END\]'
    matches = re.findall(chapter_pattern, text, re.DOTALL)
    
    for match in matches:
        chapter_num, content = match
        # Clean up the content
        content = content.strip()
        chapters.append(content)
    
    return chapters

def text_to_speech(text, filename):
    """Convert text to speech using ElevenLabs"""
    try:
        # Try different voice approaches
        voices_to_try = [
            "Priyanka Sogam",  # Voice name
            "21m00Tcm4TlvDq8ikWAM",  # Possible voice ID
            "Rachel",  # Fallback voice
            "Adam",  # Another fallback
            "Antoni"  # Another fallback
        ]
        
        audio = None
        last_error = None
        
        for voice in voices_to_try:
            try:
                logger.info(f"Trying voice: {voice}")
                audio = generate(
                    text=text,
                    voice=voice,
                    model="eleven_multilingual_v2"
                )
                logger.info(f"Successfully used voice: {voice}")
                break
            except Exception as e:
                last_error = e
                logger.warning(f"Failed to use voice '{voice}': {str(e)}")
                continue
        
        if audio is None:
            raise Exception(f"Could not generate audio with any voice. Last error: {last_error}")
        
        # Save to download directory
        download_dir = os.path.join('public', 'download')
        os.makedirs(download_dir, exist_ok=True)
        
        # Create unique filename
        import uuid
        unique_filename = f"{filename}_{uuid.uuid4().hex[:8]}.mp3"
        file_path = os.path.join(download_dir, unique_filename)
        
        save(audio, file_path)
        
        return file_path
        
    except Exception as e:
        logger.error(f"Error in text-to-speech: {str(e)}")
        raise

def create_final_meditation(audio_files):
    """Combine audio files with silence and background music"""
    if not PYDUB_AVAILABLE:
        logger.error("pydub is not available - cannot create final meditation")
        return None
        
    try:
        # Create 1 minute of silence
        silence = AudioSegment.silent(duration=60000)  # 60 seconds
        
        # Load background music
        background_music_path = "background_music.mp3"  # Place your background music file here
        
        try:
            if os.path.exists(background_music_path):
                background_music = AudioSegment.from_mp3(background_music_path)
                # Lower the volume of background music
                background_music = background_music.apply_gain(-15)
            else:
                # Fallback to ambient tone if background music file not found
                logger.warning("Background music file not found, using ambient tone")
                background_music = AudioSegment.sine(220).apply_gain(-20)
        except Exception as e:
            logger.warning(f"Error loading background music: {e}, using ambient tone")
            background_music = AudioSegment.sine(220).apply_gain(-20)
        
        # Load chapter audios
        chapter_audios = []
        for audio_file in audio_files:
            audio = AudioSegment.from_mp3(audio_file)
            chapter_audios.append(audio)
        
        # Create final meditation
        final_audio = AudioSegment.empty()
        
        for i, chapter_audio in enumerate(chapter_audios):
            # Add chapter audio
            final_audio += chapter_audio
            
            # Add silence between chapters (except after the last one)
            if i < len(chapter_audios) - 1:
                final_audio += silence
        
        # Extend background music to match the length of the meditation
        background_music = background_music[:len(final_audio)]
        
        # Mix background music with the meditation
        final_audio = final_audio.overlay(background_music)
        
        # Save final audio to download directory
        download_dir = os.path.join('public', 'download')
        os.makedirs(download_dir, exist_ok=True)
        
        # Create unique filename for final meditation
        import uuid
        unique_filename = f"meditation_{uuid.uuid4().hex[:8]}.mp3"
        final_path = os.path.join(download_dir, unique_filename)
        
        final_audio.export(final_path, format="mp3")
        
        logger.info(f"Final meditation created: {final_path}")
        return final_path
        
    except Exception as e:
        logger.error(f"Error creating final meditation: {str(e)}")
        raise

@app.route('/api/download/<filename>')
def download_file(filename):
    """Serve the generated meditation audio file"""
    try:
        # Look for the file in the public/download directory
        file_path = os.path.join('public', 'download', filename)
        
        logger.info(f"Looking for file: {file_path}")
        logger.info(f"File exists: {os.path.exists(file_path)}")
        
        if os.path.exists(file_path):
            logger.info(f"Serving file: {file_path}")
            return send_file(file_path, as_attachment=True, download_name=f"meditation_{filename}")
        else:
            # List files in download directory for debugging
            download_dir = os.path.join('public', 'download')
            if os.path.exists(download_dir):
                download_files = os.listdir(download_dir)
                logger.info(f"Files in download directory: {download_files}")
            else:
                logger.info("Download directory does not exist")
            return jsonify({"error": f"File not found: {filename}"}), 404
            
    except Exception as e:
        logger.error(f"Error serving file: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
