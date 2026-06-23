#!/bin/bash
# ============================================================================
# Parallel Topic Submission Manager
# Submits ALL topics in research_topics/ as independent SLURM jobs
# Maximum parallelization - one job per topic
# ============================================================================

TOPICS_DIR="${1:-research_topics}"

if [ ! -d "$TOPICS_DIR" ]; then
    echo "Error: Topics directory not found: $TOPICS_DIR"
    echo "Usage: bash submit_all_topics_parallel.sh [topics_dir]"
    exit 1
fi

echo "========================================="
echo "Parallel Topic Submission Manager"
echo "Topics directory: $TOPICS_DIR"
echo "Time: $(date)"
echo "========================================="
echo ""

# Create logs directory
mkdir -p logs

# Count topics
TOPIC_COUNT=$(ls -1 "$TOPICS_DIR"/*.txt 2>/dev/null | wc -l)

if [ $TOPIC_COUNT -eq 0 ]; then
    echo "Error: No .txt files found in $TOPICS_DIR"
    exit 1
fi

echo "Found $TOPIC_COUNT topics to submit"
echo ""

# Track submitted jobs
SUBMITTED_COUNT=0
FAILED_COUNT=0
declare -a JOB_IDS
declare -a TOPIC_NAMES

# Submit each topic as independent job
for TOPIC_FILE in "$TOPICS_DIR"/*.txt; do
    TOPIC_NAME=$(basename "$TOPIC_FILE" .txt)

    echo "Submitting: $TOPIC_NAME"

    # Submit job and capture job ID
    JOB_ID=$(sbatch --parsable --job-name="SingleDR_${TOPIC_NAME:0:20}" single_cs_cluster/submit_single_topic.sh "$TOPIC_FILE" 2>&1)

    if [ $? -eq 0 ]; then
        echo "  ✓ Job ID: $JOB_ID"
        JOB_IDS+=("$JOB_ID")
        TOPIC_NAMES+=("$TOPIC_NAME")
        ((SUBMITTED_COUNT++))
    else
        echo "  ✗ Failed to submit: $JOB_ID"
        ((FAILED_COUNT++))
    fi
done

echo ""
echo "========================================="
echo "Submission Summary"
echo "========================================="
echo "Total topics: $TOPIC_COUNT"
echo "Successfully submitted: $SUBMITTED_COUNT"
echo "Failed: $FAILED_COUNT"
echo ""

if [ $SUBMITTED_COUNT -gt 0 ]; then
    echo "Submitted Job IDs:"
    for i in "${!JOB_IDS[@]}"; do
        printf "  %-8s - %s\n" "${JOB_IDS[$i]}" "${TOPIC_NAMES[$i]}"
    done
    echo ""

    # Save job tracking info
    TRACKING_FILE="parallel_jobs_$(date +%Y%m%d_%H%M%S).txt"
    echo "# Parallel Single Mode Jobs - $(date)" > "$TRACKING_FILE"
    echo "# Job_ID | Topic_Name" >> "$TRACKING_FILE"
    for i in "${!JOB_IDS[@]}"; do
        echo "${JOB_IDS[$i]} | ${TOPIC_NAMES[$i]}" >> "$TRACKING_FILE"
    done
    echo ""
    echo "Job tracking saved to: $TRACKING_FILE"
    echo ""

    # Provide monitoring commands
    echo "========================================="
    echo "Monitoring Commands"
    echo "========================================="
    echo ""
    echo "# Check all jobs:"
    echo "squeue -u \$USER"
    echo ""
    echo "# Count running jobs:"
    echo "squeue -u \$USER | grep SingleDR | wc -l"
    echo ""
    echo "# Check completed reports:"
    echo "ls Single_DR_final/*/report_*.md | wc -l"
    echo ""
    echo "# Monitor all logs:"
    echo "tail -f logs/single_topic_*.out"
    echo ""
    echo "# Check for failures:"
    echo "grep -l '✗ FAILED' logs/single_topic_*.out"
    echo ""
    echo "========================================="
fi

echo ""
echo "All submissions complete!"

exit 0
