# Integration Architecture Guide

This document explains how the Voxelle system works and how all the pieces fit together.

## System Architecture

```
                    ┌─────────────────────────┐
                    │   AI Core Server        │
                    │  (Voxelle)              │
                    │  :7272                  │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
                    ▼            ▼            ▼
            ┌──────────────┐ ┌──────────┐ ┌──────────┐
            │  Discord     │ │ Twitch   │ │ VTube    │
            │  Bot         │ │ Monitor  │ │ Studio   │
            │  :8000       │ │ :5000    │ │ :8001    │
            └──────────────┘ └──────────┘ └──────────┘
                    │            │            │
                    └────────────┼────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  Input/Output Streams   │
                    │ (Chat, Voice, Emotions) │
                    └─────────────────────────┘
```

## Core Server (`src/`)

The Voxelle Core Server is the brain of the system. It handles:

### Features
- **AI Processing**: Text generation, conversation management
- **Audio Processing**: Text-to-speech, speech-to-text, voice filtering
- **Content Generation**: Images, emotions, responses
- **API Server**: REST and WebSocket endpoints for applications
- **Model Management**: Loading and running AI models

### Configuration (`config.yaml`)
```yaml
server:
  host: 127.0.0.1
  port: 7272

ai:
  model: "gpt-3.5-turbo"
  temperature: 0.7

tts:
  engine: "pyttsx3"
  
stt:
  engine: "whisper"
```

### API Endpoints
- `GET  /api/status` - Server health check
- `POST /api/generate` - Generate text response
- `POST /api/tts` - Convert text to speech
- `POST /api/stt` - Convert speech to text
- `WS   /ws` - WebSocket for real-time communication

---

## Discord Integration (`apps/discord/`)

Connects Voxelle to Discord servers, enabling:

### Features
- **Text Chat**: Respond to messages in text channels
- **Voice Chat**: Join voice channels and have real-time conversations
- **Commands**: Slash commands for managing the bot
- **Audio Processing**: Record and playback voice

### Architecture
```
Discord User → Discord API → Discord Bot Client → WebSocket → Core Server
                                  ↓
                            Recording/Playback
```

### Configuration (`apps/discord/config.yaml`)
```yaml
jaison-api-endpoint: "http://127.0.0.1:7272"
jaison-ws-endpoint: "ws://127.0.0.1:7272"
opus-filepath: null  # Only needed on non-Windows systems
idle-interval: 30    # Seconds before responding in voice
```

### Workflow
1. User sends message or joins voice channel
2. Discord bot captures the input
3. Bot sends to Core Server via WebSocket
4. Core Server processes (STT if voice, NLP for response)
5. Core Server generates response (TTS if needed)
6. Bot plays/sends response back to Discord

### Customization
Edit `apps/discord/src/commands/` to add custom commands:
```python
@app.slash_command(...)
async def my_command(ctx):
    # Custom command logic
```

---

## Twitch Integration (`apps/twitch/`)

Monitors and responds to Twitch chat and alerts:

### Features
- **Chat Monitoring**: Real-time Twitch chat
- **Alert Responses**: React to follows, subs, raids, etc.
- **Chat Filtering**: Keyword, highlight, or bits-based filtering
- **Event Summaries**: Periodic chat summaries

### Architecture
```
Twitch API → Twitch Monitor → EventSub → Core Server
Twitch Chat → Chat Monitor → Core Server
```

### Configuration (`apps/twitch/config.yaml`)
```yaml
twitch-bot-id: "YOUR_USER_ID"
twitch-target-id: "YOUR_CHANNEL_ID"
jaison-api-endpoint: "http://127.0.0.1:7272"
jaison-ws-endpoint: "ws://127.0.0.1:7272"
chat-mode: "KEYWORD"  # ALL, KEYWORD, HIGHLIGHT, BITS, DISABLE
chat-keywords: "hello,hi,hey"
chat-bits-threshold: 100
summary-interval: 10
```

### Workflow
1. **First Time**:
   - Run `python apps/twitch/src/auth.py`
   - Click authentication link in logs
   - Browser redirects with auth token
   - App saves tokens for future use

2. **Runtime**:
   - Monitors Twitch chat continuously
   - Filters messages based on mode
   - Sends relevant messages to Core Server
   - Monitors alerts (follows, subs, raids)
   - Summarizes chat activity periodically

### Chat Filtering Modes
- **ALL**: Every message
- **KEYWORD**: Messages containing keywords from `chat-keywords`
- **HIGHLIGHT**: Only highlighted messages (streamer clicks highlight)
- **BITS**: Only messages with ≥ `chat-bits-threshold` bits
- **DISABLE**: Chat disabled

---

## VTube Studio Integration (`apps/vts/`)

Animates a VTuber model and adds emotion to responses:

### Features
- **Model Animation**: Control hotkeys for expressions
- **Emotion Recognition**: Detect emotion in AI responses
- **Idle Animations**: Loop idle animations while waiting
- **Lipsync**: Synchronize model mouth to audio

### Architecture
```
VTube Studio API ↔ VTS Plugin (Python) ↔ Core Server
                   ↓
            Hotkey Triggers (JSON)
```

