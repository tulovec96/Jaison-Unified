# 🤖 Project J.A.I.son - Unified Edition

<p align="center">
  <strong>An extensible, open-source AI companion framework with integrated support for Discord, Twitch, VTube Studio, and more</strong>
</p>

<p align="center">
  <strong>Stream with AI. Create with AI. Build with AI.</strong>
</p>

<p align="center">
  <img alt="Project JAIson badge" src="https://img.shields.io/badge/Project-JAIson-blue">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.12+-3776ab?logo=python">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green">
  <img alt="Platform" src="https://img.shields.io/badge/Platform-Windows%20|%20Linux%20|%20macOS-lightgrey">
  <img alt="Status" src="https://img.shields.io/badge/Status-Active-brightgreen">
  <img alt="Maintained" src="https://img.shields.io/badge/Maintained%20by-Community-orange">
</p>

<p align="center">
  <a href="#-about">About</a> •
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-applications">Applications</a> •
  <a href="#-configuration">Configuration</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-development">Development</a> •
  <a href="#-troubleshooting">Troubleshooting</a> •
  <a href="#-community">Community</a> •
  <a href="#-contributors">Contributors</a>
</p>

---

## 📖 About

**Project J.A.I.son** is a comprehensive, production-ready framework for building AI companion applications. This unified distribution brings together the powerful core server with all official integrations—Discord, Twitch, VTube Studio, and a modern web UI—in a single, cohesive package.

### Why J.A.I.son?

- **🎯 Complete Out-of-the-Box** - Everything you need to build AI-powered applications
- **🔒 Your Data, Your Rules** - Run fully locally with zero cloud dependencies
- **🚀 Production-Ready** - Battle-tested code with comprehensive error handling
- **💡 Extensible Architecture** - Build custom integrations with REST API & WebSocket
- **🛠️ Developer-Friendly** - Well-documented, modular, easy to understand and extend

> **Note:** This software uses libraries from the FFmpeg project under the LGPLv2.1. See [LICENSE](LICENSE) for details.

## ✨ Features

### 🧠 Core AI Capabilities
- **🤖 Real-time AI Personality** - Fully customizable AI personality with natural language understanding and generation
- **🔊 Voice Interaction** - Complete audio pipeline: Speech-to-Text (STT), text processing, Text-to-Speech (TTS)
- **💭 Context Awareness** - Maintains conversation history and emotional state across sessions
- **🧬 Model Context Protocol (MCP)** - Extend AI capabilities with tools and integrations
- **⚡ Low-Latency Responses** - Optimized inference for real-time interaction
- **🌐 REST API & WebSocket** - Full-featured APIs for building custom applications
- **💻 Fully Local Execution** - No cloud dependencies—everything runs on your hardware

### 🎯 Integrated Applications

#### Communication
- **💬 Discord Integration** - Chat in text channels with context awareness and participate in voice calls with voice processing
- **📺 Twitch Integration** - Real-time chat monitoring with intelligent filtering, event-driven responses, and stream analytics

#### Animation & Streaming
- **🎭 VTube Studio Integration** - Animate your VTuber model with synchronized emotion reactions, facial expressions, and hotkey responses
- **🎨 Modern Web UI** - Professional SvelteKit + Tailwind dashboard for monitoring and controlling all services in real-time

### 🔧 Technical Strengths
- **Modular Architecture** - Independent services work together seamlessly
- **Error Recovery** - Automatic reconnection and graceful degradation
- **Performance Optimized** - Efficient resource usage, suitable for streaming servers
- **Extensive Customization** - Tweak every aspect of AI behavior through configuration files

---

## 🚀 Quick Start

### Minimum Requirements

Before you begin, ensure you have:

| Requirement | Version | Purpose |
|-------------|---------|---------|
| **Python** | 3.12+ | Runtime environment |
| **FFmpeg** | Latest | Audio/video processing |
| **RAM** | 4GB+ | Processing (8GB recommended) |
| **Disk Space** | 2-3 GB | Dependencies and models |
| **Network** | Stable | API and external integrations |

**Optional but Recommended:**
- **NVIDIA GPU** (CUDA 12.8+) - For faster AI inference (10-50x speedup)
- **Discord Server** - For Discord bot testing
- **Twitch Account** - For Twitch integration
- **VTube Studio** - For animation integration

