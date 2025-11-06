# Claude AI Integration Guide

AI-powered email analysis using Anthropic's Claude API.

---

## Quick Start

**1. Get API Key:** https://console.anthropic.com/ → API Keys → Create Key

**2. Configure:**
```yaml
# config/config.yml
ai:
  provider: "anthropic"
  api_key: "sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  model: "claude-sonnet-4-5-20250929"
```

**3. Run:**
```bash
./mailcow-filter.sh analyze
```

**Cost:** ~$0.12 per run (1,500 emails analyzed)

---

## Table of Contents

- [Claude vs Ollama](#claude-vs-ollama)
- [Setup](#setup)
- [Models & Pricing](#models--pricing)
- [Configuration](#configuration)
- [Privacy & Security](#privacy--security)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

---

## Claude vs Ollama

**Want a free alternative?** See [LOCAL_MODELS.md](LOCAL_MODELS.md) for Ollama (local LLM) setup.

| Feature | Claude API | Ollama (Local) |
|---------|-----------|----------------|
| **Cost** | ~$0.12 per run | $0 (free) |
| **Privacy** | Data sent to Anthropic | 100% offline |
| **Speed** | Fast (cloud) | Slower (local) |
| **Quality** | Excellent | Very good |
| **Setup** | API key only | Install + download model |
| **Requirements** | Internet | 16GB RAM, GPU recommended |

**Switching:** Just change `provider: "anthropic"` to `provider: "ollama"` in `config/config.yml`.

---

## Setup

### 1. Get API Key

1. Visit https://console.anthropic.com/
2. Sign up/login → **API Keys** → **Create Key**
3. Copy key (starts with `sk-ant-`)

### 2. Add to Configuration

**Option A: Config File** (Recommended)

```yaml
# config/config.yml
ai:
  provider: "anthropic"
  api_key: "sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  model: "claude-sonnet-4-5-20250929"
```

**Option B: Environment Variable**

```bash
# .env file
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. Secure Your Key

```bash
chmod 600 config/config.yml  # Restrict file permissions
```

**Never:** Commit to git, share publicly, or hardcode in source files.

---

## Models & Pricing

### Available Models

| Model | Use Case | Cost/Run | Speed |
|-------|----------|----------|-------|
| **Claude Sonnet 4.5** ⭐ | Recommended | ~$0.12 | Fast |
| **Claude Opus 4** | Highest quality | ~$0.60 | Medium |
| **Claude Haiku 3.5** | Budget option | ~$0.03 | Fastest |

**Default:** Sonnet 4.5 (`claude-sonnet-4-5-20250929`)

### Pricing Details

**Claude Sonnet 4.5:**
- Input: $3 / 1M tokens
- Output: $15 / 1M tokens
- **Typical run:** 20k input + 4k output = **$0.12**

**Claude Opus 4:**
- Input: $15 / 1M tokens
- Output: $75 / 1M tokens

**Claude Haiku 3.5:**
- Input: $0.80 / 1M tokens
- Output: $4 / 1M tokens

### Changing Models

```yaml
# config/config.yml
ai:
  model: "claude-opus-4-20250514"        # Highest quality
  # or
  model: "claude-3-5-haiku-20241022"     # Lowest cost
```

### Monthly Costs

| Usage | Cost (Sonnet) |
|-------|---------------|
| One-time setup | $0.12 |
| Monthly re-run | $0.12-0.15 |
| Weekly runs | $0.48-0.50 |

**Recommendation:** Run once for setup, then occasionally as email patterns change.

---

## Configuration

### Basic

```yaml
ai:
  provider: "anthropic"
  api_key: "your-key-here"
  model: "claude-sonnet-4-5-20250929"
```

### Advanced

```yaml
ai:
  provider: "anthropic"
  api_key: "your-key-here"
  model: "claude-sonnet-4-5-20250929"

  # Embedding-based ML clustering (default: true, recommended)
  use_embedding: true

  # Two-tier hierarchical analysis (default: false)
  use_hierarchical: false

  # Number of emails to sample for analysis
  max_emails_to_analyze: 100

analysis:
  # Folders to analyze (empty = all)
  include_folders: []

  # Folders to skip
  exclude_folders:
    - "Trash"
    - "Spam"
    - "Junk"

  # Minimum emails to create a category
  min_category_size: 5
```

### Analysis Modes

**Embedding Mode** (Default - Recommended)
- Uses ML clustering (HDBSCAN)
- Best for 1,000+ emails
- Fast: ~100-200 emails/second

**Hierarchical Mode**
- Two-tier AI analysis
- Best for 100-1,000 emails
- Higher quality: ~10-30 emails/second

**Simple Mode**
- Single AI call
- Best for <100 emails
- ~5-10 emails/second

```yaml
ai:
  use_embedding: true      # Enable ML clustering (recommended)
  use_hierarchical: false  # Enable two-tier analysis
```

---

## Privacy & Security

### What Data is Sent?

**Sent to Anthropic:**
- ✅ Sender email addresses
- ✅ Subject lines
- ✅ First 200 characters of email body
- ✅ Folder names

**NOT sent:**
- ❌ Full email bodies
- ❌ Attachments
- ❌ TO/CC recipient addresses

### Anthropic's Privacy Policy

- ✅ **Not used for training** - Your emails won't train Claude
- ✅ **30-day retention** - Data deleted after 30 days
- ✅ **Compliance** - GDPR, SOC 2, HIPAA (Enterprise)

### Security Best Practices

**Do:**
- ✅ Store keys in `config/config.yml` or `.env` (both gitignored)
- ✅ Use environment variables in production
- ✅ Set file permissions: `chmod 600 config/config.yml`
- ✅ Filter out sensitive folders in configuration

**Don't:**
- ❌ Commit API keys to git
- ❌ Share config files publicly
- ❌ Hardcode keys in source files

### API Rate Limits

**Tier 1** (default): 50 requests/min, 40k tokens/min
- This project: **1 request per run** → Rate limits not an issue

---

## Troubleshooting

### Invalid API Key

```
Failed to initialize AI analyzer: Invalid API key
```

**Fix:**
1. Verify key starts with `sk-ant-`
2. Check for extra spaces/newlines
3. Generate new key at https://console.anthropic.com/

### Insufficient Credits

```
anthropic.PermissionDeniedError: Insufficient credits
```

**Fix:**
1. Visit https://console.anthropic.com/settings/billing
2. Add payment method
3. Add $5 minimum (good for ~40 runs with Sonnet)

### Rate Limited

```
anthropic.RateLimitError: Rate limit exceeded
```

**Fix:**
- Wait 60 seconds and retry
- Reduce `max_emails_to_analyze`
- Upgrade API tier

### No Categories Generated

**Possible causes:**
- Not enough diverse emails (increase `max_emails_to_analyze`)
- All emails too similar
- `min_category_size` threshold too high

**Fix:**
- Increase sample size: `max_emails_to_analyze: 200`
- Reduce threshold: `min_category_size: 3`
- Check logs: `logs/ai-filter.log`

### Poor Category Quality

**Fix:**
- Use Claude Opus 4 for better quality
- Manually organize 50-100 emails first
- Ensure diverse email sample (multiple folders)
- Increase sample size

---

## Advanced Usage

### Custom Prompts

Customize email analysis behavior by editing adapter files:

**File:** `src/infrastructure/adapters/anthropic_adapter.py`

```python
def _create_analysis_prompt(self, email_sample, existing_filters=None):
    prompt = f"""Analyze emails with focus on:

    1. Newsletter detection (look for unsubscribe links)
    2. Work vs personal separation
    3. Priority/urgency indicators
    4. Automated vs human-sent emails

    Existing filters to avoid duplication:
    {existing_filters}

    Email samples:
    {email_sample}
    """
    return prompt
```

**Note:** Project uses hexagonal architecture - AI providers are in `src/infrastructure/adapters/`.

### How Analysis Works

**1. Email Sampling**
- Fetches up to 100 emails (configurable)
- Samples from multiple folders
- Extracts: sender, subject, body preview

**2. Pattern Analysis**
- Sender patterns (domains, frequent senders)
- Subject patterns (keywords, prefixes)
- Content patterns (newsletters, transactional)
- Existing organization (learns from your folders)

**3. Category Generation**
- Identifies natural categories
- Creates filtering conditions
- Suggests folder names
- Assigns confidence scores

**4. Sieve Rule Creation**
- Generates standard Sieve filter syntax
- Validates rules for compatibility
- Prioritizes rules correctly
- Saves to `output/generated.sieve`

---

## Best Practices

### 1. Prepare Your Mailbox
✅ Manually organize 50-100 emails first
✅ Create folders you want to use
✅ This helps Claude learn your preferences

### 2. Start Small
✅ First run: 50-100 emails
✅ Review generated rules carefully
✅ Test before applying to entire mailbox
✅ Gradually increase if satisfied

### 3. Iterate
✅ Run analysis multiple times
✅ Refine folder structure based on results
✅ Claude learns from your organization

### 4. Cost Optimization
✅ Use Haiku for simple categorization
✅ Run sparingly (monthly/quarterly)
✅ Reduce `max_emails_to_analyze` if needed
✅ Consider Ollama for zero cost

### 5. Quality Over Quantity
✅ Better: 50 well-organized emails
❌ Worse: 500 chaotic emails
✅ Manual organization improves AI results

---

## Support

### Claude API Issues
- 📖 [Documentation](https://docs.anthropic.com/)
- 📧 support@anthropic.com
- 🟢 [Status Page](https://status.anthropic.com/)

### Project Issues
- 📝 Check `logs/ai-filter.log`
- ⚙️ Review `config/config.yml`
- 🐛 [Open GitHub Issue](https://github.com/kekzl/mailcow-ai-filter/issues)
- 💬 [GitHub Discussions](https://github.com/kekzl/mailcow-ai-filter/discussions)

### Further Reading
- [Anthropic API Docs](https://docs.anthropic.com/)
- [Model Comparison](https://docs.anthropic.com/en/docs/models-overview)
- [API Pricing](https://www.anthropic.com/pricing)
- [Prompting Best Practices](https://docs.anthropic.com/en/docs/prompt-engineering)

---

## Workflow Example

```bash
# 1. Analyze emails (generates filter rules)
./mailcow-filter.sh analyze

# 2. Review generated filter
./mailcow-filter.sh view-filter

# 3. Create folders
./mailcow-filter.sh create-folders

# 4. Upload filter to server
./mailcow-filter.sh upload-filter

# 5. (Optional) Apply to existing emails
./mailcow-filter.sh apply-retroactive
```

**Total cost:** ~$0.12 (one-time)
**Total time:** ~2-5 minutes
**Result:** Fully automated email organization

---

**Remember:** Claude is a tool to assist you, not replace your judgment. Always review generated rules before applying them!

**Want zero cost?** Check out [LOCAL_MODELS.md](LOCAL_MODELS.md) for the Ollama alternative.
