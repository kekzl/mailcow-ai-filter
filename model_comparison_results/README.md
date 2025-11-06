# Model Comparison Test Results

This directory contains the results of comprehensive testing of three different LLM models for Sieve filter generation.

## Test Date
2025-11-06

## Models Tested
1. **qwen3:14b** (baseline) - General-purpose model
2. **qwen2.5-coder:14b** (winner) - Code-specialized model
3. **deepseek-r1:14b** - Reasoning-focused model

## Winner: qwen2.5-coder:14b ⭐

- 11% faster than baseline
- 19% more Sieve rules generated
- 10x better hierarchical categorization
- Optimized for structured code output

## Files

### Report
- `COMPARISON_REPORT.md` - Comprehensive analysis and recommendation

### Test Results (per model)
- `{model}_rules.sieve` - Generated Sieve filter rules
- `{model}_output.log` - Full test execution log
- `{model}_summary.txt` - Performance metrics summary

## Quick Comparison

| Model | Duration | Rules | Categories |
|-------|----------|-------|------------|
| qwen3:14b | 597s | 26 | 1 |
| **qwen2.5-coder:14b** | **532s** | **31** | **10** |
| deepseek-r1:14b | 524s | 22 | 1 |

## Recommendation

Update `config/config.yml` to use qwen2.5-coder:14b:

```yaml
ai:
  master_model: "qwen2.5-coder:14b"
```

## Test Script

Run comparison tests again:
```bash
./test_models.sh
```

## Dataset

- 1,568 emails from INBOX
- 178 clusters (HDBSCAN + BAAI/bge-large-en-v1.5 embeddings)
- Configuration: Temperature 0.7, Max tokens 10,000
