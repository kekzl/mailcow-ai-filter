# MailCow AI Filter

AI-powered email sorting for MailCow using Claude to generate Sieve filtering rules.

## Overview

This tool analyzes your existing emails using AI (Anthropic Claude) to identify patterns and automatically generates Sieve filtering rules for MailCow. It learns from how you've organized your emails and suggests smart categorization rules.

### Features

- 🤖 **AI-Powered Analysis**: Uses Claude API or Local LLMs (Ollama)
- 💰 **Zero Cost Option**: Run completely free with local models (16GB VRAM recommended)
- 📧 **IMAP/ActiveSync Support**: Connect via IMAP (recommended) or ActiveSync
- 🔧 **Sieve Rule Generation**: Creates standard Sieve filter rules
- 🐳 **Dockerized**: Runs as a container alongside MailCow
- 🔒 **Safe**: Generates rules for manual review before applying
- 📊 **Pattern Detection**: Identifies senders, subjects, and content patterns
- 🔐 **Privacy**: Optional fully offline operation with local models

## Quick Start

### 1. Clone and Configure

```bash
cd /path/to/mailcow-ai-filter

# Copy and edit configuration
cp config/config.example.yml config/config.yml
nano config/config.yml
```

### 2. Edit Configuration

Edit `config/config.yml`:

**Option A: Using Claude API**
```yaml
protocol: "imap"

imap:
  server: "mail.yourdomain.com"
  username: "your-email@yourdomain.com"
  password: "your-password"
  use_ssl: true
  port: 993

ai:
  provider: "anthropic"
  api_key: "your-anthropic-api-key"
  model: "claude-sonnet-4-5-20250929"
```

**Option B: Using Local LLM (FREE, requires GPU) ⭐ RECOMMENDED**
```yaml
protocol: "imap"

imap:
  server: "mail.yourdomain.com"
  username: "your-email@yourdomain.com"
  password: "your-password"
  use_ssl: true
  port: 993

ai:
  provider: "ollama"
  master_model: "qwen2.5-coder:14b"  # WINNER: 11% faster, 19% more rules
  base_url: "http://localhost:11434"
```

See [LOCAL_MODELS.md](LOCAL_MODELS.md) for local model setup.

### 3. Build and Run

```bash
# Build container
docker-compose build

# Run analysis
docker-compose up
```

### 4. Review and Apply Rules

1. Check generated rules in `output/generated.sieve`
2. Review and edit as needed
3. Upload to MailCow:
   - Go to Mailbox → Edit → Sieve filters
   - Paste the rules or upload the file
   - Save and activate

## Protocol: IMAP vs ActiveSync

### IMAP (Recommended) ✅

**Pros:**
- ✅ Fully supported and tested
- ✅ Simple, mature protocol
- ✅ Works perfectly with MailCow
- ✅ Reliable Python libraries

**Use IMAP if:** You want a working solution (recommended for 99% of users)

### ActiveSync ⚠️

**Pros:**
- Used by mobile devices
- Official Microsoft protocol

**Cons:**
- ⚠️ Requires WBXML (WAP Binary XML) encoding
- ⚠️ Limited/incomplete Python libraries
- ⚠️ Complex implementation
- ⚠️ Current implementation is a framework only

**Use ActiveSync if:** You have specific requirements and are willing to implement WBXML support

## Configuration

### Configuration File (`config/config.yml`)

#### Mode 1: Embedding-Based Clustering (Recommended)

