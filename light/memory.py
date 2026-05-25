"""Memory management for Light."""
import json
import uuid
from datetime import datetime
from pathlib import Path


class MemoryManager:
    """Manages conversation and interaction memory."""
    
    def __init__(self, memory_file: str = "memory.json"):
        """Initialize memory manager."""
        self.memory_file = Path(memory_file)
        self.memory = self._load_memory()
    
    def _load_memory(self) -> list:
        """Load memory from file."""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading memory: {e}")
                return []
        return []
    
    def _save_memory(self):
        """Save memory to file."""
        try:
            with open(self.memory_file, "w") as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            print(f"Error saving memory: {e}")
    
    def add_event(self, event_type: str, content: dict, metadata: dict = None):
        """Add an event to memory."""
        event = {
            "id": str(uuid.uuid4())[:12],
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "content": content,
            "metadata": metadata or {}
        }
        self.memory.append(event)
        self._save_memory()
    
    def get_events(self, event_type: str = None) -> list:
        """Get events from memory, optionally filtered by type."""
        if event_type:
            return [e for e in self.memory if e.get("type") == event_type]
        return self.memory
    
    def clear_memory(self):
        """Clear all memory."""
        self.memory = []
        self._save_memory()
