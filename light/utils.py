"""Utility functions for Light."""
import re
import subprocess
import webbrowser
from datetime import datetime


def clean_command(text: str) -> str:
    """Clean and normalize command text."""
    if not text:
        return ""
    return text.strip().lower()


def open_website(url: str) -> str:
    """Open a website in the default browser."""
    try:
        webbrowser.open(url)
        return f"Opening {url}"
    except Exception as e:
        return f"Failed to open website: {str(e)}"


def open_app(app_path: str) -> str:
    """Open an application."""
    try:
        subprocess.Popen(app_path, shell=True)
        return f"Opening {app_path}"
    except Exception as e:
        return f"Failed to open application: {str(e)}"


def get_current_time() -> str:
    """Get the current time."""
    return datetime.now().strftime("%I:%M %p").lstrip("0")


def get_current_date() -> str:
    """Get the current date."""
    return datetime.now().strftime("%A, %B %d, %Y")


def extract_number_from_text(text: str):
    """Extract the first number from text."""
    numbers = re.findall(r'\d+', text)
    return int(numbers[0]) if numbers else None
