# Reading Existing Sieve Filters

The MailCow AI Filter can now read your existing Sieve filters and include them in the analysis to:

- ✅ **Avoid duplicates** - Won't create rules that already exist
- ✅ **Learn from your patterns** - Understands your manual organization preferences
- ✅ **Create complementary rules** - Fills gaps in your existing filters
- ✅ **Avoid conflicts** - Ensures new rules work with existing ones

## How It Works

### 1. Automatic Detection (Integrated)

The analysis now automatically attempts to fetch your existing filters via ManageSieve protocol:

```python
python -m src.main  # Automatically tries to read existing filters
```

**What happens:**
1. Connects to ManageSieve server (port 4190)
2. Fetches your active Sieve script
3. Parses existing rules and folders
4. Passes this information to the AI
5. AI generates complementary rules

**Requirements:**
- ManageSieve must be enabled on your server (port 4190)
- Install: `pip install managesieve`

If ManageSieve is not available, the analysis continues normally without considering existing filters.

### 2. Manual Fetch (Standalone Script)

You can also manually fetch and review your existing filters:

```bash
python fetch_existing_filters.py
```

**Output:**
- Creates `output/existing_filters.txt`
- Shows all your current filter rules
- Displays conditions and target folders
- Includes full Sieve script content

**Example output:**
```
====================================================================================
EXISTING SIEVE FILTERS
=====================================================================================

## Script: roundcube
Status: ACTIVE
----------------------------------------------------------------------

Found 3 filter rules:

1. Move spam to Junk folder
   → Folder: Junk
   → Conditions:
      - subject:***SPAM***
      - subject:[SPAM]

2. Newsletter filtering
   → Folder: Newsletters
   → Conditions:
      - from:newsletter.example.com
      - subject:unsubscribe

3. Work emails
   → Folder: Work
   → Conditions:
      - from:company.com
```

## Installation

### Option 1: pip install (Recommended)

```bash
cd /home/kekz/git.home.kekz.org/mailcow-ai-filter
source venv/bin/activate
pip install managesieve
```

### Option 2: Add to requirements.txt

Add to `requirements.txt`:
```
managesieve>=0.5.0
```

Then install:
```bash
pip install -r requirements.txt
```

## Configuration

No additional configuration needed! The system automatically uses your IMAP credentials:

```yaml
# config/config.yml
imap:
  server: "mail.kekz.org"      # Also used for ManageSieve
  username: "kekz@kekz.org"
  password: "your-password"
```

**Note:** ManageSieve typically uses the same server as IMAP but on port 4190.

## How AI Uses Existing Filters

When existing filters are found, the AI:

### 1. Analyzes Your Organization Style

```
Existing filters show:
- You prefer specific folder names like "Work/Projects" vs generic "Work"
- You filter by sender domain more than subject keywords
- You have 5-10 emails per category on average
```

### 2. Avoids Duplicates

```
AI sees:
- "from:@github.com → Work/GitHub" exists

AI creates:
- "from:@gitlab.com → Work/GitLab" (complementary)
- NOT "from:@github.com → Development" (duplicate!)
```

### 3. Fills Gaps

```
Existing:
- Amazon orders → Shopping/Amazon
- PayPal receipts → Finance/PayPal

AI adds:
- eBay purchases → Shopping/eBay  (new category)
- Stripe invoices → Finance/Stripe (new category)
```

### 4. Respects Hierarchy

```
Existing:
- Shopping/Amazon
- Shopping/eBay

AI maintains:
- Shopping/Walmart (follows existing hierarchy)
- NOT just "Walmart" (respects your structure)
```

## Troubleshooting

### Error: "managesieve library not installed"

**Solution:**
```bash
pip install managesieve
```

### Error: "ManageSieve connection failed"

**Possible causes:**
1. **Port blocked** - ManageSieve runs on port 4190
   ```bash
   # Test connection
   telnet mail.kekz.org 4190
   ```

2. **Not enabled** - Check MailCow configuration
   - Login to MailCow admin
   - Check if ManageSieve is enabled

