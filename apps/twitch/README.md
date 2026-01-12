#  Voxelle Twitch Integration

<p align="center">
  <img src="https://img.shields.io/badge/Twitch-Integration-9146FF?style=for-the-badge&logo=twitch" alt="Twitch">
  <img src="https://img.shields.io/badge/Python-3.14.2-3776ab?style=for-the-badge&logo=python" alt="Python">
</p>

Twitch stream integration for [Voxelle](../..). Monitor chat, track events, and analyze stream metrics with sentiment analysis and moderation.

---

##  Features

| Feature | Description |
|---------|-------------|
| ** Chat Monitoring** | Real-time chat analysis with AI responses |
| ** Event Tracking** | Follows, subs, raids, cheers, hype trains |
| ** Sentiment Analysis** | Positive/neutral/negative classification |
| ** Moderation** | Filters, user tiers, spam detection |
| ** Analytics** | Top contributors, event stats, session tracking |

---

##  Installation

### Prerequisites

- Python 3.14.2
- Voxelle Core running on `localhost:7272`
- Twitch Developer Application

### Setup

```bash
cd apps/twitch
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env-template .env
```

### Twitch App Setup

1. Go to [Twitch Developer Console](https://dev.twitch.tv/console)
2. Register Application
3. Set OAuth Redirect URLs:
   - `http://localhost:5000/auth/redirect/code`
   - `http://localhost:5000/auth/redirect/tokens`
4. Copy **Client ID** and **Client Secret**

### Configuration

Edit `.env`:
```bash
TWITCH_APP_ID=<your-client-id>
TWITCH_APP_TOKEN=<your-client-secret>
```

Edit `config.yaml`:
```yaml
twitch-target-id: "<channel-id>"
twitch-bot-id: "<bot-user-id>"
jaison-api-endpoint: "http://127.0.0.1:7272"
chat-mode: "KEYWORD"  # ALL, KEYWORD, HIGHLIGHT, BITS, DISABLE
chat-keywords: "hello,hey,question"
```

### Authentication

```bash
python ./src/auth.py
```

---

##  Usage

```bash
python ./src/main.py
```

### Chat Modes

| Mode | Description |
|------|-------------|
| **ALL** | Respond to every message |
| **KEYWORD** | Only messages with keywords |
| **HIGHLIGHT** | Only highlighted messages |
| **BITS** | Only messages with bits |
| **DISABLE** | No responses |

### Tracked Events

Follows, Subscriptions, Raids, Cheers, Hype Trains, Channel Points, Charity

---

##  Project Structure

```
apps/twitch/
 src/
    main.py
    auth.py
    utils/
 tokens/
 config.yaml
 requirements.txt
```

---

##  Troubleshooting

| Issue | Solution |
|-------|----------|
| Auth fails | Re-run `auth.py`, check client ID/secret |
| No events | Verify channel ID |
| Token expired | Delete `tokens/` and re-authenticate |

---

##  License

MIT License - See [LICENSE](../../LICENSE)

<p align="center">Part of <a href="../..">Voxelle</a></p>