### ⏱️ Installation in 5 Minutes

```bash
# 1️⃣  Navigate to project directory
cd jaison-unified

# 2️⃣  Create isolated Python environment
python -m venv venv

# Activate environment:
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3️⃣  Install all dependencies
pip install -r requirements.txt

# 4️⃣  Validate installation (downloads models, checks dependencies)
python install.py

# 5️⃣  Configure the system
cp config.yaml.template config.yaml
# ✏️  Open config.yaml and customize for your needs

# 6️⃣  Launch the core server
python src/main.py
```

✅ **Server Running!** Visit `http://localhost:7272` to see the API status

---

## 💾 Installation

### 📋 Prerequisites

#### System Requirements

Your system should meet these minimum specs:

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **RAM** | 4 GB | 8+ GB |
| **Storage** | 3 GB free | 10+ GB free |
| **Python** | 3.12+ | 3.12+ |
| **GPU** | None (CPU works) | NVIDIA RTX or better |
| **CPU Cores** | 2+ | 4+ |

#### Platform-Specific Setup Instructions

<details open>
<summary><b>🪟 Windows Setup</b></summary>

**Step 1: Enable Developer Mode** (for symbolic links)
```powershell
# Open Settings:
# Settings → System → For developers → Developer Mode → Toggle ON
```

