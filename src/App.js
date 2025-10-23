import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [formData, setFormData] = useState({
    password: '',
    disease: '',
    symptom: '',
    additional_instruction: ''
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
      
      // Handle ElevenLabs tags - convert to visual indicators
      if (part.startsWith('[') && part.endsWith(']')) {
        const tagContent = part.slice(1, -1).toLowerCase();
        
        // Handle breathing tags
        if (tagContent === 'inhale') {
          return <span key={index} className="breathing-indicator">🫁 Inhale</span>;
        }
        if (tagContent === 'exhale') {
          return <span key={index} className="breathing-indicator">🫁 Exhale</span>;
        }
        
        // Handle pause tags
        if (tagContent.startsWith('pause')) {
          const timeMatch = tagContent.match(/pause (\d+) seconds?/);
          const seconds = timeMatch ? timeMatch[1] : '2';
          return <span key={index} className="pause-indicator">⏸️ {seconds}s pause</span>;
        }
        
        // Handle whisper tag
        if (tagContent === 'whisper') {
          return <span key={index} className="whisper-indicator">🤫 Whisper</span>;
        }
        
        // For other tags, just remove them
        return null;
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
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
      const response = await axios.post(`${apiUrl}/api/generate-meditation`, formData);
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
        <h1>🧘 Quantum Healing Meditation Creator</h1>
        <p>Create personalized quantum healing meditations powered by AI</p>
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
                <label htmlFor="disease">What disease or condition would you like to address?</label>
                <input
                  type="text"
                  id="disease"
                  name="disease"
                  value={formData.disease}
                  onChange={handleInputChange}
                  required
                  placeholder="e.g., anxiety, chronic pain, insomnia"
                />
              </div>

              <div className="form-group">
                <label htmlFor="symptom">What specific symptom are you experiencing?</label>
                <input
                  type="text"
                  id="symptom"
                  name="symptom"
                  value={formData.symptom}
                  onChange={handleInputChange}
                  required
                  placeholder="e.g., racing thoughts, muscle tension, difficulty falling asleep"
                />
              </div>

              <div className="form-group">
                <label htmlFor="additional_instruction">Any additional instructions or preferences?</label>
                <textarea
                  id="additional_instruction"
                  name="additional_instruction"
                  value={formData.additional_instruction}
                  onChange={handleInputChange}
                  required
                  placeholder="e.g., focus on breathing, visualize healing light, gentle guidance"
                  rows="3"
                />
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
                  ✨ Generating quantum healing meditation<br/>
                  📖 Parsing into 3 chapters<br/>
                  🎙️ Converting chapters to speech<br/>
                  ⏸️ Adding 1-minute breaks<br/>
                  🎵 Mixing with background music<br/>
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
                <source src={`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}${meditation.audio_url}`} type="audio/mpeg" />
                Your browser does not support the audio element.
              </audio>
            </div>

            <div className="meditation-text">
              <h3>Your Meditation Script:</h3>
              <div className="script-content">
                {meditation.meditation_text && meditation.meditation_text.split('\n').map((line, index) => {
                  // Skip empty lines
                  if (line.trim() === '') return null;
                  
                  // Skip break tags (they're used for chapter separation)
                  if (line.includes('<break>')) {
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
        <p>Powered by OpenAI GPT-3.5 & ElevenLabs AI - Quantum Healing Meditation</p>
      </footer>
    </div>
  );
}

export default App;
