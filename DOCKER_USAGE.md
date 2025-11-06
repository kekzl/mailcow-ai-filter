# Docker Container Usage

**No Python venv needed!** Everything runs in Docker containers.

## Quick Start

### 1. Build the Container

```bash
./mailcow-filter.sh build
```

### 2. Run Email Analysis

```bash
./mailcow-filter.sh analyze
```

### 3. Create Folders & Upload Filter

```bash
./mailcow-filter.sh create-folders
./mailcow-filter.sh upload-filter
```

## Interactive Menu

Just run the script without arguments:

```bash
./mailcow-filter.sh
```

You'll see:

```
===============================================================================
MailCow AI Filter - Container Manager
===============================================================================

Main Operations:
  1) Analyze emails and generate filter
  2) Fetch existing Sieve filters
  3) Create mail folders (IMAP)
  4) Upload filter to MailCow (API)

Utilities:
  5) View generated filter
  6) View logs (tail -f)
  7) Build/rebuild container
  8) Clean up containers

  0) Exit

Select option:
```

## All Commands

### Main Operations

```bash
./mailcow-filter.sh analyze              # Analyze emails & generate filter
./mailcow-filter.sh fetch-filters        # Fetch existing Sieve filters
./mailcow-filter.sh create-folders       # Create mail folders via IMAP
./mailcow-filter.sh upload-filter        # Upload filter via MailCow API
```

### Utilities

```bash
./mailcow-filter.sh view-filter          # View generated filter
./mailcow-filter.sh logs                 # Tail logs
./mailcow-filter.sh build                # Build/rebuild container
./mailcow-filter.sh clean                # Clean up containers
```

### Help

```bash
./mailcow-filter.sh help                 # Show help
```

## Complete Workflow Example

```bash
# 1. Build container (first time only)
./mailcow-filter.sh build

# 2. Configure (edit config.yml with your credentials)
nano config/config.yml

# 3. Run analysis
./mailcow-filter.sh analyze

# 4. Review generated filter
./mailcow-filter.sh view-filter

# 5. Create folders
./mailcow-filter.sh create-folders

# 6. Upload filter
./mailcow-filter.sh upload-filter

# Done!
```

## What Happens Inside the Container?

### analyze
- Connects to your IMAP server
- Fetches up to 2000 emails
- Generates embeddings (ML)
- Clusters similar emails
- Uses AI (Ollama) to label clusters
- Generates Sieve filter rules
- Saves to `output/generated.sieve`

### fetch-filters
- Connects to ManageSieve (port 4190)
- Fetches your existing Sieve script
- Parses filter rules
- Saves to `output/existing_filters.txt`

### create-folders
- Reads `output/generated.sieve`
- Extracts all folder paths
- Asks for your permission
- Creates folders via IMAP

### upload-filter
- Reads `output/generated.sieve`
- Asks for MailCow API key
- Uploads via MailCow REST API
- Activates filter on server

## File Locations

All files are mounted from your host:

```
Host Path                          Container Path
---------------------------------  ----------------------
./config/config.yml       →        /app/config/config.yml
./output/generated.sieve  →        /app/output/generated.sieve
./logs/ai-filter.log      →        /app/logs/ai-filter.log
./.env                    →        /app/.env
```

## Configuration

Edit `config/config.yml`:

```yaml
protocol: "imap"

imap:
  server: "mail.kekz.org"
  username: "kekz@kekz.org"
  password: "your-password"
  use_ssl: true
  port: 993

ai:
  provider: "ollama"
  master_model: "qwen2.5-coder:14b"
  base_url: "http://localhost:11434"
  use_embedding: true
  max_emails_to_analyze: 2000
```

## Networking

The container uses `network_mode: host` to access:
- Your mail server (IMAP/ManageSieve)
- Ollama on localhost:11434

This is safe for a batch job that runs and exits.

## Troubleshooting

### Container build fails

```bash
# Check Docker is running
docker ps

# Rebuild from scratch
./mailcow-filter.sh clean
./mailcow-filter.sh build
```

### Can't connect to Ollama

Make sure Ollama is running on the host:

```bash
curl http://localhost:11434/api/tags
```

If not running:

```bash
ollama serve
```

### Permission denied on output files

```bash
# Fix ownership
sudo chown -R $USER:$USER output/ logs/
```

### View container logs

```bash
docker-compose logs -f
```

## Advanced Usage

### Run custom command in container

```bash
docker run --rm -it \
  -v ./config:/app/config:ro \
  -v ./output:/app/output \
  --network host \
  mailcow-ai-filter:latest \
  python -c "print('Hello from container!')"
```

### Debug container

```bash
docker run --rm -it \
  -v ./config:/app/config:ro \
  -v ./output:/app/output \
  --network host \
  mailcow-ai-filter:latest \
  /bin/bash
```

### Update container after code changes

```bash
./mailcow-filter.sh build
```

No need to rebuild for config changes - they're mounted!

## Performance

**Container overhead:** ~1-2 seconds startup
**Analysis time:** ~90-120 seconds for 1500 emails

The container uses the same local Ollama instance as your host, so ML performance is identical to running directly.

## Security

### What's accessible from the container:

✅ config/config.yml (read-only)
✅ .env file (read-only)
✅ Your IMAP server (via host network)
✅ Ollama on localhost (via host network)
✅ output/ directory (read-write)
✅ logs/ directory (read-write)

❌ No access to other files on your system
❌ Container runs as regular user (not root)
❌ Container exits after running (no persistent process)

## Why Use Containers?

✅ **No venv needed** - Dependencies isolated in container
✅ **Clean environment** - Fresh Python environment every time
✅ **Reproducible** - Works the same everywhere
✅ **Easy updates** - Just rebuild container
✅ **No conflicts** - Won't interfere with system Python

## When NOT to Use Containers

If you need to:
- Debug Python code with breakpoints
- Make frequent code changes
- Use Python REPL interactively

For development, use venv. For production, use containers.

---

**Questions?** Check the main README.md or open an issue!
