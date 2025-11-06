# Contributing to MailCow AI Filter

Thank you for considering contributing! 🎉

## How to Contribute

### Reporting Bugs 🐛

1. Check if the bug is already reported in [Issues](https://github.com/kekzl/mailcow-ai-filter/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Logs (`logs/ai-filter.log`)
   - Your environment (OS, Docker version, etc.)

### Suggesting Features 💡

Open an issue with:
- Feature description
- Use case / motivation
- How it should work
- Any implementation ideas

### Pull Requests 🔧

1. **Fork** the repository
2. **Create a branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Test** thoroughly
5. **Commit**: Use clear commit messages
6. **Push**: `git push origin feature/your-feature-name`
7. **Create Pull Request**

## Development Setup

### Local Development (with venv)

```bash
# Clone repository
git clone https://github.com/kekzl/mailcow-ai-filter.git
cd mailcow-ai-filter

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Run analysis
python -m src.main
```

### Container Development

```bash
# Build container
./mailcow-filter.sh build

# Run container
./mailcow-filter.sh analyze

# Debug container
docker run --rm -it \
  -v ./config:/app/config:ro \
  -v ./output:/app/output \
  --network host \
  mailcow-ai-filter:latest \
  /bin/bash
```

## Code Style

- **Python**: Follow PEP 8
- **Type hints**: Required for new code
- **Docstrings**: Google-style docstrings
- **Line length**: 100 characters max
- **Format**: Use `black` and `isort`

### Run formatters:

```bash
pip install black isort
black src/
isort src/
```

## Project Structure

```
src/
├── application/       # Use cases (application logic)
├── domain/           # Business logic (pure Python)
├── infrastructure/   # External adapters (IMAP, AI, etc.)
└── main.py          # Entry point
```

**Follow Hexagonal Architecture principles:**
- Domain layer has no external dependencies
- Infrastructure adapts external services to domain interfaces
- Application layer orchestrates use cases

## Testing

### Run tests:

```bash
pytest tests/
```

### Test coverage:

```bash
pytest --cov=src tests/
```

### Integration tests:

```bash
pytest tests/integration/
```

## Documentation

- Update README.md for user-facing changes
- Update docstrings for code changes
- Add examples for new features
- Update CHANGELOG.md

## Areas Needing Help

### High Priority
- [ ] Web UI for configuration
- [ ] Additional AI providers (OpenAI, Gemini)
- [ ] Multi-language email support
- [ ] Better error messages

### Medium Priority
- [ ] Filter simulation/testing
- [ ] Email preview before filtering
- [ ] More sophisticated categorization
- [ ] Performance optimizations

### Low Priority
- [ ] Mobile app
- [ ] Scheduled analysis
- [ ] Email statistics dashboard

## Commit Message Guidelines

```
type(scope): short description

Longer description if needed

Fixes #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructure
- `test`: Add tests
- `chore`: Maintenance

**Examples:**
```
feat(ai): add OpenAI provider support
fix(imap): handle connection timeouts
docs(readme): update quick start guide
```

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

- Open an issue
- Start a discussion
- Contact: [@kekzl](https://github.com/kekzl)

Thank you for contributing! 🙏
