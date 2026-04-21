// Voice recognition and synthesis utilities
class VoiceManager {
  constructor() {
    this.recognition = null;
    this.synthesis = window.speechSynthesis;
    this.isListening = false;
    this.isSpeaking = false;
    this.voices = [];
    this.selectedVoice = null;
    
    this.initializeRecognition();
    this.initializeSynthesis();
  }

  initializeRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      this.recognition = new SpeechRecognition();
      
      this.recognition.continuous = false;
      this.recognition.interimResults = true;
      this.recognition.lang = 'en-US';
      
      this.recognition.onstart = () => {
        this.isListening = true;
        this.onListeningStart?.();
      };
      
      this.recognition.onend = () => {
        this.isListening = false;
        this.onListeningEnd?.();
      };
      
      this.recognition.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }
        
        this.onTranscript?.(finalTranscript, interimTranscript);
      };
      
      this.recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        this.onError?.(event.error);
      };
    }
  }

  initializeSynthesis() {
    if (this.synthesis) {
      // Load voices
      const loadVoices = () => {
        this.voices = this.synthesis.getVoices();
        // Prefer female voices for AI assistant
        this.selectedVoice = this.voices.find(voice => 
          voice.name.includes('Female') || 
          voice.name.includes('Samantha') ||
          voice.name.includes('Karen') ||
          voice.name.includes('Moira')
        ) || this.voices.find(voice => voice.lang.startsWith('en')) || this.voices[0];
      };
      
      loadVoices();
      this.synthesis.onvoiceschanged = loadVoices;
    }
  }

  startListening() {
    if (this.recognition && !this.isListening) {
      try {
        this.recognition.start();
        return true;
      } catch (error) {
        console.error('Failed to start speech recognition:', error);
        return false;
      }
    }
    return false;
  }

  stopListening() {
    if (this.recognition && this.isListening) {
      this.recognition.stop();
    }
  }

  speak(text, options = {}) {
    if (!this.synthesis) return false;
    
    // Stop any current speech
    this.synthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Configure voice
    utterance.voice = this.selectedVoice;
    utterance.rate = options.rate || 0.9;
    utterance.pitch = options.pitch || 1.0;
    utterance.volume = options.volume || 0.8;
    
    utterance.onstart = () => {
      this.isSpeaking = true;
      this.onSpeakStart?.(text);
    };
    
    utterance.onend = () => {
      this.isSpeaking = false;
      this.onSpeakEnd?.(text);
    };
    
    utterance.onerror = (event) => {
      this.isSpeaking = false;
      console.error('Speech synthesis error:', event.error);
      this.onSpeakError?.(event.error);
    };
    
    this.synthesis.speak(utterance);
    return true;
  }

  stopSpeaking() {
    if (this.synthesis) {
      this.synthesis.cancel();
      this.isSpeaking = false;
    }
  }

  isSupported() {
    return !!(this.recognition && this.synthesis);
  }

  // Event handlers (to be set by components)
  onListeningStart = null;
  onListeningEnd = null;
  onTranscript = null;
  onError = null;
  onSpeakStart = null;
  onSpeakEnd = null;
  onSpeakError = null;
}

// Create singleton instance
export const voiceManager = new VoiceManager();

// Utility functions
export const isVoiceSupported = () => voiceManager.isSupported();

export const startVoiceInput = () => voiceManager.startListening();

export const stopVoiceInput = () => voiceManager.stopListening();

export const speakText = (text, options) => voiceManager.speak(text, options);

export const stopSpeaking = () => voiceManager.stopSpeaking();

// Clean text for speech (remove markdown, HTML, etc.)
export const cleanTextForSpeech = (text) => {
  return text
    .replace(/\*\*(.*?)\*\*/g, '$1') // Remove bold markdown
    .replace(/\*(.*?)\*/g, '$1')     // Remove italic markdown
    .replace(/<[^>]*>/g, '')         // Remove HTML tags
    .replace(/[🎉🚀✅❌⚡🔥🌟💡📱🎯🎨🧠]/g, '') // Remove emojis
    .replace(/\s+/g, ' ')            // Normalize whitespace
    .trim();
};