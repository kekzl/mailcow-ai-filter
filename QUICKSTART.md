# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- MailCow server with a mailbox
- Anthropic API key (get one at https://console.anthropic.com/)
- Docker installed

## Step-by-Step Setup

### 1. Get Your Credentials

You'll need:
- ✉️ Your email address
- 🔑 Your email password
- 🤖 Anthropic API key

### 2. Create Configuration

```bash
# Create config from example
cp config/config.example.yml config/config.yml

# Edit with your details
nano config/config.yml
```

Fill in:
```yaml
protocol: "imap"

imap:
  server: "mail.yourdomain.com"  # Your MailCow server
  username: "you@yourdomain.com"  # Your email
  password: "your-password"       # Your password
  use_ssl: true
  port: 993

ai:
  api_key: "sk-ant-..."  # Your Anthropic API key
```

### 3. Run It

```bash
# Build and run
docker-compose up

# Or run in background
docker-compose up -d
```

### 4. Check Results

```bash
# View generated rules
cat output/generated.sieve

# Check logs
tail -f logs/ai-filter.log
```

### 5. Apply to MailCow

1. **Review the rules** in `output/generated.sieve`
2. **Login to MailCow** web interface
3. **Navigate to**: Mailbox → Your mailbox → Edit
4. **Click**: Sieve filters tab
5. **Paste** the generated rules
6. **Save** and activate

## Example Output

```
==============================================================
MailCow AI Filter - Email Sorting with AI-Generated Sieve Rules
==============================================================

Protocol: IMAP

2025-11-05 12:00:00 - INFO - Connected to IMAP server
2025-11-05 12:00:01 - INFO - Found 8 folders
2025-11-05 12:00:05 - INFO - Collected 100 emails for analysis
2025-11-05 12:00:20 - INFO - AI identified 5 categories
2025-11-05 12:00:20 - INFO - Saved Sieve rules to output/generated.sieve

==============================================================
Analysis Complete!
==============================================================

Analyzed: 100 emails
Identified: 5 categories
Generated: output/generated.sieve

Next steps:
1. Review the generated rules in output/generated.sieve
2. Test with a small subset of emails
3. Upload to MailCow: Mailbox → Edit → Sieve filters
```

## Testing Rules Before Full Deployment

### Option 1: MailCow Testing

1. Copy rules to MailCow Sieve interface
2. Send test emails to yourself
3. Check if they're sorted correctly
4. Adjust rules as needed

### Option 2: Manual Testing

```bash
# Install sieve testing tool
apt-get install sieve-connect

# Test rules
sieve-connect -u you@yourdomain.com mail.yourdomain.com
```

## Common Issues

### Can't Connect to IMAP

**Error:** `Failed to connect to IMAP server`

**Fix:**
- Check server address (should be your MailCow domain)
- Verify port (993 for SSL, 143 for non-SSL)
- Ensure email/password are correct
- Check if IMAP is enabled in MailCow

### No Anthropic API Key

**Error:** `Failed to initialize AI analyzer`

**Fix:**
1. Visit https://console.anthropic.com/
2. Create account/login
3. Generate API key
4. Add to `config/config.yml`

### No Rules Generated

**Issue:** AI didn't find patterns

**Fix:**
- Ensure you have at least 20-30 emails
- Check different folders have emails
- Look at logs for confidence scores
- May need more email samples

## Next Steps

1. **Schedule regular runs** to update rules as email patterns change
2. **Customize rules** by editing `output/generated.sieve`
3. **Add more folders** by organizing emails first, then re-running
4. **Fine-tune** patterns based on real-world testing

## Advanced: Running Periodically

Add to cron for weekly analysis:

```bash
# Edit crontab
crontab -e

# Add weekly run (every Sunday at 2am)
0 2 * * 0 cd /path/to/mailcow-ai-filter && docker-compose up

```

Or use Docker restart policy:

```yaml
# In docker-compose.yml
services:
  mailcow-ai-filter:
    restart: "no"  # Run once then stop
```

## Need Help?

- 📖 Read full README.md
- 🐛 Check logs in `logs/ai-filter.log`
- 💬 Open an issue on GitHub
- 📧 Review MailCow Sieve documentation

## Tips for Best Results

1. **Organize first**: Manually sort some emails into folders
2. **More emails = better patterns**: 50-100+ emails recommended
3. **Review before applying**: AI is smart but not perfect
4. **Iterate**: Run multiple times as you organize more emails
5. **Test thoroughly**: Send yourself test emails before going live