3. **Firewall** - Port 4190 might be blocked

**Workaround:**
The system continues without existing filters if ManageSieve isn't available.

### No filters detected

**Check:**
1. Do you have active Sieve filters?
   - Login to MailCow webmail
   - Go to Settings → Filters
   - Verify you have rules enabled

2. Is the script active?
   - Only active scripts are fetched
   - Check script status in webmail

### Filters not being considered

**Debug:**
1. Check logs:
   ```bash
   tail -f logs/ai-filter.log | grep -i sieve
   ```

2. Look for:
   ```
   INFO: Retrieved existing Sieve filters for analysis
   ```

3. If not present, ManageSieve connection failed

## Advanced Usage

### Fetch filters without running analysis

```bash
python fetch_existing_filters.py
```

### Review existing filters

```bash
cat output/existing_filters.txt
```

### Compare old vs new filters

```bash
# Before analysis
python fetch_existing_filters.py > before.txt

# After analysis
cat output/generated.sieve > after.txt

# Compare
diff before.txt after.txt
```

### Disable existing filter detection

If you want to ignore existing filters and start fresh:

**Option 1:** Don't install managesieve library
**Option 2:** Block port 4190 temporarily
**Option 3:** Deactivate filters in webmail before analysis

## Benefits

### With Existing Filter Integration:

✅ **No duplicates** - AI won't recreate what you already have
✅ **Consistent naming** - Follows your folder naming patterns
✅ **Complementary rules** - Adds to existing organization
✅ **Faster setup** - Builds on your work, not from scratch

### Without Integration:

⚠️ **May create duplicates** - Could conflict with existing rules
⚠️ **Inconsistent naming** - Might not match your style
⚠️ **More manual work** - Need to merge rules yourself

## Example Workflow

### Complete workflow with existing filters:

```bash
# 1. Install ManageSieve support
pip install managesieve

# 2. Review your current filters (optional)
python fetch_existing_filters.py
cat output/existing_filters.txt

# 3. Run analysis (automatically reads existing filters)
python -m src.main

# 4. Review generated filter
cat output/generated.sieve

# 5. Upload to MailCow
python upload_filter_api.py
```

### Result:

```
Your existing filters:
✓ Work/GitHub (from:@github.com)
✓ Shopping/Amazon (from:@amazon.de)

AI adds:
+ Work/GitLab (from:@gitlab.com)
+ Work/Slack (from:@slack.com)
+ Shopping/eBay (from:@ebay.de)
+ Finance/PayPal (from:@paypal.com)
```

## Technical Details

### Protocol

- **ManageSieve** - RFC 5804
- **Port:** 4190 (default)
- **Authentication:** Same as IMAP
- **TLS:** Usually required

### Implementation

1. **Connect:** Uses same credentials as IMAP
2. **List:** Fetches all Sieve scripts
3. **Get Active:** Retrieves currently active script
4. **Parse:** Extracts rules, folders, conditions
5. **Summarize:** Creates human-readable summary
6. **Pass to AI:** Includes in LLM prompt

### Security

- ✅ Uses existing IMAP credentials (no new secrets)
- ✅ Read-only access (doesn't modify filters)
- ✅ Optional feature (gracefully disabled if unavailable)
- ✅ Logged but not stored persistently

## Support

### If ManageSieve doesn't work:

You can still manually export your filters and paste them into a text file for reference when reviewing the AI-generated rules.

**Manual export:**
1. Login to MailCow webmail
2. Settings → Filters
3. Copy your filter script
4. Save to `output/manual_filters.txt`
5. Review alongside `output/generated.sieve`

## Future Enhancements

Planned features:
- [ ] Merge mode: Automatically merge with existing filters
- [ ] Update mode: Update existing rules instead of creating new ones
- [ ] Conflict detection: Warn about overlapping rules
- [ ] Filter optimization: Suggest simplifications to existing rules
- [ ] Version control: Track filter changes over time

---

**Note:** This feature is optional and backward-compatible. The system works perfectly fine without ManageSieve support!
