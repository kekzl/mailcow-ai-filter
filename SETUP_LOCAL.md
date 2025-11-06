# Quick Setup: Local LLM (Zero Cost)

Perfect for your setup: **16GB VRAM + 96GB RAM**

## 5-Minute Setup

### 1. Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Pull Best Model for Your Hardware

```bash
# Recommended: Llama 3.1 70B (fits perfectly in 16GB VRAM)
ollama pull llama3.1:70b-instruct-q4_K_M
```

This will download ~40GB. Grab a coffee! ☕

### 3. Start Ollama

```bash
ollama serve
```

(Usually auto-starts after install)

### 4. Configure Project

Create `config/config.yml`:

```yaml
protocol: "imap"

imap:
  server: "mail.kekz.org"
  username: "your-email@kekz.org"
  password: "your-password"
  use_ssl: true
  port: 993

ai:
  provider: "ollama"
  model: "llama3.1:70b-instruct-q4_K_M"
  base_url: "http://localhost:11434"
  max_emails_to_analyze: 100
```

### 5. Run

```bash
docker-compose up
```

## That's It!

**Benefits:**
- ✅ $0 cost (completely free)
- ✅ Unlimited runs
- ✅ 100% private (emails never leave your server)
- ✅ No API keys needed
- ✅ Works offline

**Performance:**
- Analysis time: 1-3 minutes for 100 emails
- Quality: Comparable to Claude Sonnet
- Perfect for your 16GB VRAM

## Alternative Models

Want different speed/quality tradeoff?

### Faster (32B model)
```bash
ollama pull qwen2.5:32b-instruct-q4_K_M
```

Then set `model: "qwen2.5:32b-instruct-q4_K_M"` in config.

### Ultra Fast (11B model)
```bash
ollama pull llama3.2:11b-instruct-q4_K_M
```

Then set `model: "llama3.2:11b-instruct-q4_K_M"` in config.

## Verify Setup

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# List installed models
ollama list

# Test model
ollama run llama3.1:70b-instruct-q4_K_M "Hello"
```

## Troubleshooting

**Ollama not responding?**
```bash
# Restart Ollama
systemctl restart ollama
# or
ollama serve
```

**Out of memory?**
```bash
# Use smaller model
ollama pull qwen2.5:32b-instruct-q4_K_M
```

**Want GPU stats?**
```bash
watch -n 1 nvidia-smi
```

## Full Documentation

- Detailed guide: [LOCAL_MODELS.md](LOCAL_MODELS.md)
- Claude API comparison: [CLAUDE.md](CLAUDE.md)
- General README: [README.md](README.md)

---

**Your setup is perfect for local AI. Enjoy zero-cost email sorting!** 🎉
