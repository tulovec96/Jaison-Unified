#  Voxelle - AI VTuber Platform

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.14.2-3776ab?logo=python&style=flat" alt="Python">
  <img src="https://img.shields.io/badge/SvelteKit-FF3E00?logo=svelte&style=flat" alt="SvelteKit">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat" alt="License">
  <a href="https://discord.gg/Z8yyEzHsYM"><img src="https://img.shields.io/badge/Discord-Community-5865F2?logo=discord&style=flat" alt="Discord"></a>
</p>

<p align="center">
  <strong>A unified AI VTuber framework with Discord, Twitch, VTube Studio integrations and a modern web dashboard</strong>
</p>

---

##  About

**Voxelle** is a production-ready AI VTuber platform that unifies voice processing, chat integrations, streaming tools, and a modern web dashboard into a single framework.

Originally based on [J.A.I.son](https://github.com/limitcantcode/jaison-core) by [@limitcantcode](https://github.com/limitcantcode), extensively merged and enhanced by [@tulovec96](https://github.com/tulovec96).

### Key Features

| Category | Features |
|----------|----------|
| ** Core AI** | Voice pipeline (STT  Processing  TTS), context memory, MCP protocol, low-latency, local execution |
| ** Discord** | Voice & text chat, slash commands, analytics, moderation |
| ** Twitch** | Chat monitoring, events, sentiment analysis, moderation |
| ** VTube Studio** | Emotion reactions, hotkeys, expressions, idle animations |
| ** Dashboard** | Real-time stats, live charts, config editor, API playground |

---

##  Quick Start

### Prerequisites

| Requirement | Version |
|-------------|---------|
| **Python** | 3.14.2 |
| **FFmpeg** | Latest |
| **Node.js** | 18+ (for frontend) |

### Installation

```bash
# 1. Clone and navigate
git clone https://github.com/tulovec96/Project-Voxelle.git
cd Project-Voxelle

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Linux/macOS

# 3. Install dependencies
python manager.py install

# 4. Configure
cp config.yaml.template config.yaml
# Edit config.yaml with your settings

# 5. Launch
python manager.py core
```

Server runs at `http://localhost:7272`

---

##  Applications

All apps in `apps/` require core server running on `localhost:7272`.

| App | Command | Dashboard |
|-----|---------|-----------|
| **Core** | `python manager.py core` | `http://localhost:7272` |
| **Discord** | `python manager.py discord` | `http://localhost:5173/discord` |
| **Twitch** | `python manager.py twitch` | `http://localhost:5173/twitch` |
| **VTube Studio** | `python manager.py vts` | `http://localhost:5173/vtube` |
| **Frontend** | `cd apps/frontend && npm run dev` | `http://localhost:5173` |

See individual app READMEs for detailed setup:
- [Discord README](apps/discord/README.md)
- [Twitch README](apps/twitch/README.md)
- [VTube Studio README](apps/vts/README.md)
- [Frontend README](apps/frontend/README.md)

---

##  Configuration

### Core Configuration (`config.yaml`)

```yaml
# Server
server:
  host: "localhost"
  port: 7272

# AI Model
model:
  type: "llama"
  name: "default"

# Prompts
prompts:
  character: "prompts/characters/default.txt"
  scene: "prompts/scenes/default.txt"
  instructions: "prompts/instructions/default.txt"

# TTS/STT
tts:
  engine: "tts_engine"
  voice: "default"
stt:
  engine: "whisper"
  language: "en"
```

### Environment Variables (`.env`)

```env
OPENAI_API_KEY=sk-your-key
GROQ_API_KEY=gsk-your-key
DISCORD_TOKEN=your-token
TWITCH_CLIENT_ID=your-id
TWITCH_CLIENT_SECRET=your-secret
```

---

##  Project Structure

```
Project-Voxelle/
 src/                    # Core server
    main.py
    operations/         # STT, TTS, T2T, embedding
    prompter/           # Prompt management
    server/             # API & WebSocket
 apps/
    discord/            # Discord bot
    twitch/             # Twitch integration
    vts/                # VTube Studio
    frontend/           # Web dashboard (SvelteKit)
 configs/                # Config templates
 prompts/                # AI personality files
 models/                 # Downloaded models
 manager.py              # Service manager
 config.yaml.template    # Config template
```

---

##  API

| Endpoint | Type | Purpose |
|----------|------|---------|
| `http://localhost:7272/api/` | REST | AI text/speech endpoints |
| `ws://localhost:7272/ws` | WebSocket | Real-time communication |
| `http://localhost:7272/health` | REST | Health check |

**Example:**
```bash
curl -X POST http://localhost:7272/api/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello!"}'
```

See [api.yaml](api.yaml) for full specification.

---

##  Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 7272 in use | Change port in `config.yaml` or kill existing process |
| Discord won't connect | Verify token in `.env`, check bot permissions |
| Twitch auth fails | Re-run `python apps/twitch/src/auth.py` |
| VTS not responding | Enable Plugin API in VTube Studio settings |
| FFmpeg not found | Install FFmpeg and add to PATH |
| CUDA not detected | Reinstall PyTorch with CUDA: `pip install torch --index-url https://download.pytorch.org/whl/cu128` |

---

##  Documentation

| Document | Purpose |
|----------|---------|
| [QUICKSTART.md](QUICKSTART.md) | 5-minute setup guide |
| [DEVELOPER.md](DEVELOPER.md) | Technical deep-dive |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute |
| [api.yaml](api.yaml) | REST API specification |

---

##  Community
## 🆘 Community & Support

- **Discord:** [discord.gg/Z8yyEzHsYM](https://discord.gg/Z8yyEzHsYM)
- **Developer:** [GitHub @tulovec96](https://github.com/tulovec96) - Voxelle Official
- **Original Project:** [J.A.I.son](https://github.com/limitcantcode/jaison-core) by [@limitcantcode](https://github.com/limitcantcode) **(No Voxelle Support)**
---

##  License

MIT License - See [LICENSE](LICENSE) for details.

Uses FFmpeg under LGPLv2.1.

---

<p align="center">Made with  by the Voxelle community</p>
