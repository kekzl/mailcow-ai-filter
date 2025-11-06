# Claude AI Integration Guide

This document explains how MailCow AI Filter uses Anthropic's Claude AI to analyze and categorize your emails.

## Overview

Claude AI powers the email pattern analysis in this project. It examines your emails and identifies natural categories, patterns, and filtering rules without any manual configuration.

## How It Works

### 1. Email Sampling
The system collects a sample of emails from your mailbox:
- Up to 100 emails by default
- Samples from multiple folders
- Extracts: sender, subject, folder, body preview

### 2. Pattern Analysis
Claude receives the email sample and analyzes:
- **Sender patterns**: Common domains, frequent senders
- **Subject patterns**: Keywords, formatting, prefixes
- **Content patterns**: Newsletter indicators, transactional emails
- **Existing organization**: How you've already sorted emails

### 3. Category Generation
Claude identifies natural categories like:
- Newsletters and marketing emails
- Work/professional correspondence
- Personal emails
- Financial notifications (banking, invoices)
- Social media notifications
- Automated/system emails

### 4. Rule Creation
For each category, Claude suggests:
- Specific filtering conditions
- Target folder names
- Confidence scores
- Example matches

## Getting Your API Key

### Step 1: Create an Anthropic Account

1. Visit https://console.anthropic.com/
2. Sign up or log in
3. Navigate to **API Keys** section
4. Click **Create Key**
5. Copy your API key (starts with `sk-ant-`)

### Step 2: Add to Configuration

**Option A: Configuration File**

Edit `config/config.yml`:
```yaml
ai:
  api_key: "sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  model: "claude-sonnet-4-5-20250929"
  max_emails_to_analyze: 100
```

**Option B: Environment Variable**

Create/edit `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Or export in your shell:
```bash
export ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Model Selection

### Available Models

**Claude Sonnet 4.5** (Default - Recommended)
- Model ID: `claude-sonnet-4-5-20250929`
- Best balance of intelligence and cost
- Excellent at pattern recognition
- **Cost**: $3 per million input tokens, $15 per million output tokens

**Claude Opus 4**
- Model ID: `claude-opus-4-20250514`
- Highest intelligence
- Best for complex categorization
- **Cost**: $15 per million input tokens, $75 per million output tokens

**Claude Haiku 3.5**
- Model ID: `claude-3-5-haiku-20241022`
- Fastest, most economical
- Good for simple categorization
- **Cost**: $0.80 per million input tokens, $4 per million output tokens

### Changing Models

Edit `config/config.yml`:
```yaml
ai:
  model: "claude-opus-4-20250514"  # For highest quality
  # or
  model: "claude-3-5-haiku-20241022"  # For lower cost
```

## Cost Estimation

### Typical Usage

For **100 emails** analyzed:
- Input: ~10,000-20,000 tokens (email samples + prompt)
- Output: ~2,000-4,000 tokens (analysis and categories)

### Cost Per Run

**With Claude Sonnet 4.5** (default):
- Input: 20,000 tokens × $3 / 1M = **$0.06**
- Output: 4,000 tokens × $15 / 1M = **$0.06**
- **Total: ~$0.12 per run**

**With Claude Opus 4**:
- Total: **~$0.60 per run**

**With Claude Haiku 3.5**:
- Total: **~$0.032 per run**

### Monthly Costs

If you run analysis:
- **Weekly**: $0.48-0.50/month (Sonnet)
- **Monthly**: $0.12-0.15/month (Sonnet)
- **One-time setup**: $0.12 (Sonnet)

**Recommended**: Run once for initial setup, then occasionally as email patterns change.

## Configuration Options

### Basic Configuration

```yaml
ai:
  provider: "anthropic"
  api_key: "your-key-here"
  model: "claude-sonnet-4-5-20250929"
```

### Advanced Configuration

```yaml
ai:
  provider: "anthropic"
  api_key: "your-key-here"
  model: "claude-sonnet-4-5-20250929"

  # How many emails to sample
  max_emails_to_analyze: 100

  # Sample evenly from folders
  sample_from_folders: true

analysis:
  # Only analyze these folders (empty = all)
  include_folders: []

  # Skip these folders
  exclude_folders:
    - "Trash"
    - "Spam"
    - "Junk"

  # Minimum emails needed to create a category
  min_category_size: 5
```

## API Rate Limits

Anthropic's rate limits (as of 2025):
- **Tier 1** (default): 50 requests/minute, 40,000 tokens/minute
- **Tier 2**: 1,000 requests/minute, 80,000 tokens/minute
- **Tier 3+**: Higher limits available

This project makes **1 API call per run**, so rate limits should never be an issue.

## Privacy & Security

### What Data is Sent to Claude?

