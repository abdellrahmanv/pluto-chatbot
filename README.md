# Pluto Chatbot

A simple, smart, human-sounding scenario-based chatbot for Raspberry Pi 4B with USB audio.

## Overview

Pluto is an AI-powered voice assistant that runs entirely on a Raspberry Pi 4B. It listens through a USB microphone, understands your voice commands, and responds with natural-sounding speech.

### Key Features

- **Speech-to-Text**: Uses OpenAI Whisper for accurate voice recognition
- **Text-to-Speech**: Uses Piper TTS for natural, human-like voice output
- **Intent Detection**: Simple keyword-based understanding
- **Scenario-Based**: Modular responses for different conversation types
- **Humanization**: Post-processes responses to sound more natural
- **USB Audio**: Configured for USB Audio Device (Card 3)

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                         User Input                            │
│                       (USB Microphone)                        │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                   Audio Handler Layer                         │
│              (Captures voice via Card 3)                      │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                    STT Layer (Whisper)                        │
│              (Converts speech → text)                         │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                  Intent Detection Layer                       │
│            (Detects: greeting, fun_fact, etc.)                │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                     Scenario Layer                            │
│              (Generates response text)                        │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                   Humanization Layer                          │
│           (Makes responses more natural)                      │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                    TTS Layer (Piper)                          │
│              (Converts text → speech)                         │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                        Output                                 │
│                    (USB Speakers)                             │
└──────────────────────────────────────────────────────────────┘
```

## Hardware Requirements

- **Raspberry Pi 4B** (4GB+ RAM recommended)
- **USB Audio Adapter** (configured as Card 3)
- **USB Microphone** (or mic connected to USB adapter)
- **Speakers** (or headphones connected to USB adapter)
- **MicroSD Card** (32GB+ recommended)
- **Power Supply** (official Raspberry Pi power adapter)

## Software Requirements

- Raspberry Pi OS (64-bit recommended)
- Python 3.8+
- PortAudio
- ALSA audio tools
- FFmpeg

## Installation

### Quick Setup (Automated)

1. **Clone or copy the project to your Raspberry Pi:**
   ```bash
   cd ~/
   # Copy pluto-chatbot folder to home directory
   ```

2. **Run the setup script:**
   ```bash
   cd ~/pluto-chatbot
   chmod +x setup.sh
   ./setup.sh
   ```

   The setup script will:
   - Update system packages
   - Install Python and dependencies
   - Install audio tools
   - Install Whisper
   - Install Piper TTS
   - Download voice models
   - Configure USB audio (Card 3)
   - Create virtual environment
   - Set up directories

3. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```

4. **Verify your USB audio device:**
   ```bash
   aplay -l
   ```
   Make sure you see your USB device as Card 3.

### Manual Setup

If you prefer manual installation, see [MANUAL_SETUP.md](MANUAL_SETUP.md).

## Configuration

Edit `config/config.yaml` to customize:

