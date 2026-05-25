"""Voice input and output handling."""
import threading
import pyttsx3
try:
    import speech_recognition as sr
    HAS_SPEECH_RECOGNITION = True
except ImportError:
    HAS_SPEECH_RECOGNITION = False


class VoiceManager:
    """Manages voice input and output."""
    
    def __init__(self, config: dict):
        """Initialize voice manager with config."""
        self.config = config.get("voice", {})
        self.recognizer = sr.Recognizer() if HAS_SPEECH_RECOGNITION else None
        self.engine = pyttsx3.init()
        self._configure_engine()
        self.is_listening = False
        self.listening_thread = None
    
    def _configure_engine(self):
        """Configure text-to-speech engine."""
        try:
            self.engine.setProperty('rate', self.config.get('rate', 150))
            self.engine.setProperty('volume', self.config.get('volume', 0.9))
        except Exception as e:
            print(f"Error configuring TTS: {e}")
    
    def speak(self, text: str):
        """Speak text synchronously."""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Error speaking: {e}")
    
    def speak_async(self, text: str):
        """Speak text asynchronously."""
        thread = threading.Thread(target=self.speak, args=(text,), daemon=True)
        thread.start()
    
    def listen_once(self):
        """Listen for a single voice command."""
        if not HAS_SPEECH_RECOGNITION or not self.recognizer:
            return None
        
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(
                    source,
                    timeout=self.config.get('listen_timeout', 5),
                    phrase_time_limit=self.config.get('phrase_time_limit', 8)
                )
            
            engine = self.config.get('recognition_engine', 'sphinx')
            if engine == 'google':
                return self.recognizer.recognize_google(audio)
            else:
                return self.recognizer.recognize_sphinx(audio)
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"Recognition service error: {e}")
            return None
        except Exception as e:
            print(f"Error listening: {e}")
            return None
    
    def start_listening(self, callback):
        """Start listening in background thread."""
        if self.is_listening:
            return
        
        self.is_listening = True
        self.listening_thread = threading.Thread(
            target=self._listening_loop,
            args=(callback,),
            daemon=True
        )
        self.listening_thread.start()
    
    def _listening_loop(self, callback):
        """Background listening loop."""
        while self.is_listening:
            text = self.listen_once()
            if text:
                callback(text)
    
    def stop_listening(self):
        """Stop listening."""
        self.is_listening = False
    
    def close(self):
        """Clean up voice resources."""
        self.stop_listening()
        try:
            self.engine.stop()
        except Exception as e:
            print(f"Error closing engine: {e}")
