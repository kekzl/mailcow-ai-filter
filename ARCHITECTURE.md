# MailCow AI Filter - Architecture

## Overview

MailCow AI Filter is built using **Hexagonal Architecture** (Ports & Adapters) with **Domain-Driven Design** principles. This ensures clean separation of concerns, testability, and flexibility.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Primary Adapters                        │
│  (CLI, Web, API) - User interaction layer                   │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                  Application Layer                          │
│  - Use Cases (AnalyzeEmailsUseCase)                         │
│  - DTOs (Request/Response objects)                          │
│  - Ports (Interfaces for adapters)                          │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                    Domain Layer                             │
│  - Entities (Email, SieveFilter)                            │
│  - Value Objects (EmailAddress, EmailCluster, etc.)         │
│  - Domain Services (FilterGenerator, PatternDetector)       │
└─────────────────────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                 Secondary Adapters                          │
│  - IMAPAdapter (Email fetching)                             │
│  - OllamaAdapter (LLM analysis)                             │
│  - SentenceTransformerAdapter (Embeddings)                  │
│  - HDBSCANClusteringAdapter (ML clustering)                 │
│  - SieveFileAdapter (Rule generation)                       │
└─────────────────────────────────────────────────────────────┘
```

## Three Analysis Modes

The system supports three distinct analysis modes with different performance characteristics:

### 1. Embedding-Based Clustering (Recommended for 1000+ emails)

**Performance**: 10-50x faster than hierarchical mode

**Architecture**:
```
IMAP → Emails → SentenceTransformer → Embeddings
                      ↓
              HDBSCAN Clustering → Clusters
                      ↓
              Ollama (Master LLM) → Categories
                      ↓
              FilterGenerator → Sieve Rules
```

**Components**:
- `SentenceTransformerAdapter`: Generates semantic embeddings using `all-MiniLM-L6-v2`
- `HDBSCANClusteringAdapter`: Clusters similar emails using density-based algorithm
- `OllamaAdapter.analyze_clusters()`: Master LLM labels each cluster
- `FilterGenerator`: Converts categories to Sieve rules

**Speed**: ~100-200 emails/second (CPU-bound, embedding generation)

**When to use**: Large mailboxes (1000-5000+ emails), fastest mode

### 2. Hierarchical Two-Tier (Recommended for 100-1000 emails)

**Performance**: 2-5x faster than simple mode

**Architecture**:
```
IMAP → Emails → Worker LLM (parallel) → Summaries
                      ↓
              Master LLM → Categories
                      ↓
              FilterGenerator → Sieve Rules
```

**Components**:
- `OllamaEmailSummarizer`: Fast worker model (e.g., `gemma2:2b`) summarizes each email in parallel
- `OllamaAdapter.analyze_summaries()`: Master model (e.g., `qwen3:14b`) analyzes all summaries
- `FilterGenerator`: Converts categories to Sieve rules

**Speed**: ~10-30 emails/second (depends on LLM speed and parallelization)

**When to use**: Medium mailboxes (100-1000 emails), good balance of speed and accuracy

### 3. Simple Direct Analysis (Legacy)

**Performance**: Baseline

**Architecture**:
```
IMAP → Sample of Emails → LLM → Categories → Sieve Rules
```

**Components**:
- `OllamaAdapter.analyze_emails()`: Single LLM call on email sample
- `FilterGenerator`: Converts categories to Sieve rules

**Speed**: ~5-10 emails/second

**When to use**: Small mailboxes (<100 emails), testing, or using expensive cloud APIs

## Key Components

### Application Layer

#### `AnalyzeEmailsUseCase`
Main orchestrator that:
1. Fetches existing folder structure from IMAP server
2. Fetches emails from mailbox
3. Routes to appropriate analysis mode (embedding/hierarchical/simple)
4. Generates and saves Sieve filter rules

**New Feature**: Now fetches existing folder structure and passes it to LLM for context-aware categorization.

### Domain Layer

#### Entities
- `Email`: Core email entity with sender, recipients, subject, body, folder
- `SieveFilter`: Collection of filter rules

#### Value Objects
- `EmailAddress`: Email address with validation
- `EmailCluster`: Group of similar emails with representatives
- `EmailSummary`: Structured summary from worker LLM
- `EmailPattern`: Detected pattern (sender domain, subject keywords)
- `FilterRule`: Individual Sieve rule with conditions and actions

#### Domain Services
- `FilterGenerator`: Converts AI analysis to Sieve rules
- `PatternDetector`: Detects patterns in email clusters

### Infrastructure Layer

#### Secondary Adapters

**`IMAPAdapter`** (implements `IEmailFetcher`)
- Connects to IMAP server
- Fetches emails with filtering
- **New**: `list_folders()` and `get_folder_count()` for folder structure

**`OllamaAdapter`** (implements `ILLMService`)
- Communicates with local Ollama server
- Supports three analysis methods:
  - `analyze_emails()`: Simple mode
  - `analyze_summaries()`: Hierarchical mode
  - `analyze_clusters()`: Embedding mode
- **Improved**: Prompts now include existing folder structure and better hierarchical naming guidelines

**`SentenceTransformerAdapter`** (implements `IEmbeddingService`)
- Generates semantic embeddings using SentenceTransformers
- Model: `all-MiniLM-L6-v2` (384 dimensions)
- Efficient CPU/GPU support

**`HDBSCANClusteringAdapter`** (implements `IClusteringService`)
- Density-based clustering algorithm
- Automatically determines number of clusters
- Handles noise (uncategorized emails)

**`OllamaEmailSummarizer`** (implements `IEmailSummarizer`)
- Parallel batch summarization
- Uses fast worker model (e.g., `gemma2:2b`)
- Structured JSON output

**`SieveFileAdapter`** (implements `IFilterRepository`)
- Generates Sieve script syntax
- Handles hierarchical folder names (Parent/Child)
- Creates fileinto rules with pattern matching

## Configuration

The system uses a layered configuration approach:

1. **`config/config.yml`**: Main configuration file (gitignored)
2. **`.env`**: Environment variable overrides (gitignored)
3. **Dependency Injection**: `Container` class wires up dependencies

### Mode Selection Logic

```python
# Priority: Embedding > Hierarchical > Simple
if embedding_service and clustering_service:
    mode = "embedding"
