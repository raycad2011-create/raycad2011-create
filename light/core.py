"""Core coordinator for Light assistant."""
import threading
import traceback
from light.state import AssistantState
from light.voice import VoiceManager
from light.ai import OllamaClient
from light.commands import CommandHandler
from light.memory import MemoryManager


class AssistantCoordinator:
    """Coordinates all assistant functionality."""
    
    def __init__(self, config: dict, on_user_message=None, on_assistant_message=None,
                 on_state_change=None, on_listening_change=None):
        """Initialize coordinator."""
        self.config = config
        self.on_user_message = on_user_message or (lambda x: None)
        self.on_assistant_message = on_assistant_message or (lambda x: None)
        self.on_state_change = on_state_change or (lambda s, l: None)
        self.on_listening_change = on_listening_change or (lambda x: None)
        
        self.state = AssistantState.IDLE
        self.voice = VoiceManager(config)
        self.ai = OllamaClient(config)
        self.commands = CommandHandler(config)
        self.memory = MemoryManager()
        self.listening = False
        self.processing_thread = None
    
    def _set_state(self, state: AssistantState, label: str = ""):
        """Update state and notify listeners."""
        self.state = state
        if not label:
            label = state.value.capitalize()
        self.on_state_change(state, label)
    
    def submit(self, text: str, source: str = "voice"):
        """Submit user input for processing."""
        if not text or not text.strip():
            return
        
        # Record user message
        self.memory.add_event("user_input", {"text": text, "source": source})
        self.on_user_message(text)
        
        # Process in background
        thread = threading.Thread(target=self._process_input, args=(text,), daemon=True)
        thread.start()
    
    def _process_input(self, text: str):
        """Process user input and generate response."""
        try:
            self._set_state(AssistantState.THINKING, "Processing...")
            
            # First check if it's a command
            if self.commands.is_command(text):
                result = self.commands.execute(text)
                if result:
                    self.memory.add_event("command", {"text": text, "result": result})
                    self.on_assistant_message(result)
                    self.voice.speak_async(result)
                    
                    # Check for shutdown
                    if "offline" in result.lower():
                        self._set_state(AssistantState.IDLE)
                    else:
                        self._set_state(AssistantState.IDLE)
                    return
            
            # Fall back to AI
            if not self.ai.is_available():
                response = "I can't reach Ollama right now. Please make sure it is running."
                self.on_assistant_message(response)
                self.voice.speak_async(response)
                self._set_state(AssistantState.IDLE)
                return
            
            self._set_state(AssistantState.THINKING, "Generating response...")
            response = self.ai.generate(text)
            
            if response:
                self.memory.add_event("ai_response", {"prompt": text, "response": response})
                self.on_assistant_message(response)
                self._set_state(AssistantState.SPEAKING, "Speaking...")
                self.voice.speak_async(response)
            else:
                error_msg = "I couldn't generate a response. Please try again."
                self.on_assistant_message(error_msg)
                self.voice.speak_async(error_msg)
            
            self._set_state(AssistantState.IDLE)
        except Exception as e:
            print(f"Error processing input: {e}")
            traceback.print_exc()
            error_msg = "An error occurred. Please try again."
            self.on_assistant_message(error_msg)
            self._set_state(AssistantState.ERROR, "Error")
    
    def start_listening(self):
        """Start listening for voice commands."""
        if self.listening:
            return
        
        self.listening = True
        self.on_listening_change(True)
        self.voice.start_listening(self.submit)
    
    def stop_listening(self):
        """Stop listening for voice commands."""
        if not self.listening:
            return
        
        self.listening = False
        self.on_listening_change(False)
        self.voice.stop_listening()
    
    def is_listening(self) -> bool:
        """Check if currently listening."""
        return self.listening
    
    def start_push_to_talk(self):
        """Start push-to-talk mode (listen once)."""
        self._set_state(AssistantState.LISTENING, "Listening...")
        thread = threading.Thread(target=self._push_to_talk_handler, daemon=True)
        thread.start()
    
    def _push_to_talk_handler(self):
        """Handle push-to-talk."""
        text = self.voice.listen_once()
        self._set_state(AssistantState.IDLE)
        if text:
            self.submit(text, source="voice")
    
    def close(self):
        """Close the coordinator and clean up."""
        self.stop_listening()
        try:
            self.voice.close()
        except Exception as e:
            print(f"Error closing voice: {e}")
