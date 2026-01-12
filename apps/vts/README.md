#  Voxelle VTube Studio Integration

<p align="center">
  <img src="https://img.shields.io/badge/VTube_Studio-Integration-FF6B9D?style=for-the-badge" alt="VTube Studio">
  <img src="https://img.shields.io/badge/Python-3.14.2-3776ab?style=for-the-badge&logo=python" alt="Python">
</p>

VTube Studio animation integration for [Voxelle](../..). Synchronize your VTuber model with AI-detected emotions, hotkeys, and idle animations.

---

##  Features

| Feature | Description |
|---------|-------------|
| ** Emotion Reactions** | Trigger expressions based on AI emotion detection |
| ** Hotkey Control** | Map emotions to VTube Studio hotkeys |
| ** Idle Animations** | Loop idle animations when not speaking |
| ** Lip Sync** | Audio-reactive mouth movement |
| ** Expression History** | Track emotion changes over time |

---

##  Installation

### Prerequisites

- Python 3.14.2
- Voxelle Core running on `localhost:7272`
- [VTube Studio](https://denchisoft.com/) with API enabled

### Setup

```bash
cd apps/vts
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp vts_hotkeys/example.json vts_hotkeys/my_model.json
```

### Configuration

Edit `config.yaml`:
```yaml
jaison-api-endpoint: "http://127.0.0.1:7272"
jaison-ws-endpoint: "ws://127.0.0.1:7272"
vts-api-endpoint: "ws://0.0.0.0:8001"
vts-hotkeys-config: "./vts_hotkeys/my_model.json"
```

---

##  VTube Studio Setup

1. **Enable API**: Settings  General Settings  Start API (Allow Plugins)
2. **Enable Microphone**: Settings  Enable lipsync
3. **Audio Routing**: Use [Voicemeeter](https://vb-audio.com/Voicemeeter/) to route AI audio to VTS
4. **Allow Plugin**: Accept Voxelle plugin when prompted

---

##  Hotkey Configuration

Create hotkey mappings in `vts_hotkeys/`:

```json
{
  "idle": {
    "emotions": [],
    "hotkeys": ["idle1", "idle2"]
  },
  "happy": {
    "emotions": ["joy", "amusement", "excitement", "love"],
    "hotkeys": ["happy1", "smile"]
  },
  "sad": {
    "emotions": ["sadness", "disappointment"],
    "hotkeys": ["sad1", "cry"]
  },
  "angry": {
    "emotions": ["anger", "annoyance"],
    "hotkeys": ["angry1"]
  }
}
```

### Emotion Reference

See `vts_hotkeys/list_of_emotions.txt` for all detectable emotions.

---

##  Usage

```bash
python ./src/main.py
```

### How It Works

1. Idle: Loops through idle animations
2. Speaking: AI generates text with detected emotion
3. Trigger: Maps emotion to hotkey, triggers animation
4. Return: After speaking, returns to idle

---

##  Project Structure

```
apps/vts/
 src/
    main.py
    utils/
 vts_hotkeys/
    example.json
    list_of_emotions.txt
 tokens/
 config.yaml
 requirements.txt
```

---

##  Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Ensure VTS is running with API enabled |
| Lip sync not working | Check audio routing through Voicemeeter |
| Hotkeys not triggering | Verify hotkey names match exactly |
| WSL issues | Use Windows IP instead of 0.0.0.0 |

---

##  License

MIT License - See [LICENSE](../../LICENSE)

<p align="center">Part of <a href="../..">Voxelle</a></p>