elif email_summarizer:
    mode = "hierarchical"
else:
    mode = "simple"
```

## Performance Characteristics

### Embedding Mode
- **Emails/second**: 100-200 (CPU: i7-10700K)
- **Memory**: ~500MB for 5000 emails
- **Bottleneck**: Embedding generation (CPU)
- **Scalability**: Linear with email count

### Hierarchical Mode
- **Emails/second**: 10-30 (depends on LLM)
- **Memory**: ~300MB for 1000 emails
- **Bottleneck**: LLM inference speed
- **Scalability**: Linear with parallelization

### Simple Mode
- **Emails/second**: 5-10
- **Memory**: ~100MB for 100 emails
- **Bottleneck**: LLM context window
- **Scalability**: Limited by sample size

## Recent Improvements

### Task 1: Existing Folder Structure Awareness
- `AnalyzeEmailsUseCase` now fetches folder structure before analysis
- Passes folder names and email counts to LLM
- LLM can respect existing structure and suggest improvements

### Task 2: Increased Email Capacity
- `max_emails_to_analyze` increased from 2000 to 5000
- Enables processing of larger mailboxes
- Optimized for embedding mode performance

### Task 3: Enhanced Prompts
- Added hierarchical folder structure guidelines (Parent/Child format)
- Included examples of good vs bad folder naming
- More detailed pattern matching instructions
- Better handling of existing folder structure

### Task 4: Code Cleanup
- Removed 7 unused legacy files
- Cleaned up old backup files
- Removed pre-DDD architecture code

### Task 5: Improved .gitignore
- Comprehensive Python patterns
- Virtual environment exclusions
- Test and coverage directories
- OS-specific files

## Testing

Test structure follows the hexagonal architecture:

```
tests/
├── unit/           # Unit tests for domain logic
│   ├── domain/
│   ├── application/
│   └── infrastructure/
├── integration/    # Integration tests for adapters
└── e2e/           # End-to-end workflow tests
```

## Future Enhancements

1. **Incremental Updates**: Only analyze new emails since last run
2. **Active Learning**: Learn from user corrections to improve patterns
3. **Multi-Account Support**: Analyze multiple mailboxes simultaneously
4. **Web UI**: Interactive interface for reviewing and editing rules
5. **Rule Testing**: Simulate rules against email sample before deployment
6. **Custom Embeddings**: Fine-tune embeddings on user's email corpus

## Dependencies

### Core
- Python 3.10+
- imaplib (IMAP protocol)

### LLM Integration
- ollama (local LLM server)
- anthropic (optional, for Claude API)

### ML/Embedding Mode
- sentence-transformers (embeddings)
- hdbscan (clustering)
- numpy, scipy (numerical operations)

### Development
- pytest (testing)
- black (code formatting)
- mypy (type checking)

## Contributing

See [HEXAGONAL_ARCHITECTURE.md](HEXAGONAL_ARCHITECTURE.md) for detailed architecture patterns and best practices.

## License

MIT License - See LICENSE file