**Step 2: Install FFmpeg**
1. Download [`ffmpeg-git-essentials.7z`](https://www.gyan.dev/ffmpeg/builds/) (latest)
2. Extract the archive
3. Copy all files from `bin/` folder to your project root directory
4. Verify: Run `ffmpeg -version` in PowerShell

**Step 3: Install Python 3.12+**
- Download from [python.org](https://www.python.org/downloads/)
- ✅ Check: "Add Python to PATH" during installation
- Verify: `python --version`

**Step 4: GPU Support (Optional)**
For NVIDIA RTX cards:
- Install [NVIDIA CUDA Toolkit 12.8](https://developer.nvidia.com/cuda-toolkit)
- Install [NVIDIA cuDNN](https://developer.nvidia.com/cudnn)
- After JAIson setup, verify GPU detection: `python -c "import torch; print(torch.cuda.is_available())"`

**Troubleshooting:**
- If `python` command not found: Ensure Python is in PATH (restart terminal)
- If `ffmpeg` not found: Place `ffmpeg.exe` in project root or system PATH

</details>

<details>
<summary><b>🍎 macOS Setup</b></summary>

**Step 1: Install Homebrew** (if not installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Step 2: Install Python & FFmpeg**
```bash
brew install python@3.12 ffmpeg
```

**Step 3: Verify Installation**
```bash
python3.12 --version
ffmpeg -version
```

**Step 4: GPU Support (Apple Silicon)**
- PyTorch automatically uses Metal Performance Shaders
- No additional setup needed—enjoy GPU acceleration!

**Step 5: Optional - Rosetta 2** (Intel-based Macs)
```bash
# Enable Rosetta for broader compatibility
softwareupdate --install-rosetta
```

</details>

<details>
<summary><b>🐧 Linux Setup (Ubuntu/Debian)</b></summary>

**Step 1: Install System Dependencies**
```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-pip ffmpeg
```

**Step 2: Verify Installation**
```bash
python3.12 --version
ffmpeg -version
```

**Step 3: GPU Support (NVIDIA)**
```bash
# Install CUDA 12.8
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-toolkit-12-8

# Install cuDNN
# Download from NVIDIA website and follow their installation guide
```

**Step 4: Verify CUDA**
```bash
nvcc --version
```

</details>

### 🔧 Installation Methods

Choose the installation method that works best for you:

#### **Method 1️⃣: Pip Install (Recommended for Users)**
```bash
# Install the package in development mode (easy to update)
pip install -e .

# Or install directly without development features
pip install .
```

**Advantages:** Easiest to update, creates CLI commands, works everywhere

#### **Method 2️⃣: From Requirements File**
```bash
# Install all dependencies from requirements file
pip install -r requirements.txt

# Install core packages without dependencies
pip install --no-deps -r requirements.no_deps.txt
```

**Advantages:** More control, faster if you have dependencies cached

#### **Method 3️⃣: Traditional Python Setup**
```bash
# Classic setup.py installation
python setup.py install
```

**Advantages:** Familiar to many developers, integrates with system Python

### ✅ Post-Installation Validation

After installing, run these commands to download required models and validate the setup:

```bash
# 1. Download language models (required for text processing)
python -m spacy download en_core_web_sm

# 2. Run complete installation validation
# This downloads NLTK data, checks dependencies, validates configs
python install.py

# 3. Optional: Japanese language support (if using Japanese text)
python -m unidic download
```

**What gets validated:**
- ✅ All Python packages installed correctly
- ✅ PyTorch/TensorFlow loaded
- ✅ NLTK datasets downloaded
- ✅ Directory structure correct
- ✅ Configuration files present
- ✅ FFmpeg accessible

## 🎛️ Applications

All applications live in the `apps/` directory and can be managed independently. The core server must be running for applications to function.

### 💬 Discord Bot Integration

Enable your AI to chat naturally in Discord servers and participate in voice conversations.

**What it does:**
- Responds to messages in text channels (with mention or configured prefix)
- Joins voice channels and participates in conversations
- Maintains conversation context across multiple users
- Emotion-aware responses based on conversation sentiment

**Setup:**
```bash
# Navigate to Discord app
cd apps/discord

# Copy environment template
cp .env-template .env

# Edit .env file with your Discord bot token
# You need: DISCORD_TOKEN from Discord Developer Portal
nano .env  # or use your favorite editor

# Run the bot
python src/main.py
```

**Configuration:** Edit `apps/discord/config.yaml`
```yaml
jaison_endpoints:
  rest: "http://localhost:7272/api"
  websocket: "ws://localhost:7272/ws"

audio:
  opus_library_path: null  # Auto-detect or specify path
  
voice:
  idle_interval: 60  # Seconds before leaving voice channel
```

**Getting a Discord Bot Token:**
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create New Application
3. Go to "Bot" section → Add Bot
4. Copy the TOKEN under "TOKEN"
5. In "OAuth2" → "URL Generator": Select scopes: `bot`
6. Select permissions: `Send Messages`, `Connect`, `Speak`, `Use Voice Activity`
7. Copy generated URL and add bot to your server

---

### 📺 Twitch Integration

Monitor Twitch chat in real-time and respond with AI-generated messages based on your configuration.

**What it does:**
- Monitors chat and events from your Twitch channel
- Filters messages based on criteria (keywords, highlights, bits, etc.)
- Generates contextual responses to chat
- Tracks viewer interactions and sentiment

**Setup:**
```bash
# Navigate to Twitch app
cd apps/twitch

# First-time only: Authenticate with Twitch
python src/auth.py
# This opens a browser window for OAuth authentication

# Copy environment file (if needed)
cp .env-template .env

# Run the integration
python src/main.py
```

**Configuration:** Edit `apps/twitch/config.yaml`
```yaml
# Chat monitoring mode
chat_filter: "ALL"  # Options: ALL, KEYWORD, HIGHLIGHT, BITS, DISABLE

# Summary generation
summary_interval: 300  # Generate summary every 5 minutes

# Which events to monitor
events:
  follow: true
  subscribe: true
  host: true
  raid: true
```

**Filter Modes Explained:**
- `ALL` - Respond to every message (high rate)
- `KEYWORD` - Only respond to messages with specific keywords
- `HIGHLIGHT` - Only respond to chat highlights
- `BITS` - Only respond to messages with bits
- `DISABLE` - Don't respond (monitoring only)

---

### 🎭 VTube Studio Integration

Animate your VTuber character with synchronized emotion reactions and hotkey responses.

**What it does:**
- Reads hotkey configuration from JSON
- Triggers character animations based on emotions
- Syncs facial expressions with AI responses
- Real-time animation control via WebSocket

**Setup:**
```bash
# Navigate to VTS app
cd apps/vts

# Ensure VTube Studio is running on your system
# With: Settings → General Settings & External Connections → Plugins API enabled

# Run the integration
python src/main.py
```

**Configuration:** Edit `apps/vts/config.yaml`
```yaml
# VTube Studio WebSocket connection
vts_websocket_url: "ws://localhost:8001"

# Path to your hotkey configuration
hotkeys_config: "vts_hotkeys/example.json"

# JAIson WebSocket connection
jaison_websocket: "ws://localhost:7272/ws"
```

**Hotkey Configuration Example:**
```json
{
  "happy": ["expression_happy", "mouth_smile"],
  "sad": ["expression_sad", "tear_left"],
  "excited": ["jump", "expression_happy"],
  "confused": ["tilt_head", "expression_confused"]
}
```

**Getting Started with VTS API:**
1. Start VTube Studio
2. Enable Plugins API: VTS Settings → Advanced → Plugins
3. Allow plugin connections when prompted
4. Start the JAIson VTS integration

---

### 🎨 Web UI Dashboard

Professional, real-time dashboard for monitoring and controlling all services.

**What it does:**
- Live status monitoring of all connected services
- Real-time chat/event log streaming
- Service start/stop controls
- Configuration management UI
- Performance metrics and logs

**Launch:**
```bash
# Navigate to frontend
cd apps/frontend

# Install Node.js dependencies
npm install

# Start development server
npm run dev
```

**Access:** http://localhost:5173 (default Vite port)

**Features:**
- 📊 Real-time status dashboard
- 💬 Live chat viewer
- 🎛️ Service controls
- ⚙️ Configuration editor
- 📈 Performance graphs
- 🔍 Log viewer

---

## ⚙️ Configuration

### 🎯 Core Server Configuration

The heart of J.A.I.son is configured via `config.yaml`. This file controls all AI behavior.

**Example Configuration:**
```yaml
# ============================================================================
# PROJECT J.A.I.SON - CORE CONFIGURATION
# ============================================================================

# AI Model Configuration
model:
  type: "llama"  # AI model type
  name: "default"  # Model identifier
  
# Server Settings
server:
  host: "localhost"  # Bind address
  port: 7272  # API port
  debug: false  # Enable debug logging
  
# Voice/Audio Settings
audio:
  sample_rate: 16000  # 16kHz sampling (standard for voice)
  channels: 1  # Mono audio
  format: "pcm_s16le"  # PCM 16-bit signed little-endian

# AI Personality & Prompts
prompts:
  character: "prompts/characters/default.txt"  # Personality file
  scene: "prompts/scenes/default.txt"  # Context/scene
  instructions: "prompts/instructions/default.txt"  # System instructions

# Text-to-Speech (TTS) Engine
tts:
  engine: "tts_engine"  # Which TTS to use
  voice: "default"  # Voice profile
  speed: 1.0  # Speaking speed (0.5-2.0)

# Speech-to-Text (STT) Engine  
stt:
  engine: "whisper"  # Speech recognition model
  language: "en"  # Language code

# Model Context Protocol (MCP)
mcp:
  enabled: true
  tools: []  # List of external tools
```

**See `configs/example.yaml` for all 100+ configuration options.**

### 🔐 Environment Variables & Secrets

Never commit API keys to version control! Use `.env` file for sensitive data.

**Create `.env` file in project root:**
```bash
cp .env-template .env
nano .env  # Edit with your values
```

**Sample `.env` contents:**
```env
# OpenAI / Groq API Keys
OPENAI_API_KEY=sk-your-key-here
GROQ_API_KEY=gsk-your-key-here

# Discord
DISCORD_TOKEN=your-discord-bot-token

# Twitch
TWITCH_CLIENT_ID=your-client-id
TWITCH_CLIENT_SECRET=your-client-secret
TWITCH_REFRESH_TOKEN=your-refresh-token

# Other Services
CUSTOM_API_KEY=your-custom-api-key
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

**Security Tips:**
- ✅ Never commit `.env` to git (it's in `.gitignore`)
- ✅ Use different keys for dev/production
- ✅ Rotate keys regularly
- ✅ Use environment-specific config overrides

### 🚀 Free AI Integration with Groq

Save money by using Groq's free API with J.A.I.son:

```yaml
text_to_text:
  type: "openai"  # Use OpenAI format
  model: "mixtral-8x7b-32768"  # Groq model
  api_key: "${GROQ_API_KEY}"  # Load from .env
  base_url: "https://api.groq.com/openai/v1"  # Groq endpoint
  
# Get your free API key at: https://console.groq.com/
```

**Why Groq?**
- ✅ Free tier available
- ✅ Fast inference (competitive with paid services)
- ✅ No credit card required
- ✅ Works with existing OpenAI integrations

---

## 🎮 Usage

### ▶️ Starting the Core Server

The core server is the heart of J.A.I.son. It must be running for all other applications to function.

```bash
# Basic startup with default config
python src/main.py

# Start with specific configuration
python src/main.py --config=example

# Show help and all available options
python src/main.py --help
```

**What happens when you start:**
1. Loads configuration from `config.yaml`
2. Initializes AI models
3. Starts REST API server on port 7272
4. Opens WebSocket connection on port 7273
5. Waits for incoming requests from applications

**You'll see output like:**
```
✓ Configuration loaded: config.yaml
✓ Models initialized
✓ REST API listening on http://localhost:7272
✓ WebSocket listening on ws://localhost:7273
✓ Server ready - waiting for requests
```

### 🔄 Managing All Services Together

For a complete setup, start services in separate terminal windows:

```bash
# Terminal 1: Start the core server
python src/main.py

# Terminal 2: Start Discord bot
python manager.py discord

# Terminal 3: Start Twitch integration
python manager.py twitch

# Terminal 4: Start VTube Studio
python manager.py vts

# Terminal 5: Start Web UI
cd apps/frontend && npm run dev
```

**Alternatively, use the manager script:**
```bash
python manager.py core discord twitch vts  # Start all at once
```

### 🔌 API Endpoints

Once the server is running, access these APIs:

| Endpoint | Type | Purpose |
|----------|------|---------|
| `http://localhost:7272/api/` | REST | AI text/speech endpoints |
| `ws://localhost:7272/ws` | WebSocket | Real-time bidirectional communication |
| `http://localhost:7272/health` | REST | Health check endpoint |
| `http://localhost:7272/status` | REST | System status and metrics |

**Example API Request:**
```bash
# Send text to AI and get response
curl -X POST http://localhost:7272/api/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, how are you?"}'

# Response:
# {
#   "response": "I'm doing well, thanks for asking!",
#   "emotion": "happy",
#   "confidence": 0.95
# }
```

### 🛠️ CLI Tools

After installing with `pip install -e .`, these commands become available system-wide:

```bash
# Start JAIson server
jaison

# Start with specific config
jaison --config=my_config

# Start manager (all services)
jaison-manager core discord twitch

# Run installer/validation
jaison-install

# Check version
jaison --version
```

See [api.yaml](api.yaml) for complete REST API specifications.

---

## 👨‍💻 Development

### 📁 Understanding the Project Structure

```
jaison-unified/
│
├── 📂 src/                     # ⭐ Core JAIson server code
│   ├── main.py                # Entry point - starts the server
│   ├── utils/                 # Utility functions and helpers
│   │   ├── config.py          # Configuration loader
│   │   ├── logging.py         # Logging setup
│   │   ├── args.py            # Command-line argument parser
│   │   └── helpers/           # Helper modules (audio, etc.)
│   ├── operations/            # AI Operation modules
│   │   ├── stt/               # Speech-to-Text engine
│   │   ├── tts/               # Text-to-Speech engine
│   │   ├── t2t/               # Text-to-Text (LLM) engine
│   │   ├── embedding/         # Embedding generation
│   │   └── filter_audio/      # Audio processing (pitch, RVC)
│   ├── prompter/              # Prompt management and context
│   └── server/                # API and WebSocket server
│
├── 📂 apps/                    # Official integrations
│   ├── discord/               # Discord bot (27 files)
│   │   └── src/
│   │       ├── main.py        # Bot entry point
│   │       ├── bot.py         # Discord.py bot implementation
│   │       └── ...
│   ├── twitch/                # Twitch integration (16 files)
│   │   └── src/
│   │       ├── main.py        # Twitch integration entry point
│   │       ├── auth.py        # OAuth authentication
│   │       └── twitch_monitor.py  # Chat monitoring
│   ├── vts/                   # VTube Studio integration (23 files)
│   │   └── src/
│   │       ├── main.py        # VTS integration entry point
│   │       └── vts_plugin.py  # VTS API communication
│   └── frontend/              # Web UI Dashboard (SvelteKit) (73 files)
│       ├── src/
│       ├── package.json       # Node.js dependencies
│       ├── svelte.config.js   # Svelte configuration
│       └── vite.config.ts     # Vite build configuration
│
├── 📂 configs/                # Configuration templates
│   ├── example.yaml           # Full example with all options
│   └── ...
│
├── 📂 prompts/                # AI personality definitions
│   ├── characters/            # Character personality files
│   ├── scenes/                # Scene/context definitions
│   └── instructions/          # System instructions
│
├── 📂 models/                 # Pre-downloaded models directory
│   ├── rvc/                   # RVC voice models
│   ├── melotts/               # MeloTTS voice models
│   ├── kobold/                # Kobold models
│   └── mcp/                   # MCP tool models
│
├── 📂 docs/                   # Documentation files
│   ├── api.yaml               # REST API specification
│   ├── DEVELOPER.md           # Developer guide
│   └── CONTRIBUTING.md        # How to contribute
│
├── 📂 assets/                 # Images, logos, resources
│
├── 🐍 setup.py                # Python package installer
├── 🐍 install.py              # Post-installation validation script
├── 🐍 manager.py              # Service manager (start all apps)
├── 📄 requirements.txt         # All Python dependencies (177 packages)
├── 📄 requirements.no_deps.txt # Core packages without dependencies
├── 📄 config.yaml.template    # Configuration template
├── 📄 .env-template           # Environment variables template
├── 📄 .gitignore              # Git ignore rules
├── 📄 LICENSE                 # MIT License
└── 📄 README.md               # This file!
```

### 📚 Building Custom Applications

Want to extend J.A.I.son with your own integration? Read these docs:

| Document | Purpose |
|----------|---------|
| [DEVELOPER.md](DEVELOPER.md) | Complete development guide with examples |
| [api.yaml](api.yaml) | Full REST API specification |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute back to the project |

**Quick Example: Custom Application**
```python
import requests
import asyncio

async def ask_jaison(question: str):
    """Send a question to JAIson and get response"""
    response = requests.post(
        "http://localhost:7272/api/text",
        json={"text": question}
    )
    return response.json()["response"]

# Use it
answer = asyncio.run(ask_jaison("What's 2+2?"))
print(answer)  # Output: "The answer is 4"
```

### 🧪 Development Setup

Set up your environment for development:

```bash
# Install with development dependencies
pip install -r requirements.txt
pip install -e .[dev]  # Installs dev tools

# Format code (PEP 8 style)
black src/ apps/

# Check code quality
flake8 src/ apps/
pylint src/

# Run tests
pytest tests/

# Generate documentation
sphinx-build docs/ docs/_build/
```

**Development Tools Installed:**
- `black` - Code formatter
- `flake8` - Linter
- `pytest` - Testing framework
- `sphinx` - Documentation generator

---

## 🐛 Troubleshooting

Common issues and solutions:

### ⚠️ Port Already in Use

**Problem:** "Address already in use" when starting server

```bash
# Find what's using port 7272:
# Windows:
netstat -ano | findstr :7272

# macOS/Linux:
lsof -i :7272

# Kill the process (Windows):
taskkill /PID <PID> /F

# Kill the process (macOS/Linux):
kill -9 <PID>
```

**Permanent Fix:** Change port in `config.yaml`
```yaml
server:
  port: 7273  # Use different port
```

---

### 🔴 Discord Bot Won't Connect

**Checklist:**
- ✅ **Token Valid?** Copy token from [Discord Developer Portal](https://discord.com/developers/applications)
- ✅ **Bot Permissions?** Check bot has "Send Messages" and "Connect" permissions
- ✅ **Bot in Server?** Add bot with [OAuth URL Generator](https://discord.com/developers/applications) → OAuth2 → URL Generator
- ✅ **Firewall?** Discord needs outbound connections on port 443 (HTTPS)
- ✅ **Token Format?** Should start with `MTk4NjIyNDgzNzU3NTkwNDcyODc` (long string)

**Debug:**
```bash
# Check if Discord module loads
python -c "import discord; print(discord.__version__)"

# Enable debug logging
python -c "import logging; logging.basicConfig(level=logging.DEBUG)" src/main.py
```

---

### 🔴 Twitch Authentication Failed

**Problem:** "Invalid token" or "Authentication failed"

**Solution:**
```bash
# Re-authenticate (opens browser window)
cd apps/twitch
python src/auth.py

# This saves tokens to .env
# Verify they match what you see in Twitch Developer Console
nano .env
```

**Twitch Setup:**
1. Go to [Twitch Developer Console](https://dev.twitch.tv/console)
2. Create Application
3. Get Client ID and Client Secret
4. Set OAuth Redirect URL to: `http://localhost:3000/callback` (or whatever your app uses)

---

### 🔴 VTube Studio Not Responding

**Checklist:**
- ✅ **VTS Running?** Start VTube Studio application
- ✅ **Plugin API Enabled?** VTS Settings → Advanced → Plugins → Toggle ON
- ✅ **Correct WebSocket URL?** Usually `ws://localhost:8001` (check in VTS)
- ✅ **Firewall?** Allow localhost connections
- ✅ **Port 8001 Free?** Check: `netstat -ano | findstr :8001`

**Test Connection:**
```bash
# Try connecting to VTS WebSocket
python -c "
import websocket
try:
    ws = websocket.create_connection('ws://localhost:8001')
    print('✓ VTS WebSocket is accessible')
    ws.close()
except:
    print('✗ Cannot connect to VTS')
"
```

---

### 🔴 FFmpeg Not Found

**Problem:** "ffmpeg not found" or "FFmpeg is not installed"

**Windows:**
```bash
# Check if ffmpeg works
ffmpeg -version

# If not found, add to PATH:
# 1. Copy ffmpeg.exe to project root
# 2. Or add to system PATH (search: Environment Variables in Windows)
# 3. Restart terminal/IDE
```

**macOS:**
```bash
# Reinstall via Homebrew
brew reinstall ffmpeg

# Verify
which ffmpeg
ffmpeg -version
```

**Linux:**
```bash
# Reinstall
sudo apt remove ffmpeg
sudo apt install ffmpeg

# Verify
which ffmpeg
ffmpeg -version
```

---

### 🔴 CUDA/GPU Not Detected

**Problem:** "CUDA is not available" or model uses CPU instead of GPU

**Check if CUDA available:**
```bash
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')"
```

**If CUDA not detected:**

1. **Verify CUDA installed:**
   ```bash
   nvcc --version  # Should show CUDA version
   ```

2. **Reinstall PyTorch with CUDA:**
   ```bash
   pip uninstall torch torchvision torchaudio
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
   ```

3. **Check cuDNN installed:**
   - Download from [NVIDIA cuDNN](https://developer.nvidia.com/cudnn)
   - Follow installation guide for your OS

4. **Windows: libiomp5md.dll error**
   ```bash
   # Find and delete duplicate
   conda info  # Shows environment location
   # Find libiomp5md.dll in torch package and delete
   # Or reinstall environment
   ```

---

### 🔴 Model Download Fails

**Problem:** "Failed to download model" during `python install.py`

**Solution:**
```bash
# Retry download with more verbose output
python install.py --verbose

# Or manually download models:
python -m spacy download en_core_web_sm
python -m nltk.downloader punkt tokenize averaged_perceptron_tagger
```

**Large Files?** Some models are 500MB+. Ensure:
- ✅ Stable internet connection
- ✅ Enough disk space (10GB+ free)
- ✅ Not behind restrictive firewall

---

### 🔴 Permission Denied Errors

**Linux/macOS:**
```bash
# Make scripts executable
chmod +x src/main.py
chmod +x manager.py
chmod +x install.py

# Or run with python explicitly
python src/main.py
```

**Windows - Enable Developer Mode:**
- Settings → System → Developer settings → Developer Mode → Toggle ON
- Restart terminal
- Try again

---

### 📞 Still Having Issues?

If the above doesn't help:

1. **Check logs:**
   ```bash
   # Look for error messages in output
   python src/main.py 2>&1 | tee debug.log
   ```

2. **Enable debug mode:** Edit `config.yaml`
   ```yaml
   server:
     debug: true
   ```

3. **Ask for help:**
   - Discord: [Join community server](https://discord.gg/Z8yyEzHsYM)
   - GitHub Issues: Create a detailed issue report
   - Include: OS, Python version, error messages, config (without secrets!)

---

## 👥 Community

### 🤝 Connect With Us

Join thousands of developers and creators building with J.A.I.son:

- **💬 Discord Community:** [discord.gg/Z8yyEzHsYM](https://discord.gg/Z8yyEzHsYM)
  - Real-time support and Q&A
  - Share projects and ideas
  - Weekly community voice chats

- **📺 YouTube Channel:** [@LimitCantCode](https://www.youtube.com/@LimitCantCode)
  - Tutorial videos
  - Project showcases
  - Development insights

- **🎥 Twitch Channel:** [atmylimit_](https://www.twitch.tv/atmylimit_)
  - Live development streams
  - Q&A sessions
  - Community interactions

### 🤲 Contributing

We love contributions! Whether it's bug fixes, new features, documentation, or examples—all are welcome.

**How to contribute:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to your fork (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### ⭐ Contributors

This project is built by the community. A huge thank you to everyone who contributes:

<a href="https://github.com/limitcantcode/jaison-core/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=limitcantcode/jaison-core" alt="Contributors" />
</a>

**Special Thanks to:**
- **Original Creator:** [LimitCantCode](https://github.com/limitcantcode) - Core architecture and vision
- **Unified Distribution:** [tulovec96](https://github.com/tulovec96) - Merged distribution, modernization, and enhancement

---

## 📜 License

This project is licensed under the **[MIT License](LICENSE)** - you're free to use, modify, and distribute this software for personal or commercial use.

**Third-Party Licenses:**
- FFmpeg: [LGPLv2.1](https://ffmpeg.org/legal.html)
- PyTorch: [BSD License](https://github.com/pytorch/pytorch/blob/master/LICENSE)
- Discord.py: [MIT License](https://github.com/Rapptz/discord.py/blob/master/LICENSE)

See [LICENSE](LICENSE) for complete details.

---

## 📝 Citation

If you use Project J.A.I.son in your research or project, please cite:

```bibtex
@software{jaison2024,
  title = {Project J.A.I.son - Unified AI Companion Framework},
  author = {LimitCantCode and Contributors},
  year = {2024},
  url = {https://github.com/limitcantcode/jaison-core},
  license = {MIT}
}
```

---

## 🗺️ Roadmap

**Planned Features:**
- [ ] Web-based configuration editor
- [ ] Advanced emotion detection and responses
- [ ] Multi-language support (beyond English)
- [ ] GPU acceleration for faster inference
- [ ] Docker containers for easy deployment
- [ ] Kubernetes orchestration examples
- [ ] Mobile app companion
- [ ] Live streaming integration (YouTube, Facebook)
- [ ] Voice cloning capabilities
- [ ] Advanced analytics dashboard

**Want a feature?** Open an [issue](https://github.com/limitcantcode/jaison-core/issues/new) with your idea!

---

## 🙏 Acknowledgments

Built with ❤️ by the open-source community.

**Technologies Used:**
- 🐍 [Python 3.12+](https://www.python.org/)
- 🔥 [PyTorch](https://pytorch.org/) - AI/ML framework
- 🤖 [Transformers](https://huggingface.co/transformers/) - NLP models
- 💬 [Discord.py](https://discordpy.readthedocs.io/) - Discord integration
- 🎨 [Svelte](https://svelte.dev/) + [Tailwind CSS](https://tailwindcss.com/) - Web UI
- 🌐 [FastAPI](https://fastapi.tiangolo.com/) - API framework
- 🔊 [FFmpeg](https://ffmpeg.org/) - Audio/video processing

---

<p align="center">
  <strong>Made with ❤️ by the Project J.A.I.son community</strong>
</p>

<p align="center">
  <a href="https://github.com/limitcantcode/jaison-core">⭐ Star us on GitHub!</a> •
  <a href="https://discord.gg/Z8yyEzHsYM">💬 Join Discord</a> •
  <a href="#contributors">👥 Become a Contributor</a>
</p>
