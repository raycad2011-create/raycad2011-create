"""Command handler for Light."""
import subprocess
import webbrowser
from light.utils import get_current_time, get_current_date


class CommandHandler:
    """Handles local commands without AI."""
    
    def __init__(self, config: dict):
        """Initialize command handler."""
        self.config = config
        self.commands_config = config.get("commands", {})
        self.websites = self.commands_config.get("websites", {})
        self.apps = self.commands_config.get("apps", {})
    
    def is_command(self, text: str) -> bool:
        """Check if text is a command."""
        text_lower = text.lower()
        
        # Check built-in commands
        if any(keyword in text_lower for keyword in [
            "open", "what time", "what day", "current time", "current date",
            "tell me the time", "tell me the date", "date", "time"
        ]):
            return True
        
        # Check configured commands
        for website in self.websites.keys():
            if website in text_lower:
                return True
        
        for app in self.apps.keys():
            if app in text_lower:
                return True
        
        return False
    
    def execute(self, text: str):
        """Execute a command and return result or None if not found."""
        text_lower = text.lower()
        
        # Time/Date commands
        if any(kw in text_lower for kw in ["what time", "tell me the time", "current time", "what's the time"]):
            return f"The time is {get_current_time()}"
        
        if any(kw in text_lower for kw in ["what day", "current date", "tell me the date", "what's the date", "what date"]):
            return f"Today is {get_current_date()}"
        
        # Website commands
        for website_name, url in self.websites.items():
            if website_name in text_lower:
                try:
                    webbrowser.open(url)
                    return f"Opening {website_name}"
                except Exception as e:
                    return f"Failed to open {website_name}: {str(e)}"
        
        # App commands
        for app_name, app_path in self.apps.items():
            if app_name in text_lower:
                try:
                    subprocess.Popen(app_path, shell=True)
                    return f"Opening {app_name}"
                except Exception as e:
                    return f"Failed to open {app_name}: {str(e)}"
        
        # Shutdown command
        if "shutdown" in text_lower or ("close" in text_lower and "light" in text_lower):
            return "Light offline."
        
        return None
