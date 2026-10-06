#!/bin/bash
#SBATCH --job-name=DToR_Branch
#SBATCH --partition=yuxinchen-contrib
#SBATCH --gres=gpu:a40:4
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=4:00:00                     # 4 hours for one branch
#SBATCH --output=dtor_branch_%j.out
#SBATCH --error=dtor_branch_%j.err
#SBATCH --mem=450G
#SBATCH --exclusive

source ~/.bashrc

# Ollama environment variables
export OLLAMA_LOAD_TIMEOUT=60m
export OLLAMA_HOST=127.0.0.1:21485

# Proxy settings for localhost
export no_proxy="localhost,127.0.0.1,::1"
export NO_PROXY="localhost,127.0.0.1,::1"

# Ollama one-CUDA-backend fix
OLLAMA_BIN="$(command -v ollama)"
OLLAMA_HOME="$(realpath "$(dirname "$OLLAMA_BIN")/..")"
export OLLAMA_CONTEXT_LENGTH=131072
GGML_ROOT="$OLLAMA_HOME/lib/ollama"
for d in "$GGML_ROOT"/cuda_v{11,12}; do [ -f "$d/libggml-cuda.so" ] && mv -n "$d/libggml-cuda.so" "$d/libggml-cuda.so.disabled" || true; done
export LD_LIBRARY_PATH="$GGML_ROOT:${LD_LIBRARY_PATH:-}"
export OLLAMA_LIBRARY_PATH="$GGML_ROOT"
export OLLAMA_KEEP_ALIVE=-1
ulimit -n 1048575

# Start Ollama service
ollama serve &
sleep 30

source /opt/conda/etc/profile.d/conda.sh
conda activate /net/projects/yuxinlab/dtor_DR_agent_env
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Get arguments
TOPIC_FILE="$1"
BRANCH_ID="$2"

if [ -z "$TOPIC_FILE" ] || [ -z "$BRANCH_ID" ]; then
    echo "Error: Usage: $0 <topic_file> <branch_id>"
    exit 1
fi

# Generate run ID
RUN_ID=$(basename "$TOPIC_FILE" .txt \
    | tr '[:upper:]' '[:lower:]' \
    | tr -cs 'a-z0-9-' '-' \
    | sed 's/^-//; s/-$//')

echo "========================================="
echo "DToR Stage 2: Branch Execution"
echo "Topic: $TOPIC_FILE"
echo "Run ID: $RUN_ID"
echo "Branch ID: $BRANCH_ID"
echo "Time: $(date)"
echo "========================================="

# Log branch start time
TIMING_LOG="synthesis_branches_and_final/${RUN_ID}/timing.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Stage 2 Branch $BRANCH_ID started (SLURM Job: $SLURM_JOB_ID)" >> "$TIMING_LOG"

# Check if this branch is already complete (check both possible locations)
SYNTHESIS_DIR="synthesis_branches_and_final/${RUN_ID}"
TOPIC_BASED_DIR="synthesis_branches_and_final/$(basename "$TOPIC_FILE" .txt)"

if ls ${SYNTHESIS_DIR}/branch_${BRANCH_ID}_*.md 2>/dev/null | grep -q . || \
   ls ${TOPIC_BASED_DIR}/branch_${BRANCH_ID:0:8}_*.md 2>/dev/null | grep -q .; then
    echo "Branch $BRANCH_ID already completed, skipping."
    exit 0
fi

# Get thread_id from perspectives file or generate it
PERSPECTIVES_FILE="cluster_checkpoints/${RUN_ID}/perspectives.json"
if [ -f "$PERSPECTIVES_FILE" ]; then
    # Extract thread_id from perspectives.json
    thread_id=$(python -c "import json; data=json.load(open('$PERSPECTIVES_FILE')); print(data.get('thread_id', 'research_default'))")
else
    # Fallback: generate from topic (should match Stage 1 logic)
    thread_id="research_$(echo -n "$(head -1 $TOPIC_FILE)" | md5sum | cut -c1-6)"
fi

# Set environment variables for branch execution
export TARGET_BRANCH_ID="$BRANCH_ID"
export ONE_BRANCH_PER_JOB=true
export PERSPECTIVES_FILE="cluster_checkpoints/${RUN_ID}/perspectives.json"

# Check perspectives file exists
if [ ! -f "$PERSPECTIVES_FILE" ]; then
    echo "ERROR: Perspectives file not found at $PERSPECTIVES_FILE"
    echo "Stage 1 must complete before Stage 2 can run"
    exit 1
fi

echo "Using perspectives from $PERSPECTIVES_FILE"
echo "Target branch: $BRANCH_ID"

# Run using the existing run_batch_cluster.py with DToR mode
# Use fixed run-id (branch_BRANCH_ID) to ensure consistent checkpoint paths across serial jobs
python dtor_orchestration/run_batch_cluster.py "$TOPIC_FILE" \
    -c research_mode dtor \
    -c nodes_per_branch 100 \
    -c max_branch_depth 3 \
    -c max_branches 3 \
    --run-id "branch_${BRANCH_ID}" \
    --checkpoint-dir "cluster_checkpoints/${RUN_ID}" \
    --output-dir "synthesis_branches_and_final/${RUN_ID}"

# Log branch end time
END_TIME=$(date '+%Y-%m-%d %H:%M:%S')
echo "[${END_TIME}] Stage 2 Branch $BRANCH_ID ended (SLURM Job: $SLURM_JOB_ID)" >> "$TIMING_LOG"

echo "Branch $BRANCH_ID execution complete"
