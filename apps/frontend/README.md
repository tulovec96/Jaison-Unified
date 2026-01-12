#  Voxelle Frontend - Web Dashboard

<p align="center">
  <img src="https://img.shields.io/badge/SvelteKit-FF3E00?style=for-the-badge&logo=svelte" alt="SvelteKit">
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript" alt="TypeScript">
  <img src="https://img.shields.io/badge/Tailwind-06B6D4?style=for-the-badge&logo=tailwindcss" alt="Tailwind">
</p>

Modern web dashboard for [Voxelle](../..). Monitor services, view live stats, configure settings, and control all integrations.

---

##  Features

| Page | Features |
|------|----------|
| ** Dashboard** | Service status, system metrics, integration cards |
| ** Metrics** | CPU, memory, latency with rolling charts |
| ** Logs** | Real-time logs with filtering, search, export |
| ** Config** | YAML configuration editor |
| ** Twitch** | Live viewer charts, chat feed, event tracking |
| ** VTube Studio** | Emotion triggers, hotkey control, queue management |
| ** Discord** | Server stats, voice sessions, moderation |
| ** API** | Interactive REST API testing |

---

##  Getting Started

### Prerequisites

- Node.js 18+
- Voxelle Core running on `localhost:7272`

### Installation

```bash
cd apps/frontend
npm install
```

### Development

```bash
npm run dev
```

Visit **http://localhost:5173**

### Production

```bash
npm run build
npm run preview
```

---

##  Backend Integration

| Protocol | URL | Purpose |
|----------|-----|---------|
| **REST** | `http://localhost:7272/api/*` | Configuration, commands |
| **WebSocket** | `ws://localhost:8080` | Real-time updates |

### Environment

Create `.env.local`:
```env
VITE_API_URL=http://localhost:7272
VITE_WS_URL=ws://localhost:8080
```

---

##  Project Structure

```
apps/frontend/
 src/
    routes/           # SvelteKit pages
       +layout.svelte
       +page.svelte  # Dashboard
       socketio.ts   # Socket.IO client
       metrics/
       logs/
       config/
       twitch/
       vtube/
       discord/
    lib/
       components/ui/
    app.pcss
 package.json
 svelte.config.js
 tailwind.config.js
```

---

##  Tech Stack

| Tool | Purpose |
|------|---------|
| **Svelte 4** | UI framework |
| **SvelteKit 2** | Full-stack framework |
| **TypeScript** | Type safety |
| **Tailwind CSS** | Styling |
| **Socket.IO** | Real-time updates |
| **Lucide Svelte** | Icons |

---

##  Troubleshooting

| Issue | Solution |
|-------|----------|
| WebSocket won't connect | Verify Core is running on 7272/8080 |
| Metrics not updating | Check browser console |
| Styles not loading | Run `npm run build` |

---

##  License

MIT License - See [LICENSE](../../LICENSE)

<p align="center">Part of <a href="../..">Voxelle</a></p>