```yaml
# Protocol: 'imap' recommended
protocol: "imap"

# IMAP settings
imap:
  server: "mail.yourdomain.com"
  username: "user@yourdomain.com"
  password: "password"
  use_ssl: true
  port: 993

# AI settings for embedding mode
ai:
  provider: "ollama"
  model: "qwen3:14b"
  base_url: "http://localhost:11434"

  # Enable embedding mode (FASTEST for large mailboxes)
  use_embedding: true

  # Hierarchical mode (fallback if embedding disabled)
  use_hierarchical: false

  # Worker model for summarization (only used if hierarchical enabled)
  worker_model: "gemma2:2b"
  master_model: "qwen3:14b"

  # Analysis settings
  max_emails_to_analyze: 5000  # Process up to 5000 emails
  max_parallel_workers: 3      # Parallel workers for summarization

# Analysis settings
analysis:
  exclude_folders:
    - "Trash"
    - "Spam"
  min_category_size: 5
  months_back: 12

# Sieve generation
sieve:
  output_file: "/app/output/generated.sieve"
  create_folders: true
  mark_as_read: false
```

#### Mode 2: Hierarchical Two-Tier

```yaml
ai:
  provider: "ollama"

  # Disable embedding, enable hierarchical
  use_embedding: false
  use_hierarchical: true

  worker_model: "gemma2:2b"      # Fast model for summaries
  master_model: "qwen3:14b"      # Smart model for patterns

  max_emails_to_analyze: 1000    # Reasonable for hierarchical
  max_parallel_workers: 3
```

#### Mode 3: Simple Mode (Legacy)

```yaml
ai:
  provider: "anthropic"
  api_key: "sk-ant-..."
  model: "claude-sonnet-4-5-20250929"

  # Both disabled = simple mode
  use_embedding: false
  use_hierarchical: false

  max_emails_to_analyze: 100     # Small sample
```

### Environment Variables (Alternative)

Create `.env` file:

```bash
MAIL_SERVER=mail.yourdomain.com
MAIL_USERNAME=user@yourdomain.com
MAIL_PASSWORD=password
PROTOCOL=imap
ANTHROPIC_API_KEY=sk-ant-...
```

## How It Works

The tool supports three analysis modes with different performance characteristics:

### Mode 1: Embedding-Based Clustering (Recommended for 1000+ emails)

**Performance**: 10-50x faster than hierarchical mode for large email volumes

1. **Connect**: Connects to your mailbox via IMAP
2. **Fetch Structure**: Retrieves existing folder structure and email counts
3. **Collect**: Fetches up to 5000 emails from your mailbox
4. **Embed**: Generates semantic embeddings using SentenceTransformers
5. **Cluster**: Groups similar emails using HDBSCAN algorithm
6. **Label**: Master LLM analyzes representative emails from each cluster
7. **Generate**: Creates hierarchical Sieve filtering rules
8. **Review**: You review and approve rules before applying

**Speed**: ~100-200 emails/second (on modern CPU)
**Best for**: Large mailboxes (1000-5000+ emails)
**Accuracy**: High - ML clustering finds natural email patterns

### Mode 2: Hierarchical Two-Tier (Recommended for 100-1000 emails)

**Performance**: 2-5x faster than simple mode

1. **Connect**: Connects to your mailbox via IMAP
2. **Fetch Structure**: Retrieves existing folder structure and email counts
3. **Collect**: Fetches emails from your mailbox
4. **Summarize**: Worker LLM creates structured summaries (parallel)
5. **Analyze**: Master LLM analyzes all summaries for patterns
6. **Generate**: Creates hierarchical Sieve filtering rules
7. **Review**: You review and approve rules before applying

**Speed**: ~10-30 emails/second (depends on LLM speed)
**Best for**: Medium mailboxes (100-1000 emails)
**Accuracy**: Very high - two-tier analysis captures nuance

### Mode 3: Simple Direct Analysis (Legacy)

**Performance**: Baseline

1. **Connect**: Connects to your mailbox via IMAP
2. **Sample**: Analyzes a small sample of emails (20-50)
3. **Analyze**: Single LLM call analyzes sample
4. **Generate**: Creates basic Sieve filtering rules
5. **Review**: You review and approve rules before applying

**Speed**: ~5-10 emails/second
**Best for**: Small mailboxes (<100 emails) or quick testing
**Accuracy**: Good for simple patterns

