#!/bin/bash
# Smart ToT Manager - Automatically detects current stage and submits appropriate jobs
# Usage: bash tot_smart_manager.sh <topic_file> [chain_count]
#   chain_count: Number of serial jobs per branch (default: 3)

TOPIC_FILE="$1"
CHAIN_COUNT="${2:-3}"  # Default to 3 serial jobs per branch

if [ -z "$TOPIC_FILE" ]; then
    echo "Usage: $0 <topic_file> [chain_count]"
    echo "  chain_count: Number of serial jobs per branch (default: 3)"
    exit 1
fi

# Generate run ID from topic file
RUN_ID=$(basename "$TOPIC_FILE" .txt | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9-' '-' | sed 's/^-//; s/-$//')

CHECKPOINT_DIR="cluster_checkpoints/${RUN_ID}"
SYNTHESIS_DIR="synthesis_branches_and_final/${RUN_ID}"
PERSPECTIVES_FILE="${CHECKPOINT_DIR}/perspectives.json"
TIMING_LOG="${SYNTHESIS_DIR}/timing.log"

# Create synthesis dir if needed for timing log
mkdir -p "$SYNTHESIS_DIR"

# Function to log timing
log_timing() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$TIMING_LOG"
}

echo "========================================="
echo "DToR Smart Manager"
echo "Topic: $TOPIC_FILE"
echo "Run ID: $RUN_ID"
echo "Chain Count: $CHAIN_COUNT serial jobs per branch"
echo "========================================="

# Log initial run if this is the first time
if [ ! -f "$TIMING_LOG" ]; then
    log_timing "DToR run started for $TOPIC_FILE"
fi

# Function to check if job is running/pending
check_job_running() {
    local job_name=$1
    squeue -u $USER --name="$job_name" --noheader | wc -l
}

# Function to get unique job name suffix (first 8 chars of RUN_ID)
get_job_suffix() {
    echo "${RUN_ID:0:8}"
}

# Stage 1: Check if diversification is done
if [ ! -f "$PERSPECTIVES_FILE" ]; then
    echo "Stage 1: Diversification not found"

    # Check if Stage 1 job is already running (with unique suffix)
    JOB_SUFFIX=$(get_job_suffix)
    if [ $(check_job_running "DToR_Div_${JOB_SUFFIX}") -gt 0 ]; then
        echo "  Stage 1 job already running/pending for this topic"
    else
        echo "  Submitting Stage 1: Diversification"
        JOB_ID=$(sbatch --parsable --job-name="DToR_Div_${JOB_SUFFIX}" dtor_orchestration_dsi_cluster/tot_stage1_diversify.sh "$TOPIC_FILE")
        echo "  Submitted Stage 1 with Job ID: $JOB_ID"
        log_timing "Stage 1 submitted (Job ID: $JOB_ID)"
    fi
    echo "  Run this script again after Stage 1 completes"
    exit 0
fi

echo "✓ Stage 1 completed: Diversification found"
log_timing "Stage 1 completed"

# Read perspectives to get branch IDs
if command -v jq &> /dev/null; then
    BRANCH_IDS=$(jq -r '.perspectives[].id' "$PERSPECTIVES_FILE")
    BRANCH_COUNT=$(jq '.perspectives | length' "$PERSPECTIVES_FILE")
else
    # Fallback to grep/sed if jq not available
    BRANCH_IDS=$(grep -o '"id": *"[^"]*"' "$PERSPECTIVES_FILE" | sed 's/.*"id": *"\([^"]*\)".*/\1/')
    BRANCH_COUNT=$(echo "$BRANCH_IDS" | wc -l)
fi

echo "  Found $BRANCH_COUNT branches: $(echo $BRANCH_IDS | tr '\n' ' ')"

# Stage 2: Check branch completion and submit missing ones
COMPLETED_BRANCHES=0
RUNNING_BRANCHES=0
NEED_SUBMISSION=""

