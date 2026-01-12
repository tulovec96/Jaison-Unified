# Changelog

All notable changes to Voxelle are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - Unified Edition - 2026-01-11

### 🎉 Major Release - Full Unification

This release brings together all JAIson projects into a single, cohesive framework.

### ✨ Added

**Core System**
- ✅ Unified distribution with all official integrations
- ✅ Modern CLI with `jaison` command line tools
- ✅ Professional setup.py with PyPI packaging
- ✅ Comprehensive installation validation script
- ✅ Service manager for coordinated startup

**Documentation**
- ✅ Complete README.md (1200+ lines, 4400+ words)
- ✅ Enhanced CONTRIBUTING.md with detailed guidelines
- ✅ Improved .gitignore with JAIson-specific patterns
- ✅ CHANGELOG.md for version tracking
- ✅ Quick Start guide
- ✅ Integration guide with architecture details

**Developer Experience**
- ✅ Better error messages and logging
- ✅ Type hints throughout codebase
- ✅ Pre-commit hooks support
- ✅ Automated code formatting (black, isort)
- ✅ Testing framework setup (pytest)

**Features**
- ✅ Groq API free integration guide
- ✅ Multi-platform setup support (Windows/macOS/Linux)
- ✅ GPU acceleration with CUDA detection
- ✅ Web UI dashboard (SvelteKit)
- ✅ Real-time monitoring and control

### 🔧 Changed

- 🔄 Modernized all dependencies (Python 3.12+)
- 🔄 Streamlined installation process
- 🔄 Improved project structure with apps/ directory
- 🔄 Enhanced API documentation
- 🔄 Better error handling and validation

### 🐛 Fixed

- ✅ FFmpeg path detection on Windows
- ✅ Virtual environment compatibility
- ✅ NLTK data download reliability
- ✅ Spacy model installation
- ✅ Configuration file validation

### 📦 Dependencies

**Core** (177 packages)
- torch >= 2.5.0
- transformers >= 4.50.0
- fastapi >= 0.115.0
- discord.py (from git)
- websockets >= 15.0
- pydantic >= 2.11.0

**Optional**
- [dev] pytest, black, flake8, mypy
- [docs] sphinx, sphinx-rtd-theme
- [audio] openai, gradio

---

## [1.5.0] - Individual Apps - 2025-12-01

### Added (Discord App)
- Voice channel support
- Context-aware responses
- Emotion-based reactions

### Added (Twitch App)
- Real-time chat monitoring
- Chat filtering (keyword, highlight, bits)
- Event-driven responses

### Added (VTube Studio App)
- Hotkey-based animations
- Emotion synchronization
- WebSocket integration

---

## [1.0.0] - Initial Release - 2025-06-15

### Added
- Core JAIson server
- REST API
- WebSocket support
- Basic prompt management
- Configuration system

---

## Roadmap

### Planned for 2.1.0
- [ ] Web-based configuration UI
- [ ] Advanced emotion detection
- [ ] Multi-language support
- [ ] Docker containers
- [ ] YouTube/Facebook streaming

### Planned for 2.2.0
- [ ] Mobile companion app
- [ ] Voice cloning capabilities
- [ ] Advanced analytics
- [ ] Kubernetes support
- [ ] Database persistence

### Planned for 3.0.0
- [ ] Breaking: New API structure
- [ ] Performance optimizations
- [ ] Extended MCP support
- [ ] Cloud deployment options
- [ ] Enterprise features

---

## Migration Guides

### From 1.5.0 → 2.0.0

**Configuration Changes:**
```yaml
# Old (1.5.0)
server:
  port: 7272

# New (2.0.0) - Same, but with more options
server:
  host: "localhost"
  port: 7272
  debug: false
```

**Installation:**
```bash
# Old
python install.py

# New (same, but better)
pip install -e .
python install.py
```

**Running Services:**
```bash
# Old
python apps/discord/src/main.py

# New (use manager)
python manager.py discord
```

---

## Version Support

| Version | Status | EOL |
|---------|--------|-----|
| 2.0.x | ✅ Current | Jan 2027 |
| 1.5.x | ⚠️ Legacy | Jul 2026 |
| 1.0.x | ❌ Unsupported | Jan 2026 |

---

## Getting Help

- **Bug Reports**: [GitHub Issues](https://github.com/limitcantcode/jaison-core/issues)
- **Questions**: [Discord Server](https://discord.gg/Z8yyEzHsYM)
- **Discussions**: [GitHub Discussions](https://github.com/limitcantcode/jaison-core/discussions)

---

## Contributors

Special thanks to all contributors making JAIson better:

- **LimitCantCode** - Original creator and core developer
- **tulovec96** - Unified distribution and modernization
- **Community Contributors** - Bug reports, features, documentation

---

## License

Project Voxelle is licensed under the [MIT License](LICENSE).

**Credits:**
- **LimitCantCode** - Original J.A.I.son project
- **tulovec96** - Voxelle Unified Distribution and Modernization

---

<p align="center">
  <strong>Updated: January 11, 2026</strong>
</p>
