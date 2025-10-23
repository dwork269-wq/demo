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

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Load environment variables, but don't fail if .env doesn't exist
try:
    load_dotenv()
except Exception as e:
    logger.warning(f"Could not load .env file: {e}")
    logger.info("Using system environment variables or defaults")

app = Flask(__name__, static_folder='public')
CORS(app)

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY or OPENAI_API_KEY == 'your_openai_api_key_here':
    logger.warning("OpenAI API key not set. Set OPENAI_API_KEY environment variable.")
    openai_client = None
else:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)

# ElevenLabs API key
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
if not ELEVENLABS_API_KEY or ELEVENLABS_API_KEY == 'your_elevenlabs_api_key_here':
    logger.warning("ElevenLabs API key not set. Set ELEVENLABS_API_KEY environment variable.")
else:
    set_api_key(ELEVENLABS_API_KEY)

# Simple password protection
APP_PASSWORD = os.getenv('APP_PASSWORD', 'meditation2024')

# Toggle between hybrid and real APIs
USE_MOCK_DATA = True  # Set to False when you want to use real TTS (expensive)

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

def generate_meditation_text(disease, symptom, additional_instruction):
    """Generate meditation text using OpenAI"""
    try:
        if not openai_client:
            raise Exception("OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.")
        # Create meditation prompt following the new structure
        prompt = f"""#Instruction: write a 10-minute meditation following the below structure. In that meditation, include elevenlabs tags such as [inhale], [exhale], [pause] or [whisper]. To not make it too fast paced, make sure to include a [pause 2 seconds] tag after each sentence. Using "..." also slows the pace down. Take the user inputs into account in the relevant parts of the meditation, as described. Avoid using "now" too much to progress the meditation forward. 

#User input: 
##Disease: {disease}
##Symptom: {symptom}
##additional instruction: {additional_instruction}

#output: output only the meditation itself with the relevant tags, without saying anything else or without including section titles 

#structure of the meditation with instructions for each section: 
##section 1: Introduction to the topic. The general topic is quantum healing. Select a topic at random addressed by Deepak Chopra in his Quantum Healing book without mentioning that book in the meditation. Tie in this general topic with the disease, symptom and additional instruction given by the user above. 
##section 2: start of the meditation, settle the user. Choose any of common techniques to do so. Leave some extra time/silence at the end of this section to allow the user to relax further in silence. End this section with the following tag: <break>
##section 3: further relaxation. Choose any of common techniques to do so. Leave some extra time/silence at the end of this section to allow the user to relax further in silence. End this section with the following tag: <break>
##section 4: visualisation. Introduce the visualisation technique, tie it to the disease, symptom and additional instruction of the user and then start. Choose any of common visualisation techniques to do so. 
##section 5: end of meditation."""
    
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
        return meditation_text
        
    except Exception as e:
        logger.error(f"Error generating meditation text: {str(e)}")
        raise

@app.route('/api/generate-meditation', methods=['POST'])
def generate_meditation():
    try:
        data = request.get_json()
        # Validate password
        if data.get('password') != APP_PASSWORD:
            return jsonify({"error": "Invalid password"}), 401
        
        # Extract user inputs
        disease = data.get('disease', '')
        symptom = data.get('symptom', '')
        additional_instruction = data.get('additional_instruction', '')
        
        if not all([disease, symptom, additional_instruction]):
            return jsonify({"error": "Missing required fields"}), 400
        
        logger.info(f"Generating meditation for: disease={disease}, symptom={symptom}, additional_instruction={additional_instruction}")
        
        if USE_MOCK_DATA:
            # HYBRID MODE - Use real OpenAI text generation but skip TTS
            logger.info("Using hybrid mode: Real OpenAI text + Mock audio")
            
            # Generate real meditation text using OpenAI
            meditation_text = generate_meditation_text(disease, symptom, additional_instruction)

            # Parse chapters from the real meditation text
            chapters = parse_chapters(meditation_text)
            
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
            
            logger.info("Hybrid meditation generated successfully (Real OpenAI + Mock audio)")
            
            return jsonify({
                "success": True,
                "meditation_text": meditation_text,
                "chapters": chapters,
                "audio_url": f"/download/{mock_filename}"
            })
        
        else:
            # REAL API CALLS - Use when you have API keys
            logger.info("Using real APIs (OpenAI + ElevenLabs)")
            
            # Generate meditation text using OpenAI
            meditation_text = generate_meditation_text(disease, symptom, additional_instruction)
            
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
    """Parse meditation text into 3 chapters based on <break> tags"""
    chapters = []
    
    # Split the text by <break> tags
    parts = re.split(r'<break>', text, flags=re.IGNORECASE)
    
    # We expect exactly 3 chapters (2 <break> tags create 3 sections)
    if len(parts) >= 3:
        # Take the first 3 parts as chapters
        for i in range(3):
            content = parts[i].strip()
            chapters.append(content)
    else:
        # Fallback: if we don't have enough <break> tags, split by sections
        # Look for section markers or split by paragraphs
        paragraphs = text.split('\n\n')
        if len(paragraphs) >= 3:
            # Distribute paragraphs across 3 chapters
            chunk_size = len(paragraphs) // 3
            for i in range(3):
                start_idx = i * chunk_size
                if i == 2:  # Last chapter gets remaining paragraphs
                    end_idx = len(paragraphs)
                else:
                    end_idx = (i + 1) * chunk_size
                content = '\n\n'.join(paragraphs[start_idx:end_idx]).strip()
                chapters.append(content)
        else:
            # If we still don't have enough content, just split the text into 3 equal parts
            text_length = len(text)
            chunk_size = text_length // 3
            for i in range(3):
                start_idx = i * chunk_size
                if i == 2:  # Last chapter gets remaining text
                    end_idx = text_length
                else:
                    end_idx = (i + 1) * chunk_size
                content = text[start_idx:end_idx].strip()
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
        # Create 1 minute of silence for breaks between chapters
        silence_break = AudioSegment.silent(duration=60000)  # 60 seconds
        
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
            
            # Add 1-minute silence break between chapters (except after the last one)
            if i < len(chapter_audios) - 1:
                final_audio += silence_break
        
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
