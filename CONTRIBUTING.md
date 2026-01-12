# 🤝 Contributing to Voxelle

<p align="center">
  <img src="https://img.shields.io/badge/Contributions-Welcome-brightgreen?style=for-the-badge" alt="Contributions Welcome">
  <img src="https://img.shields.io/badge/PRs-Welcome-blue?style=for-the-badge" alt="PRs Welcome">
</p>

Thank you for your interest in contributing to **Voxelle**! This project thrives on community contributions, whether it's code, documentation, bug reports, or feature ideas.

> **Note:** Voxelle is based on [J.A.I.son](https://github.com/limitcantcode/jaison-core) by [@limitcantcode](https://github.com/limitcantcode) **(No Voxelle Support)**. Voxelle is maintained & enhanced by [@tulovec96](https://github.com/tulovec96).

---

## 📋 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [How to Contribute](#-how-to-contribute)
- [Development Setup](#-development-setup)
- [Project Structure](#-project-structure)
- [Commit Guidelines](#-commit-guidelines)
- [Pull Request Process](#-pull-request-process)
- [Reporting Issues](#-reporting-issues)
- [Questions & Support](#-questions--support)

---

## 📜 Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors:

- ✅ Be respectful and considerate
- ✅ Welcome different opinions and experiences
- ✅ Provide constructive feedback
- ✅ Help newcomers learn
- ❌ No harassment, discrimination, or hate speech
- ❌ No spam or self-promotion

---

## 💡 How to Contribute

### 🐛 Found a Bug?

1. **Check existing issues** first
2. **Create a detailed bug report** including:
   - What you were trying to do
   - What you expected vs what happened
   - Your environment (OS, Python 3.14.2, Node.js version)
   - Error messages or logs
   - Steps to reproduce

### 🎯 Have a Feature Idea?

1. **Discuss first** - Open an issue to discuss your idea
2. **Explain the use case** - Why is this feature needed?
3. **Propose an implementation** - How would you build it?

### 📚 Improve Documentation?

Documentation improvements are always welcome! You can:
- Fix typos in README or docs
- Add examples or tutorials
- Clarify confusing sections
- Update outdated information

No approval needed—just submit a PR!

### 🔧 Submit Code

Follow the guidelines below for the best chance of acceptance.

---

## 🛠️ Development Setup

### Prerequisites

- Python 3.14.2
- Node.js 18+
- Git

### 1. Fork & Clone

```bash
# Fork the repo on GitHub, then:
git clone https://github.com/YOUR_USERNAME/voxelle.git
cd voxelle
```

### 2. Install Dependencies

```bash
# Use the manager to install everything
python manager.py install

# Or manually:
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Linux/macOS

pip install -r requirements.txt

# Frontend
cd apps/frontend
npm install
```

### 3. Verify Setup

```bash
python manager.py status
python manager.py deps
```

---

## 📁 Project Structure

```
voxelle/
├── src/                    # Core AI server
├── apps/
│   ├── discord/            # Discord bot integration
│   ├── twitch/             # Twitch chat integration
│   ├── vts/                # VTube Studio integration
│   └── frontend/           # SvelteKit web dashboard
├── configs/                # Configuration templates
├── prompts/                # AI prompt templates
├── models/                 # AI models directory
├── scripts/                # Utility scripts
├── manager.py              # Project manager CLI
└── requirements.txt        # Python dependencies
```

### Key Files

| File | Purpose |
|------|---------|
| `manager.py` | Main CLI for running services and managing deps |
| `src/main.py` | Core server entry point |
| `apps/*/src/main.py` | App entry points |
| `config.yaml` | Main configuration |

---

## 📝 Commit Guidelines

### Commit Message Format

```
[TYPE] Brief description (50 chars or less)

Optional longer explanation:
- What changed
- Why it changed
```

### Commit Types

| Type | Description |
|------|-------------|
| `[feature]` | New feature |
| `[fix]` | Bug fix |
| `[refactor]` | Code restructuring |
| `[perf]` | Performance improvement |
| `[docs]` | Documentation changes |
| `[test]` | Test additions/changes |
| `[chore]` | Build, deps, config |
| `[ui]` | Frontend/UI changes |

### Examples

```
[feature] Add emotion distribution chart to VTS panel

[fix] Resolve WebSocket reconnection on network change

[docs] Update Discord bot setup instructions

[ui] Improve Twitch page responsive layout
```

---

## 🔄 Pull Request Process

### 1. Create a Feature Branch

```bash
git checkout -b feature/amazing-feature
```

### 2. Make Your Changes

- ✅ Write clear, well-commented code
- ✅ Follow existing code style
- ✅ Update documentation if needed
- ✅ Test your changes

### 3. Run Checks

```bash
# Python
python -m py_compile src/main.py

# Frontend
cd apps/frontend
npm run check
npm run build
```

### 4. Push & Create PR

```bash
git push origin feature/amazing-feature
```

**Include in PR Description:**
- What changed and why
- Screenshots for UI changes
- How to test

---

## 🐛 Reporting Issues

**Title Format:**
```
[BUG] Short description
```

**Include:**
- OS (Windows/macOS/Linux)
- Python version (should be 3.14.2)
- Node.js version (for frontend issues)
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

---

## 🎯 Feature Requests

**Title Format:**
```
[FEATURE] Short description
```

**Include:**
- Use case (why is this needed?)
- Proposed solution
- Which component (Core, Discord, Twitch, VTS, Frontend)

---

## 💬 Questions & Support

- **Discord**: [Join Community](https://discord.gg/Z8yyEzHsYM)
- **Issues**: Open a GitHub issue with `[QUESTION]` prefix

---

## 🎨 Code Style

### Python
- Follow PEP 8
- Use type hints
- Docstrings for functions

```python
def process_message(text: str, user_id: int) -> dict:
    """Process incoming message and return response data."""
    ...
```

### TypeScript/Svelte
- Use TypeScript for type safety
- Follow existing component patterns
- Use Tailwind utility classes

```svelte
<script lang="ts">
  export let title: string;
  export let active: boolean = false;
</script>
```

---

## 🚀 Review Process

PRs are reviewed as soon as possible. We check:

- ✅ Code quality and style
- ✅ Logic and implementation
- ✅ Documentation updates
- ✅ No breaking changes

---

## 🎉 All Contributions Welcome!

We appreciate all types of contributions:

| Type | Examples |
|------|----------|
| 🐛 Bug fixes | Fix crashes, errors, edge cases |
| ✨ Features | New functionality, integrations |
| 📚 Documentation | Guides, examples, translations |
| 🎨 UI/UX | Design improvements, accessibility |
| 🧪 Tests | Unit tests, integration tests |
| 💬 Community | Help others, answer questions |

---

<p align="center">
  <strong>Thank you for making Voxelle better! ❤️</strong>
</p>

<p align="center">
  <em>Based on <a href="https://github.com/limitcantcode/jaison-core">J.A.I.son</a> by limitcantcode, merged & enhanced by tulovec96</em>
</p>
