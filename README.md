# Light

Light is a lightweight Windows desktop AI assistant built with Python, CustomTkinter, SpeechRecognition, pyttsx3, and Ollama.

This is Phase 1: a stable local-first assistant that opens as a desktop app, listens to voice, speaks responses, handles simple commands, and sends general questions to a small local Ollama model.

## Phase 1 Features

- Desktop window titled **Light**
- Status display: Online, Listening, Thinking, Responding
- Microphone start/stop button
- Text area showing user commands and assistant responses
- Optional typed command input
- Voice input through SpeechRecognition
- Offline speech recognition by default with PocketSphinx
- Text-to-speech responses with pyttsx3
- Local AI chat through Ollama
- Basic commands like opening websites/apps and telling the time
- Graceful handling for missing microphone, unclear speech, and Ollama connection issues

## Project Structure

```text
Light/
  main.py              Desktop app entry point and UI
  config.json          Model, voice, website, and app settings
  requirements.txt     Python packages
  README.md            Setup and usage guide
  light/
    __init__.py        Package marker
    ai.py              Ollama local AI connection
    commands.py        Local command handling
    config.py          Loads config.json
    core.py            Main coordinator
    memory.py          Conversation memory
    state.py           State enumerations
    utils.py           Small helper functions
    voice.py           Speech input and text-to-speech
```

## Setup Instructions

### 1. Install Python

1. Download Python from [python.org](https://www.python.org/downloads/windows/).
2. Install Python 3.11 or 3.12. Python 3.10 should also work, but 3.11/3.12 are recommended for smoother Windows audio package installs.
3. During installation, check **Add python.exe to PATH**.
4. Open PowerShell and confirm:

```powershell
python --version
```

### 2. Install Ollama

1. Download Ollama for Windows from [ollama.com](https://ollama.com/download/windows).
2. Install it and let it run in the background.
3. Confirm it works:

```powershell
ollama --version
```

### 3. Download a Lightweight Local Model

Required default for this setup:

```powershell
ollama pull llama3.2:1b
```

Light is configured to use `llama3.2:1b` through the local Ollama endpoint at `http://localhost:11434`.

### 4. Create a Virtual Environment

From the project folder:

```powershell
cd "C:\Users\rayca\OneDrive\Documents\Light"
python -m venv .venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate again:

```powershell
.\venv\Scripts\Activate.ps1
```

### 5. Install Requirements

```powershell
pip install -r requirements.txt
```

`PyAudio` is intentionally not required for the app to launch. Light will still open in GUI-only mode without it.

For microphone input, install PyAudio separately:

```powershell
python -m pip install --upgrade pip setuptools wheel
pip install PyAudio
```

If PyAudio does not install cleanly, you can still run Light and type commands in the app.

### 6. Run Light

Make sure Ollama is running, then start the desktop app:

```powershell
python main.py
```

The app opens a window, displays **Light online**, and speaks **Light online**.

Click **Start Listening** to begin voice control. Click **Stop Listening** to pause.

## Example Commands

Try saying or typing:

- `open youtube`
- `open google`
- `open discord`
- `open notepad`
- `open calculator`
- `what time is it`
- `what day is it`
- `explain what RAM is`
- `tell me a joke`
- `who is Albert Einstein`

To close Light, use the window close button or say/type:

```text
shutdown
```

## Configuration

Edit `config.json` to adjust Light without changing code.

### Ollama Model

Default:

```json
"model": "llama3.2:1b"
```

You can change this to any model available locally:

```bash
ollama pull mistral
ollama pull neural-chat
```

Then update `config.json` accordingly.

### Change Speech Recognition

Local/offline default:

```json
"recognition_engine": "sphinx"
```

Optional online recognition:

```json
"recognition_engine": "google"
```

Use `sphinx` for the most local setup. Use `google` only if you want better speech recognition accuracy and are comfortable using SpeechRecognition's online recognizer.

### Add Websites

```json
"websites": {
  "youtube": "https://www.youtube.com",
  "reddit": "https://www.reddit.com"
}
```

Then say:

```text
open reddit
```

### Add or Fix Apps

Simple Windows commands:

```json
"notepad": "notepad",
"calculator": "calc"
```

Discord is configured with a Windows launch command:

```json
"discord": "\"%LOCALAPPDATA%\\Discord\\Update.exe\" --processStart Discord.exe"
```

If an app does not open, update its entry in `config.json`.

## Troubleshooting

### Ollama is not responding

Check that Ollama is installed and running:

```powershell
ollama list
```

If `llama3.2:1b` is missing:

```powershell
ollama pull llama3.2:1b
```

### No microphone is detected

Light will still open and allow typed commands. To enable microphone input:

```powershell
pip install PyAudio
```

Then check Windows microphone access:

1. Open Windows Settings.
2. Go to **Privacy & security**.
3. Open **Microphone**.
4. Allow microphone access for desktop apps.

### Speech recognition is inaccurate

The default `sphinx` mode is lightweight and offline, but less accurate than larger systems. For better accuracy, set `"recognition_engine": "google"` in `config.json`.

### App won't start

Check the console output for errors. Common issues:

1. Missing dependencies: Run `pip install -r requirements.txt` again
2. Ollama not running: Start Ollama from the system tray
3. Config file issues: Ensure `config.json` is in the project root
4. Python version: Ensure Python 3.11+ is installed

## Design Notes

Light intentionally avoids:

- Cloud AI APIs
- OpenAI API keys
- Electron or React
- Heavy frontend frameworks
- Wake words
- Smart home systems
- Face recognition
- Memory databases
- Multi-agent systems

The biggest performance factor is the Ollama model. For a smooth Phase 1 experience, keep the model small and let local commands handle simple tasks before AI is used.
