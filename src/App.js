import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [formData, setFormData] = useState({
    password: '',
    focus_area: '',
    duration: '',
    mood: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [meditation, setMeditation] = useState(null);
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const parseMeditationText = (text) => {
    if (!text) return '';
    
    // Split by various patterns and process each part
    const parts = text.split(/(\*\*.*?\*\*|\*.*?\*|<[^>]*>)/g);
    
    return parts.map((part, index) => {
      if (!part) return null;
      
      // Handle bold text **text**
      if (part.startsWith('**') && part.endsWith('**')) {
        const content = part.slice(2, -2);
        return <strong key={index} className="bold-text">{content}</strong>;
      }
      
      // Handle italic text *text*
      if (part.startsWith('*') && part.endsWith('*') && !part.startsWith('**')) {
        const content = part.slice(1, -1);
        return <em key={index} className="italic-text">{content}</em>;
      }
      
      // Handle SSML tags - convert to visual indicators
      if (part.startsWith('<') && part.endsWith('>')) {
        // Handle break tags
        if (part.includes('break time=')) {
          const timeMatch = part.match(/time="(\d+)s"/);
          const seconds = timeMatch ? timeMatch[1] : '2';
          return <span key={index} className="pause-indicator">⏸️ {seconds}s pause</span>;
        }
        
        // Handle prosody tags
        if (part.includes('prosody')) {
          if (part.includes('rate="slow"')) {
            return <span key={index} className="slow-speech">🐌 Slow</span>;
          }
          if (part.includes('rate="x-slow"')) {
            return <span key={index} className="very-slow-speech">🐌🐌 Very Slow</span>;
          }
          if (part.includes('pitch="low"')) {
            return <span key={index} className="low-pitch">🔉 Low Pitch</span>;
          }
        }
        
        // Handle emphasis tags
        if (part.includes('emphasis level="strong"')) {
          return <span key={index} className="emphasis-indicator">💪 Strong</span>;
        }
        
        // For other tags, just remove them
        return null;
      }
      
      // Regular text
      return <span key={index}>{part}</span>;
    }).filter(Boolean);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setMeditation(null);

    try {
      const response = await axios.post('http://localhost:5000/api/generate-meditation', formData);
      setMeditation(response.data);
      console.log(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred while generating the meditation');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🧘 Custom Meditation Creator</h1>
        <p>Create personalized meditations powered by AI</p>
      </header>

      <main className="App-main">
        {!meditation ? (
          <div className="meditation-form-container">
            <form onSubmit={handleSubmit} className="meditation-form">
              <div className="form-group">
                <label htmlFor="password">Access Password:</label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  required
                  placeholder="Enter access password"
                />
              </div>

              <div className="form-group">
                <label htmlFor="focus_area">What would you like to focus on?</label>
                <select
                  id="focus_area"
                  name="focus_area"
                  value={formData.focus_area}
                  onChange={handleInputChange}
                  required
                >
                  <option value="">Select a focus area</option>
                  <option value="stress relief">Stress Relief</option>
                  <option value="sleep preparation">Sleep Preparation</option>
                  <option value="anxiety management">Anxiety Management</option>
                  <option value="mindfulness">Mindfulness</option>
                  <option value="self-compassion">Self-Compassion</option>
                  <option value="focus and concentration">Focus & Concentration</option>
                  <option value="emotional healing">Emotional Healing</option>
                  <option value="gratitude practice">Gratitude Practice</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="duration">How long would you like to meditate?</label>
                <select
                  id="duration"
                  name="duration"
                  value={formData.duration}
                  onChange={handleInputChange}
                  required
                >
                  <option value="">Select duration</option>
                  <option value="5 minutes">5 minutes</option>
                  <option value="10 minutes">10 minutes</option>
                  <option value="15 minutes">15 minutes</option>
                  <option value="20 minutes">20 minutes</option>
                  <option value="30 minutes">30 minutes</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="mood">What's your current mood or energy level?</label>
                <select
                  id="mood"
                  name="mood"
                  value={formData.mood}
                  onChange={handleInputChange}
                  required
                >
                  <option value="">Select your mood</option>
                  <option value="calm and peaceful">Calm & Peaceful</option>
                  <option value="energized and alert">Energized & Alert</option>
                  <option value="tired and drained">Tired & Drained</option>
                  <option value="anxious and restless">Anxious & Restless</option>
                  <option value="focused and determined">Focused & Determined</option>
                  <option value="emotional and sensitive">Emotional & Sensitive</option>
                  <option value="neutral and balanced">Neutral & Balanced</option>
                </select>
              </div>

              <button type="submit" disabled={isLoading} className="generate-btn">
                {isLoading ? 'Creating Your Meditation...' : 'Create My Meditation'}
              </button>
            </form>

            {error && (
              <div className="error-message">
                <p>{error}</p>
              </div>
            )}

            {isLoading && (
              <div className="loading-container">
                <div className="spinner"></div>
                <p>AI is crafting your personalized meditation...</p>
                <p className="loading-steps">
                  ✨ Generating meditation text<br/>
                  🎙️ Converting to speech<br/>
                  🎵 Adding background music<br/>
                  🔗 Finalizing your meditation
                </p>
              </div>
            )}
          </div>
        ) : (
          <div className="meditation-result">
            <div className="result-header">
              <h2>Your Custom Meditation is Ready!</h2>
              <button 
                onClick={() => setMeditation(null)} 
                className="create-new-btn"
              >
                Create Another Meditation
              </button>
            </div>

            <div className="meditation-player">
              <audio controls className="audio-player">
                <source src={meditation.audio_url} type="audio/mpeg" />
                Your browser does not support the audio element.
              </audio>
            </div>

            <div className="meditation-text">
              <h3>Your Meditation Script:</h3>
              <div className="script-content">
                {meditation.meditation_text && meditation.meditation_text.split('\n').map((line, index) => {
                  // Skip empty lines
                  if (line.trim() === '') return null;
                  
                  // Skip chapter tags
                  if (line.includes('[CHAPTER_') && (line.includes('_START]') || line.includes('_END]'))) {
                    return null;
                  }
                  
                  // Parse and format the line
                  return (
                    <p key={index} className="meditation-line">
                      {parseMeditationText(line)}
                    </p>
                  );
                })}
              </div>
            </div>

            <div className="chapters-section">
              <h3>Meditation Chapters:</h3>
              {meditation.chapters && meditation.chapters.map((chapter, index) => (
                <div key={index} className="chapter">
                  <h4>Chapter {index + 1}</h4>
                  <div className="chapter-content">
                    {chapter.split('\n').map((line, lineIndex) => {
                      if (line.trim() === '') return null;
                      return (
                        <p key={lineIndex} className="chapter-line">
                          {parseMeditationText(line)}
                        </p>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      <footer className="App-footer">
        <p>Powered by OpenAI GPT-3.5 & ElevenLabs AI</p>
      </footer>
    </div>
  );
}

export default App;
