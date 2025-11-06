#!/bin/bash
# Model Comparison Test Script
# Tests qwen3:14b vs qwen2.5-coder:14b vs deepseek-r1:14b

set -e

MODELS=("qwen3:14b" "qwen2.5-coder:14b" "deepseek-r1:14b")
RESULTS_DIR="./model_comparison_results"

mkdir -p "$RESULTS_DIR"

echo "========================================"
echo "Model Comparison Test for Sieve Filters"
echo "========================================"
echo ""

for MODEL in "${MODELS[@]}"; do
    echo "Testing model: $MODEL"

    # Check if model is installed
    if ! ollama list | grep -q "$MODEL"; then
        echo "  ⚠️  Model not installed. Run: ollama pull $MODEL"
        continue
    fi

    # Update config with this model
    sed -i.bak "s/master_model: .*/master_model: \"$MODEL\"/" config/config.yml

    echo "  ⏱️  Starting analysis..."
    START_TIME=$(date +%s)

    # Run analysis
    if docker compose up > "$RESULTS_DIR/${MODEL//:/\_}_output.log" 2>&1; then
        END_TIME=$(date +%s)
        DURATION=$((END_TIME - START_TIME))

        # Extract metrics
        CATEGORIES=$(grep "Identified:" "$RESULTS_DIR/${MODEL//:/\_}_output.log" | awk '{print $2}')
        RULES=$(grep "Generated:" "$RESULTS_DIR/${MODEL//:/\_}_output.log" | grep "rules" | awk '{print $6}')

        echo "  ✅ Success!"
        echo "     Duration: ${DURATION}s"
        echo "     Categories: $CATEGORIES"
        echo "     Rules: $RULES"

        # Copy output
        cp output/generated.sieve "$RESULTS_DIR/${MODEL//:/\_}_rules.sieve"

        # Save summary
        cat > "$RESULTS_DIR/${MODEL//:/\_}_summary.txt" << EOF
Model: $MODEL
Duration: ${DURATION}s
Categories: $CATEGORIES
Rules: $RULES
Output: ${MODEL//:/\_}_rules.sieve
Log: ${MODEL//:/\_}_output.log
EOF
    else
        echo "  ❌ Failed - check log: $RESULTS_DIR/${MODEL//:/\_}_output.log"
    fi

    echo ""
done

# Restore original config
mv config/config.yml.bak config/config.yml

echo "========================================"
echo "Comparison Complete!"
echo "Results saved to: $RESULTS_DIR/"
echo ""
echo "Compare results:"
echo "  cat $RESULTS_DIR/*_summary.txt"
echo ""
echo "Compare generated rules:"
echo "  diff $RESULTS_DIR/qwen3_14b_rules.sieve $RESULTS_DIR/qwen2.5-coder_14b_rules.sieve"
echo "========================================"
