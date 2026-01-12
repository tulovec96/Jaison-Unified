# Voxelle - Quick Setup Guide

Welcome to Voxelle! This guide will help you get up and running quickly.

## ⚡ 5-Minute Quick Start

### Step 1: Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements-all.txt
```

### Step 3: Configure Core Server
```bash
# Copy template to config
cp config.yaml.template config.yaml

# Edit with your settings (API keys, model preferences, etc.)
# See config.yaml.template for detailed options
```

### Step 4: Start Core Server
```bash
python manager.py core
```

You should see: `API: http://localhost:7272` and `WebSocket: ws://localhost:7272`

---

## 🤖 Setting Up Applications

Once the core server is running, you can enable integrations:

### Discord Bot

1. **Create Discord Application**:
   - Go to https://discord.com/developers/applications
   - Click "New Application"
   - Go to "Bot" → "Add Bot"
   - Copy the token

2. **Configure Discord App**:
   ```bash
   cd apps/discord
   cp .env-template .env
   # Edit .env and paste your Discord bot token
   ```

3. **Invite Bot to Server**:
   - In Developer Portal, go to OAuth2 → URL Generator
   - Select "bot" scope and "Administrator" permission
   - Copy the generated URL and open it in your browser

4. **Run Discord Bot**:
   ```bash
   python manager.py discord
   # Or directly:
   python apps/discord/src/main.py
   ```

### Twitch Integration

1. **Create Twitch Application**:
   - Go to https://dev.twitch.tv/console
   - Create New Application
   - Set OAuth Redirect URLs:
     - `http://localhost:5000/auth/redirect/code`
     - `http://localhost:5000/auth/redirect/tokens`
   - Copy Client ID and Client Secret

2. **Configure Twitch App**:
   ```bash
   cd apps/twitch
   cp .env-template .env
   # Edit .env with your Client ID and Secret
   ```

3. **Authenticate**:
   ```bash
   python src/auth.py
   # Click the link in the log message to authorize
   ```

4. **Configure Settings**:
   ```bash
   # Edit config.yaml with your Twitch User ID
   # You can find yours at: https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/
   ```

5. **Run Twitch Integration**:
   ```bash
   python manager.py twitch
   ```

### VTube Studio Integration

1. **Install VTube Studio**:
   - Download from https://denchisoft.com/
   - Install and create your VTuber model

2. **Enable API**:
   - Open VTube Studio
   - Go to Settings → General Settings & External Connections
   - Enable "Allow plugin connections"
   - Enable "Allow webcam/microphone input for animation"

3. **Configure App**:
   ```bash
   cd apps/vts
   # Edit config.yaml:
   # - Set vts_url to your VTube Studio API URL (usually ws://localhost:8001)
   # - Set voxelle_ws_endpoint to ws://localhost:7272
   # - Set vts_hotkey_config_file to your custom hotkey config
   ```

4. **Create Hotkey Config** (optional):
   - Copy `vts_hotkeys/example.json` to create your own
   - Define emotion hotkeys and response triggers

5. **Run VTube Studio Integration**:
   ```bash
   python manager.py vts
   ```

---

## 📁 Project Structure Explained

```
Project-Voxelle/
├── src/                     # Core Voxelle server
│   ├── main.py             # Server entry point
│   ├── utils/              # Utilities and helpers
│   │   ├── jaison.py       # Main server class
│   │   ├── config.py       # Configuration management
│   │   └── operations/     # AI operations (TTS, STT, etc.)
│   └── ...
│
├── apps/                    # Application integrations
│   ├── discord/            # Discord bot
│   │   ├── src/
│   │   ├── config.yaml     # Discord-specific config
│   │   └── requirements.txt
│   ├── twitch/             # Twitch integration
│   │   ├── src/
│   │   ├── config.yaml
│   │   └── requirements.txt
│   └── vts/                # VTube Studio integration
│       ├── src/
│       ├── config.yaml
│       └── requirements.txt
│
├── prompts/                 # AI personality & context
│   ├── characters/         # Character definitions
│   ├── instructions/       # System instructions
│   └── scenes/             # Scene contexts
│
├── models/                  # AI models storage
│   ├── rvc/               # Voice conversion models
│   ├── melotts/           # Text-to-speech models
│   ├── kobold/            # Language models
│   └── mcp/               # MCP models
│
├── config.yaml             # Main configuration (edit this!)
├── requirements-all.txt    # All dependencies
├── manager.py              # System manager script
└── README-UNIFIED.md       # Full documentation
```

---

## 🚀 Usage Examples

### Just Start the Core Server
```bash
python manager.py core
```

### Run Everything (requires all apps configured)
```bash
# Terminal 1: Core server
python manager.py core

# Terminal 2: Discord bot
python manager.py discord

# Terminal 3: Twitch integration
python manager.py twitch

# Terminal 4: VTube Studio
python manager.py vts
```

### Check System Status
```bash
python manager.py status
```

### Run in Debug Mode
```bash
python manager.py core --debug
```

---

## ⚙️ Configuration Files

### Main Config: `config.yaml`
- Server settings (host, port)
- AI model selection and API keys
- TTS/STT preferences
- Personality settings

### Discord: `apps/discord/config.yaml`
- **Voxelle API endpoints**
- Opus library path (Windows only if needed)
- Idle interval for voice responses

### Twitch: `apps/twitch/config.yaml`
- Twitch user IDs
- Chat filtering mode
- Message summaries

### VTube Studio: `apps/vts/config.yaml`
- VTS WebSocket URL
- **Voxelle WebSocket endpoint**
- Hotkey config file path

---

## 🔧 Troubleshooting

### "Port 7272 already in use"
```bash
# Check what's using the port
netstat -ano | findstr :7272  # Windows
lsof -i :7272                 # macOS/Linux

# Change port in config.yaml and restart
```

### Discord bot doesn't respond
1. Check bot has Administrator permission
2. Verify token is correct in `.env`
3. Ensure core server is running on correct endpoint
4. Check Discord bot is joined to your server

### Twitch authentication fails
1. Verify Client ID and Secret in `.env`
2. Ensure redirect URLs match exactly in Twitch Developer Console
3. Run `python src/auth.py` again to re-authenticate

### VTube Studio not responding
1. Ensure VTube Studio is running
2. Check API is enabled in Settings
3. Verify WebSocket URL is correct (usually `ws://localhost:8001`)
4. Check firewall isn't blocking the connection

### Import errors / Missing dependencies
```bash
# Reinstall all dependencies
pip install --upgrade -r requirements-all.txt

# For specific app, install its requirements
pip install -r apps/discord/requirements.txt
pip install -r apps/twitch/requirements.txt
pip install -r apps/vts/requirements.txt
```

---

## 📖 Full Documentation

For complete documentation, see:
- [README-UNIFIED.md](README-UNIFIED.md) - Full system overview
- [DEVELOPER.md](DEVELOPER.md) - Development guide
- [api.yaml](api.yaml) - API specification

---

## 🆘 Getting Help

- **Community Discord**: https://discord.gg/Z8yyEzHsYM
- **Report Issues**: https://github.com/tulovec96/Project-Voxelle/issues
- **Developer**: [@tulovec96](https://github.com/tulovec96) - Voxelle Official
- **Original Project (No Voxelle Support)**: https://github.com/limitcantcode/jaison-core by [@limitcantcode](https://github.com/limitcantcode)

---

Happy AI companioning! 🎉
