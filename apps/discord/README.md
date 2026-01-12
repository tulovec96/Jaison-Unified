#  Voxelle Discord Integration

<p align="center">
  <img src="https://img.shields.io/badge/Discord-Integration-5865F2?style=for-the-badge&logo=discord" alt="Discord">
  <img src="https://img.shields.io/badge/Python-3.14.2-3776ab?style=for-the-badge&logo=python" alt="Python">
</p>

Discord bot integration for [Voxelle](../..). Enables AI conversations in text and voice channels with analytics and moderation.

---

##  Features

| Feature | Description |
|---------|-------------|
| ** Text Chat** | AI responds naturally with context awareness |
| ** Voice Chat** | Join voice channels and participate in conversations |
| ** Slash Commands** | 15+ built-in commands for control |
| ** Analytics** | Track message stats, voice sessions, member activity |
| ** Moderation** | Response filters, user blocklists, tone control |
| ** Context Memory** | Maintains conversation history |

---

##  Installation

### Prerequisites

- Python 3.14.2
- Voxelle Core running on `localhost:7272`
- Discord Bot Token

### Setup

```bash
cd apps/discord
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env-template .env
# Edit .env with DISCORD_BOT_TOKEN
```

### Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create Application  Bot  Copy TOKEN
3. Enable **Message Content Intent** under Privileged Intents
4. OAuth2  URL Generator:
   - Scopes: `bot`, `applications.commands`
   - Permissions: `Send Messages`, `Connect`, `Speak`, `Use Voice Activity`, `View Channels`, `Read Message History`
5. Add bot to your server

### Configuration

Edit `config.yaml`:
```yaml
jaison_api_endpoint: "http://127.0.0.1:7272"
jaison_ws_endpoint: "ws://127.0.0.1:7272"
opus_filepath: null
```

---

##  Usage

```bash
python ./src/main.py
```

### Commands

| Category | Commands |
|----------|----------|
| **Voice** | `/join_vc`, `/leave_vc` |
| **Management** | `/clear_history`, `/get_current_config`, `/config_load`, `/config_save` |
| **Analytics** | `/get_message_stats`, `/get_voice_stats`, `/get_member_activity`, `/export_analytics` |
| **Moderation** | `/set_activity_filter`, `/set_response_tone`, `/add_blocked_user`, `/remove_blocked_user` |
| **Context** | `/context_request_add`, `/context_conversation_add`, `/context_custom_register` |

### Text Interaction

- **Mention the bot**: `@Voxelle hello!`
- **Reply to messages**: Reply to continue conversation

---

##  Project Structure

```
apps/discord/
 src/
    main.py
    audio/          # Voice processing
    commands/       # Slash commands
 config.yaml
 requirements.txt
```

---

##  Troubleshooting

| Issue | Solution |
|-------|----------|
| Bot not responding | Check if Core is running on port 7272 |
| Voice not working | Ensure opus is installed, check audio permissions |
| Commands not showing | Re-invite bot with `applications.commands` scope |

---

##  License

MIT License - See [LICENSE](../../LICENSE)

<p align="center">Part of <a href="../..">Voxelle</a></p>
