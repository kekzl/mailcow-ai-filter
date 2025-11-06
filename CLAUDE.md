# Project Instructions for Claude Code

This file contains instructions for Claude Code (AI assistant) when working with this project.

## Project Overview

**MailCow AI Filter** - AI-powered email sorting for MailCow that automatically generates Sieve filters.

**Architecture:** Hexagonal (ports & adapters)
**Language:** Python 3.11+
**Deployment:** Docker containers

## Key Principles

### 1. Architecture Rules
- **Hexagonal architecture** - Domain layer has NO external dependencies
- Infrastructure adapters in `src/infrastructure/adapters/`
- Use cases in `src/application/use_cases/`
- Domain logic in `src/domain/`

### 2. Code Style
- **Type hints** - Required for all functions
- **Docstrings** - Google-style for all public functions
- **Frozen dataclasses** - For DTOs and value objects
- **No emojis** - Unless user explicitly requests them

### 3. Dependencies
- AI: Anthropic Claude API OR Ollama (local LLMs)
- ML: sentence-transformers, HDBSCAN clustering
- Email: IMAP, ManageSieve, MailCow API
- Config: YAML via `config/config.yml`

## Important Files

### User-Facing Scripts
- `mailcow-filter.sh` - Main orchestration script (bash)
- `apply_filters_retroactive.py` - Retroactive filter application
- `create_folders.py` - IMAP folder creation
- `fetch_existing_filters.py` - ManageSieve filter fetcher
- `upload_filter_api.py` - MailCow API uploader

### Core Application
- `src/main.py` - Entry point
- `src/application/use_cases/analyze_emails_use_case.py` - Main analysis logic
- `src/domain/services/filter_generator.py` - Sieve filter generation
- `src/infrastructure/adapters/ollama_adapter.py` - Ollama integration
- `src/infrastructure/adapters/anthropic_adapter.py` - Claude API integration

### Configuration
- `config/config.yml` - User configuration (gitignored)
- `config/config.example.yml` - Example configuration
- `requirements.txt` - Python dependencies

## Common Tasks

### Adding a New AI Provider

1. Create adapter in `src/infrastructure/adapters/`
2. Implement the AI analyzer interface
3. Add to provider factory
4. Update `config/config.example.yml`
5. Document in appropriate guide

### Adding New Filter Conditions

1. Update `src/domain/value_objects/filter_condition.py`
2. Update `src/domain/services/filter_generator.py`
3. Ensure Sieve syntax compatibility
4. Add validation in `src/domain/services/filter_validator.py`

### Modifying Analysis Logic

1. Edit `src/application/use_cases/analyze_emails_use_case.py`
2. Maintain hexagonal architecture boundaries
3. Keep domain logic pure (no external dependencies)
4. Test with both Claude and Ollama providers

## Testing

- Use `test_improvements.py` for filter generation tests
- Always test with actual email samples
- Verify Sieve filter syntax validity
- Check both analysis modes (embedding and hierarchical)

## Documentation Files

- `README.md` - Main project documentation
- `ANTHROPIC.md` - Claude API setup guide (NOT CLAUDE.md!)
- `LOCAL_MODELS.md` - Ollama/local LLM guide
- `DOCKER_USAGE.md` - Container orchestration
- `EXISTING_FILTERS.md` - ManageSieve integration
- `ARCHITECTURE.md` - Technical architecture details

## User Workflow

Typical user flow to remember:
```bash
1. ./mailcow-filter.sh analyze          # Generate filter rules
2. ./mailcow-filter.sh view-filter      # Review generated filter
3. ./mailcow-filter.sh create-folders   # Create IMAP folders
4. ./mailcow-filter.sh upload-filter    # Upload to server
5. ./mailcow-filter.sh apply-retroactive # Apply to existing emails
```

## Key Concepts

### Sieve Filters
- Standard: RFC 5228
- Generated in `output/generated.sieve`
- Only apply to NEW incoming emails by default
- Retroactive application via IMAP client-side

### Analysis Modes
- **Embedding** - ML clustering with HDBSCAN (default, fastest)
- **Hierarchical** - Two-tier AI analysis (higher quality)
- **Simple** - Single AI call (for small mailboxes)

### ManageSieve Integration
- Port 4190
- Fetches existing Sieve filters
- AI learns from existing organization
- Avoids creating duplicates

## Development Notes

### Container Development
- Everything runs in Docker containers
- No local Python venv needed for users
- `mailcow-filter.sh` orchestrates all operations

### Configuration
- Supports both Anthropic Claude and Ollama
- Switching: Just change `provider: "ollama"` or `provider: "anthropic"`
- Environment variables supported via `.env`

### Privacy
- With Ollama: 100% offline, zero cost
- With Claude: Data sent to Anthropic, ~$0.12 per run
- Users should be informed of the trade-off

## When Making Changes

1. **Maintain hexagonal architecture** - No external dependencies in domain layer
2. **Update documentation** - Keep README and guides in sync
3. **Test both providers** - Ollama AND Claude
4. **Respect user data** - Privacy-first design
5. **No emojis** - Unless explicitly requested
6. **Type hints required** - For all new functions

## Important Reminders

- CLAUDE.md (this file) = Instructions for Claude Code (AI assistant)
- ANTHROPIC.md = Documentation about Anthropic's Claude API for users
- Keep these separate!

## Git Workflow

- Meaningful commit messages with context
- Include "🤖 Generated with Claude Code" footer
- Test before committing
- Document breaking changes in CHANGELOG.md
