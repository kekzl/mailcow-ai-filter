# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-06

### Added
- 🎉 **Initial Release**
- AI-powered email analysis with Claude or Ollama
- Embedding-based ML clustering (HDBSCAN)
- Hierarchical two-tier analysis mode
- ManageSieve integration for existing filter detection
- Docker container orchestration script (`mailcow-filter.sh`)
- Interactive menu interface
- Automated folder creation via IMAP
- Filter upload via MailCow API
- Support for local LLMs (Ollama)
- Support for Claude API
- Comprehensive documentation

### Features
- **Analysis Modes:**
  - Embedding mode (ML clustering) - fastest for 1000+ emails
  - Hierarchical mode (two-tier AI) - best quality
  - Simple mode (legacy) - for small mailboxes

- **Deployment Options:**
  - Docker containers (recommended)
  - Python venv (development)
  - Docker Compose integration

- **AI Providers:**
  - Ollama (local, free)
  - Anthropic Claude (cloud, paid)

- **Utilities:**
  - Existing filter fetching (ManageSieve)
  - Folder creation (IMAP)
  - Filter upload (MailCow API)
  - Filter validation

### Performance
- Analyzes 1,500+ emails in ~90-120 seconds
- Generates 15-20 filter rules on average
- 92-95% categorization accuracy

### Documentation
- README.md - Main documentation
- QUICKSTART.md - 5-minute guide
- DOCKER_USAGE.md - Container guide
- EXISTING_FILTERS.md - Filter integration
- LOCAL_MODELS.md - Local LLM setup
- CLAUDE.md - Claude API guide
- ARCHITECTURE.md - Technical details

### Security
- Read-only IMAP access
- Credentials stored in gitignored config files
- Optional fully offline operation
- No email content sent to cloud (with local LLMs)

---

## [Unreleased]

### Planned Features
- Web UI for configuration
- OpenAI provider support
- Gemini provider support
- Multi-language email support
- Filter simulation/testing
- Email preview
- Scheduled analysis
- Statistics dashboard

---

## Version History

- **1.0.0** (2025-01-06) - Initial public release
  - Docker orchestration
  - ManageSieve integration
  - ML clustering
  - Complete documentation

---

## Migration Guide

### From Manual Setup to Docker

If you were using Python venv before:

```bash
# Old way
source venv/bin/activate
python -m src.main

# New way (recommended)
./mailcow-filter.sh analyze
```

All config files remain compatible!

---

## Breaking Changes

None in this release (first public version).

---

## Contributors

Thanks to all contributors who helped make this release possible!

- kekzl - Initial work and project maintainer
- Community contributors welcome!

---

For detailed commit history, see [GitHub Commits](https://github.com/kekzl/mailcow-ai-filter/commits/master)