## Example Generated Rules

```sieve
# Rule: Newsletters
# Description: Marketing emails and newsletters
# Confidence: 85%
if anyof (
  address :domain :is "from" "newsletter.example.com",
  header :contains "subject" "Newsletter"
) {
  fileinto "Newsletters";
  stop;
}

# Rule: Work
# Description: Work-related correspondence
# Confidence: 92%
if anyof (
  address :domain :is "from" "company.com",
  header :contains "subject" "[WORK]"
) {
  fileinto "Work";
  stop;
}
```

## Docker Deployment

### Standalone

```bash
docker-compose up -d
```

### With MailCow Network

Update `docker-compose.yml`:

```yaml
networks:
  mailcow-network:
    external: true
    name: mailcowdockerized_mailcow-network
```

Then:

```bash
docker-compose up -d
```

## Folder Structure

```
mailcow-ai-filter/
├── config/
│   ├── config.example.yml
│   └── config.yml (your config)
├── src/
│   ├── main.py
│   ├── config.py
│   ├── imap_client.py
│   ├── activesync_client.py
│   ├── ai_analyzer.py
│   ├── sieve_generator.py
│   └── utils.py
├── output/
│   └── generated.sieve (generated rules)
├── logs/
│   └── ai-filter.log
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Troubleshooting

### Connection Issues

**IMAP connection fails:**
```bash
# Test IMAP connection manually
openssl s_client -connect mail.yourdomain.com:993
```

**ActiveSync not working:**
- ActiveSync requires WBXML implementation
- Switch to IMAP (recommended)

### API Issues

**Anthropic API key invalid:**
- Get key from https://console.anthropic.com/
- Set in `config/config.yml` or `ANTHROPIC_API_KEY` env var

### No Rules Generated

- Ensure you have enough emails (at least 20-30)
- Check AI confidence threshold in logs
- Review `logs/ai-filter.log` for details

## Security Notes

- **Credentials**: Store config files securely, never commit secrets
- **API Key**: Keep your Anthropic API key secret
- **Review Rules**: Always review generated rules before applying
- **Test First**: Test rules on a small email subset first

## Development

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export MAIL_SERVER=mail.yourdomain.com
export MAIL_USERNAME=user@yourdomain.com
export MAIL_PASSWORD=password
export ANTHROPIC_API_KEY=sk-ant-...

# Run
python -m src.main
```

### Extending

**Add new protocols:**
- Implement client in `src/`
- Follow `IMAPClient` interface
- Add to `main.py`

**Customize Sieve generation:**
- Edit `src/sieve_generator.py`
- Modify `_pattern_to_sieve_condition()`

## AI Options & Costs

### Option 1: Claude API (Paid)

Anthropic Claude API costs:
- **Analysis**: ~$0.12 per run (100 emails)
- **Monthly**: ~$0.50 for 4 runs
- See [CLAUDE.md](CLAUDE.md) for details

### Option 2: Local LLMs (FREE)

Run on your own GPU with Ollama:
- **Cost**: $0 (free)
- **Privacy**: Fully offline
- **Requirements**: 16GB VRAM recommended
- See [LOCAL_MODELS.md](LOCAL_MODELS.md) for setup

**Recommended:** If you have a GPU with 16GB+ VRAM, use local models for zero cost!

## Contributing

Contributions welcome! Especially:

- Full WBXML implementation for ActiveSync
- Additional AI providers (OpenAI, local models)
- UI/web interface
- Improved pattern detection

## License

MIT License - see LICENSE file

## Support

For issues or questions:
- Open an issue on GitHub
- Check logs in `logs/ai-filter.log`
- Review MailCow Sieve documentation

## Acknowledgments

- Built for MailCow (https://mailcow.email/)
- Powered by Anthropic Claude AI
- Sieve filtering standard (RFC 5228)