- **Audio settings** (device, sample rate, etc.)
- **Whisper model** (tiny, base, small, medium, large)
- **Piper voice model** (path and settings)
- **Intent keywords** (add your own triggers)
- **Response messages** (customize Pluto's personality)
- **System settings** (logging, humanization, etc.)

### Audio Device Configuration

If your USB device is not Card 3:
1. Run `aplay -l` to find your device number
2. Update `card_index` in `config/config.yaml`
3. Update `~/.asoundrc` to match your card number

## Usage

### Starting Pluto

**Easy way (recommended):**
```bash
cd ~/pluto-chatbot
./run_pluto.sh
```

**Manual way:**
```bash
cd ~/pluto-chatbot
source venv/bin/activate
python3 main.py
```

> **Important:** Always activate the virtual environment before running Pluto! The `run_pluto.sh` script does this automatically.

### Interacting with Pluto

Once started, Pluto will say "Hello! I'm Pluto, your AI assistant. I'm ready to chat!"

You can then speak commands:

- **"Hey"** or **"Hello"** → Pluto introduces itself
- **"Fun fact"** or **"Tell me something"** → Pluto shares a random fun fact
- Anything else → Pluto asks you to try again

### Stopping Pluto

Press `Ctrl+C` to stop the chatbot gracefully.

## Project Structure

```
pluto-chatbot/
├── main.py                  # Main controller loop
├── setup.sh                 # Automated setup script
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── config/
│   └── config.yaml         # Configuration file
├── data/
│   └── fun_facts.txt       # Fun facts database
├── audio_layer/
│   ├── __init__.py
│   └── audio_manager.py    # Audio input/output handling
├── stt_layer/
│   ├── __init__.py
│   └── whisper_stt.py      # Speech-to-text (Whisper)
├── intent_layer/
│   ├── __init__.py
│   └── intent_detector.py  # Intent detection
├── scenario_layer/
│   ├── __init__.py
│   └── scenario_manager.py # Response generation
├── tts_layer/
│   ├── __init__.py
│   └── piper_tts.py        # Text-to-speech (Piper)
├── utils/
│   ├── __init__.py
│   ├── logger.py           # Logging configuration
│   └── humanizer.py        # Response post-processing
├── logs/                   # Log files (auto-created)
└── temp/                   # Temporary audio files (auto-created)
```

## Extending Pluto

### Adding New Intents

1. **Add keywords** to `config/config.yaml`:
   ```yaml
   intents:
     my_new_intent:
       keywords:
         - "keyword1"
         - "keyword2"
   ```

2. **Add response** in `config/config.yaml`:
   ```yaml
   responses:
     my_new_response: "Your response text here"
   ```

3. **Update scenario_manager.py** to handle the new intent:
   ```python
   elif intent == 'my_new_intent':
       return self._handle_my_new_intent(context)
   ```

### Adding More Fun Facts

Simply edit `data/fun_facts.txt` and add one fact per line.

### Changing Piper Voice

1. Download a different voice model from [Piper releases](https://github.com/rhasspy/piper/releases)
2. Update `model_path` and `config_path` in `config/config.yaml`

## Troubleshooting

### Audio Issues

**No audio input/output:**
```bash
# List audio devices
aplay -l
arecord -l

# Test speaker
speaker-test -c 2 -t wav -l 1

# Test microphone
arecord -D hw:3 -f cd -d 5 test.wav
aplay test.wav
```

**Wrong audio device:**
- Update `card_index` in `config/config.yaml`
- Update `~/.asoundrc` to match

### Whisper Issues

**Slow transcription:**
- Use smaller model: change `model_size` to `tiny` or `base` in config
- Raspberry Pi 4B works best with `tiny` or `base` models

**Poor recognition:**
- Use larger model: try `small` or `medium`
- Improve microphone quality
- Reduce background noise

### Piper Issues

**Piper not found:**
```bash
# Check Piper installation
which piper
~/piper/piper/piper --version

# Add to PATH if needed
export PATH="$HOME/piper/piper:$PATH"
```

**Robotic voice:**
- Adjust `noise_scale` (try 0.8 for more variability)
- Adjust `length_scale` (try 0.9 for faster speech)
- Try a different voice model

### Permission Issues

```bash
# Add user to audio group
sudo usermod -a -G audio $USER

# Reboot for changes to take effect
sudo reboot
```

## Auto-Start on Boot

To start Pluto automatically when Raspberry Pi boots:

```bash
crontab -e
```

Add this line:
```
@reboot cd /home/pi/pluto-chatbot && source venv/bin/activate && python3 main.py >> logs/startup.log 2>&1
```

## Performance Tips

1. **Use smaller Whisper model** (`tiny` or `base`) on Raspberry Pi 4B
2. **Close other applications** to free up RAM
3. **Use wired audio** instead of Bluetooth for lower latency
4. **Overclock safely** if needed (check Raspberry Pi documentation)

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests!

## Credits

- **OpenAI Whisper**: Speech recognition
- **Rhasspy Piper**: Text-to-speech
- Built for Raspberry Pi enthusiasts and voice assistant lovers

## Support

For issues and questions:
1. Check the Troubleshooting section
2. Review the logs in `logs/pluto.log`
3. Open an issue on GitHub

---

**Enjoy chatting with Pluto!** 🤖✨