The following email data is sent to Anthropic:
- ✅ Sender email addresses
- ✅ Subject lines
- ✅ First 200 characters of email body
- ✅ Folder names
- ❌ Full email bodies (not sent)
- ❌ Attachments (not sent)
- ❌ Email addresses in TO/CC fields (not sent)

### Data Privacy

According to Anthropic's policy:
- API requests are **not used to train models**
- Data is **not retained** after 30 days
- Compliant with GDPR, SOC 2, HIPAA (on Enterprise)

**For sensitive emails**: Consider filtering out sensitive folders in your configuration.

### Securing Your API Key

**Do:**
- ✅ Store in `config/config.yml` or `.env` (both in `.gitignore`)
- ✅ Use environment variables in production
- ✅ Restrict file permissions: `chmod 600 config/config.yml`

**Don't:**
- ❌ Commit API keys to git
- ❌ Share config files publicly
- ❌ Hardcode in source files

## Troubleshooting

### Error: Invalid API Key

```
Failed to initialize AI analyzer: Invalid API key
```

**Solution:**
1. Verify key starts with `sk-ant-`
2. Check for extra spaces/newlines
3. Generate a new key at https://console.anthropic.com/

### Error: Rate Limited

```
anthropic.RateLimitError: Rate limit exceeded
```

**Solution:**
- Wait 60 seconds and retry
- Reduce `max_emails_to_analyze`
- Upgrade API tier at Anthropic

### Error: Insufficient Credits

```
anthropic.PermissionDeniedError: Insufficient credits
```

**Solution:**
1. Visit https://console.anthropic.com/settings/billing
2. Add payment method or credits
3. Minimum: $5 credit (enough for ~40+ runs with Sonnet)

### No Categories Generated

**Issue:** AI returns empty categories

**Solutions:**
- Increase `max_emails_to_analyze` (need more data)
- Check you have emails in multiple folders
- Reduce `min_category_size` threshold
- Review logs: `logs/ai-filter.log`

### Poor Category Quality

**Issue:** Categories don't make sense

**Solutions:**
- Increase sample size: `max_emails_to_analyze: 200`
- Use Claude Opus for better quality
- Manually organize more emails first, then re-run
- Ensure diverse email sample (multiple folders)

## Advanced: Custom Prompts

If you want to customize how Claude analyzes your emails, edit `src/ai_analyzer.py`:

```python
def _create_analysis_prompt(self, email_sample, existing_folders):
    prompt = f"""Analyze these emails and focus on:

    1. Newsletter detection
    2. Work vs personal separation
    3. Priority/urgency indicators

    Emails:
    {email_sample}
    """
    return prompt
```

## Example Analysis Output

Claude's typical response structure:

```json
{
  "categories": [
    {
      "name": "Newsletters",
      "description": "Marketing emails and subscriptions",
      "patterns": [
        "from: @newsletter.example.com",
        "subject: Newsletter",
        "subject: Unsubscribe"
      ],
      "suggested_folder": "Newsletters",
      "confidence": 0.92,
      "example_subjects": [
        "Weekly Newsletter - January 2025",
        "Latest Updates from Example Corp"
      ]
    },
    {
      "name": "Work Email",
      "description": "Professional correspondence",
      "patterns": [
        "from: @company.com",
        "subject: [WORK]",
        "subject: RE: Project"
      ],
      "suggested_folder": "Work",
      "confidence": 0.88,
      "example_subjects": [
        "[WORK] Team Meeting Notes",
        "RE: Project Proposal"
      ]
    }
  ]
}
```

## Best Practices

### 1. Prepare Your Mailbox
- Manually organize 50-100 emails first
- Create folders you want to use
- This helps Claude learn your preferences

### 2. Start Small
- First run: Analyze 50-100 emails
- Review generated rules carefully
- Test with a subset of emails
- Gradually increase if satisfied

### 3. Iterate
- Run analysis multiple times
- Refine your folder structure
- Claude learns from your organization

### 4. Cost Optimization
- Use Haiku for simple categorization
- Run analysis sparingly (monthly/quarterly)
- Reduce `max_emails_to_analyze` if budget-conscious

### 5. Quality Over Quantity
- Better to analyze well-organized 50 emails
- Than poorly organized 500 emails
- Manual organization improves AI results

## Support

### Claude API Issues
- Documentation: https://docs.anthropic.com/
- Support: support@anthropic.com
- Status: https://status.anthropic.com/

### Project Issues
- Check `logs/ai-filter.log`
- Review configuration
- Open GitHub issue

## Further Reading

- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Claude Model Comparison](https://docs.anthropic.com/en/docs/models-overview)
- [API Pricing](https://www.anthropic.com/pricing)
- [Best Practices for Prompting](https://docs.anthropic.com/en/docs/prompt-engineering)

---

**Remember**: Claude is a tool to help you, not replace your judgment. Always review generated rules before applying them to your email!
