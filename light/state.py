"""Assistant state enumerations."""
from enum import Enum


class AssistantState(Enum):
    """Enum for assistant states."""
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    PAUSED = "paused"
    ERROR = "error"