# Check both possible locations for branch synthesis files
# Stage 2 creates directory with full path (replace / with _) but truncates to 50 chars
FULL_DIR_NAME=$(echo "$TOPIC_FILE" | sed 's/\.txt$//' | tr '/' '_')
# Truncate to first 50 characters to match actual truncation behavior
ACTUAL_SYNTHESIS_DIR="synthesis_branches_and_final/${FULL_DIR_NAME:0:50}"

for BRANCH_ID in $BRANCH_IDS; do
    # Check if branch synthesis exists (try both locations)
    # Note: synthesis files only use first 8 chars of branch ID
    SHORT_ID=${BRANCH_ID:0:8}

    # Also check with _txt suffix for edge cases
    DIR_NAME_WITH_TXT="${FULL_DIR_NAME}_txt"
    ACTUAL_SYNTHESIS_DIR_TXT="synthesis_branches_and_final/${DIR_NAME_WITH_TXT:0:50}"  # Truncate directory name to 50 chars

    echo "  DEBUG: Checking branch $BRANCH_ID (short: $SHORT_ID)"
    echo "    - Checking dir 1: ${SYNTHESIS_DIR}"
    echo "    - Pattern: branch_${SHORT_ID}_*.md"
    echo "    - Find result: $(find ${SYNTHESIS_DIR} -maxdepth 1 -name "branch_${SHORT_ID}_*.md" 2>/dev/null)"

    echo "    - Checking dir 2: ${ACTUAL_SYNTHESIS_DIR}"
    echo "    - Pattern: branch_${SHORT_ID}_*.md"
    echo "    - Find result: $(find ${ACTUAL_SYNTHESIS_DIR} -maxdepth 1 -name "branch_${SHORT_ID}_*.md" 2>/dev/null)"

    echo "    - Checking dir 3: ${ACTUAL_SYNTHESIS_DIR_TXT}"
    echo "    - Pattern: branch_${SHORT_ID}_*.md"
    echo "    - Find result: $(find ${ACTUAL_SYNTHESIS_DIR_TXT} -maxdepth 1 -name "branch_${SHORT_ID}_*.md" 2>/dev/null)"

    # Use find instead of ls for more reliable file existence check
    FOUND=0
    if [ -n "$(find ${SYNTHESIS_DIR} -maxdepth 1 -name "branch_${SHORT_ID}_*.md" 2>/dev/null)" ] || \
       [ -n "$(find ${ACTUAL_SYNTHESIS_DIR} -maxdepth 1 -name "branch_${SHORT_ID}_*.md" 2>/dev/null)" ] || \
       [ -n "$(find ${ACTUAL_SYNTHESIS_DIR_TXT} -maxdepth 1 -name "branch_${SHORT_ID}_*.md" 2>/dev/null)" ]; then
        FOUND=1
    fi

    if [ $FOUND -eq 1 ]; then
        echo "✓ Branch $BRANCH_ID completed"
        # Log completion if not already logged
        if ! grep -q "Stage 2 Branch $BRANCH_ID completed" "$TIMING_LOG" 2>/dev/null; then
            log_timing "Stage 2 Branch $BRANCH_ID completed"
        fi
        ((COMPLETED_BRANCHES++))
    else
        echo "✗ Branch $BRANCH_ID not completed"
        NEED_SUBMISSION="$NEED_SUBMISSION $BRANCH_ID"
    fi
done

# Check if any branch jobs are running (with unique suffix)
JOB_SUFFIX=$(get_job_suffix)
BRANCH_JOBS_RUNNING=$(check_job_running "DToR_Br_${JOB_SUFFIX}")
if [ $BRANCH_JOBS_RUNNING -gt 0 ]; then
    echo "⚡ Found $BRANCH_JOBS_RUNNING branch job(s) running"
    RUNNING_BRANCHES=$BRANCH_JOBS_RUNNING
fi