### Configuration (`apps/vts/config.yaml`)
```yaml
vts_url: 'ws://localhost:8001'
vts_hotkey_config_file: 'vts_hotkeys/default.json'
jaison_ws_endpoint: 'ws://localhost:7272'
```

### Hotkey Config (`vts_hotkeys/default.json`)
```json
{
  "idle_animation": "idle",
  "emotions": {
    "happy": "smile",
    "sad": "cry",
    "angry": "angry",
    "surprised": "surprise"
  },
  "triggers": [
    {
      "name": "greeting",
      "keywords": ["hello", "hi", "hey"],
      "animation": "wave"
    }
  ]
}
```

### Workflow
1. Core Server generates response with emotion
2. VTS integration analyzes emotion
3. Looks up corresponding hotkey
4. Sends hotkey trigger to VTube Studio
5. VTube Studio plays animation
6. Audio playback triggers lipsync

---

## Data Flow Example: Discord Message

Here's what happens when someone sends a Discord message:

```
1. User in Discord: "Hello Voxelle!"
   ↓
2. Discord Bot receives event
   ↓
3. Bot connects to Core Server WebSocket
   ↓
4. Core Server receives: {type: "message", content: "Hello Voxelle!"}
   ↓
5. Core Server processes:
   - Checks personality/character context
   - Uses AI to generate response
   - Adds tone/emotion metadata
   ↓
6. Core Server returns: {
     content: "Hi there! How are you doing today?",
     emotion: "happy",
     should_tts: true
   }
   ↓
7. Discord Bot receives response
   ↓
8. If voice channel:
   - TTS converts text to audio
   - Plays audio in voice channel
   ↓
9. If text channel:
   - Posts text response directly
```

---

## Communication Protocol

All applications communicate with Core Server via:

### REST API
```
POST /api/generate
Content-Type: application/json

{
  "text": "User input",
  "context": "conversation history",
  "model_params": {...}
}

Response:
{
  "response": "AI generated text",
  "emotion": "happy",
  "metadata": {...}
}
```

### WebSocket
```
Client connects to ws://127.0.0.1:7272

// Send message
{
  "type": "message",
  "content": "User input",
  "source": "discord"
}

// Receive response
{
  "type": "response",
  "content": "AI response",
  "emotion": "happy"
}
```

---

## Customization Examples

### Add Custom Command to Discord Bot
```python
# apps/discord/src/commands/custom.py

@app.slash_command(name="ask", description="Ask Voxelle something")
async def ask_command(ctx, question: str):
    # Send to Core Server
    response = await voxelle.generate(question)
    await ctx.respond(response.content)
```

### Add New Chat Filter for Twitch
```python
# apps/twitch/src/utils/chat_filter.py

def custom_filter(message):
    """Custom chat filtering logic"""
    # Filter based on user level, account age, etc.
    return user_is_legitimate(message.user)
```

### Create Custom VTube Studio Emotion
```json
{
  "emotions": {
    "confused": "tilt_head",
    "excited": "jump_and_clap",
    "tired": "yawn"
  }
}
```

---

## Performance Considerations

### API Response Times
- Text generation: 1-5 seconds (depends on model)
- TTS: 0.5-2 seconds
- STT: 1-3 seconds
- VTS command: <100ms

### Resource Usage
- Core Server: 2-4 GB RAM, varies by model size
- Discord Bot: 200-500 MB RAM
- Twitch Monitor: 100-200 MB RAM
- VTS Plugin: 50-100 MB RAM

### Scaling
For multiple servers/channels:
- Run multiple instances of Discord bot
- Each connects to same Core Server
- Core Server load balances requests

---

## Troubleshooting Inter-App Communication

### Apps Can't Find Core Server
```bash
# Check Core Server is running
python manager.py core

# Check port 7272 is accessible
curl http://127.0.0.1:7272/api/status

# Verify endpoint in app config.yaml
# Should match: http://127.0.0.1:7272
```

### Async Timeout Issues
```bash
# Increase timeout in app config
timeout: 30  # seconds

# Check network between apps
# They should all be on same machine or network
```

### Mixed Audio/Response Delays
```bash
# Reduce latency:
# 1. Use faster TTS engine (pyttsx3 vs Azure)
# 2. Reduce model temperature for faster generation
# 3. Cache common responses
# 4. Use GPU acceleration if available
```

---

## Advanced: Running on Multiple Machines

You can run apps on different machines:

### Machine A (Core Server)
```bash
# config.yaml
server:
  host: "0.0.0.0"  # Listen on all interfaces
  port: 7272
```

### Machine B (Discord Bot)
```bash
# apps/discord/config.yaml
jaison-api-endpoint: "http://192.168.1.100:7272"
jaison-ws-endpoint: "ws://192.168.1.100:7272"
```

### Machine C (Twitch)
```bash
# apps/twitch/config.yaml
jaison-api-endpoint: "http://192.168.1.100:7272"
jaison-ws-endpoint: "ws://192.168.1.100:7272"
```

⚠️ **Security Warning**: Open ports on your network are a security risk. Use VPN or firewalls to restrict access.

---

For more details, see [README-UNIFIED.md](README-UNIFIED.md).