# Submit missing branches with serial chain
if [ -n "$NEED_SUBMISSION" ]; then
    echo ""
    echo "Stage 2: Submitting missing branches (${CHAIN_COUNT} serial jobs each)..."
    JOB_SUFFIX=$(get_job_suffix)
    for BRANCH_ID in $NEED_SUBMISSION; do
        # Submit first job with unique name
        JOB_ID1=$(sbatch --parsable --job-name="DToR_Br_${JOB_SUFFIX}" dtor_orchestration_dsi_cluster/tot_stage2_branch.sh "$TOPIC_FILE" "$BRANCH_ID")
        echo "  Branch $BRANCH_ID job 1/${CHAIN_COUNT}: Job ID $JOB_ID1"
        log_timing "Stage 2 Branch $BRANCH_ID job 1/${CHAIN_COUNT} submitted (Job ID: $JOB_ID1)"

        # Submit remaining chained jobs
        PREV_JOB=$JOB_ID1
        for i in $(seq 2 $CHAIN_COUNT); do
            JOB_ID=$(sbatch --parsable --job-name="DToR_Br_${JOB_SUFFIX}" --dependency=afterany:$PREV_JOB dtor_orchestration_dsi_cluster/tot_stage2_branch.sh "$TOPIC_FILE" "$BRANCH_ID")
            echo "  Branch $BRANCH_ID job ${i}/${CHAIN_COUNT}: Job ID $JOB_ID (after $PREV_JOB)"
            log_timing "Stage 2 Branch $BRANCH_ID job ${i}/${CHAIN_COUNT} submitted (Job ID: $JOB_ID, dependency: $PREV_JOB)"
            PREV_JOB=$JOB_ID
        done
    done
    echo ""
    echo "  Submitted ${CHAIN_COUNT} serial jobs for each branch"
    echo "  Total jobs: $(echo "$NEED_SUBMISSION" | wc -w) branches × ${CHAIN_COUNT} = $(($(echo "$NEED_SUBMISSION" | wc -w) * CHAIN_COUNT))"
    echo "  Run this script again after branches complete"
    exit 0
fi

if [ $RUNNING_BRANCHES -gt 0 ]; then
    echo ""
    echo "Stage 2: $RUNNING_BRANCHES branch job(s) still running"
    echo "  Run this script again after they complete"
    exit 0
fi

echo "✓ Stage 2 completed: All branches done"
log_timing "Stage 2 completed (all branches done)"

# Stage 3: Check if final synthesis exists
if [ -f "${SYNTHESIS_DIR}/final_synthesis.md" ]; then
    echo "✓ Stage 3 completed: Final synthesis exists"
    log_timing "Stage 3 completed - ALL DONE"
    echo ""
    echo "========================================="
    echo "✅ ALL STAGES COMPLETE!"
    echo "Final report: ${SYNTHESIS_DIR}/final_synthesis.md"
    echo "Timing log: ${TIMING_LOG}"
    echo "========================================="
    exit 0
fi

# Check if Stage 3 job is running (with unique suffix)
JOB_SUFFIX=$(get_job_suffix)
if [ $(check_job_running "DToR_Fin_${JOB_SUFFIX}") -gt 0 ]; then
    echo "⚡ Stage 3 job already running/pending"
    echo "  Run this script again after it completes"
    exit 0
fi

# Submit Stage 3
echo ""
echo "Stage 3: Submitting final synthesis..."
JOB_ID=$(sbatch --parsable --job-name="DToR_Fin_${JOB_SUFFIX}" dtor_orchestration_dsi_cluster/tot_stage3_finalize.sh "$TOPIC_FILE")
echo "  Submitted Stage 3 with Job ID: $JOB_ID"
log_timing "Stage 3 submitted (Job ID: $JOB_ID)"
echo "  Run this script again after Stage 3 completes"

echo ""
echo "Current Status Summary:"
echo "  Stage 1 (Diversify): ✓ Complete"
echo "  Stage 2 (Branches):  ✓ Complete ($COMPLETED_BRANCHES/$BRANCH_COUNT)"
echo "  Stage 3 (Synthesis): ⚡ Submitted"