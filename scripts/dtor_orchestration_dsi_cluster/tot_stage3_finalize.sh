#!/bin/bash
#SBATCH --job-name=DToR_Final
#SBATCH --partition=ai+s
#SBATCH --gres=gpu:4
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=1:00:00                     # 1 hour for final synthesis
#SBATCH --output=dtor_final_%j.out
#SBATCH --error=dtor_final_%j.err
#SBATCH --mem=450G

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

eval "$(conda shell.bash hook)"
conda activate /net/scratch/ruiding/tot_DR_agent_env
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Load .env file if it exists
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Get topic file
TOPIC_FILE="$1"
if [ -z "$TOPIC_FILE" ]; then
    echo "Error: No topic file provided"
    exit 1
fi

# Generate run ID
RUN_ID=$(basename "$TOPIC_FILE" .txt \
    | tr '[:upper:]' '[:lower:]' \
    | tr -cs 'a-z0-9-' '-' \
    | sed 's/^-//; s/-$//')

echo "========================================="
echo "DToR Stage 3: Final Synthesis"
echo "Topic: $TOPIC_FILE"
echo "Run ID: $RUN_ID"
echo "Time: $(date)"
echo "========================================="

# Check if final synthesis already exists
SYNTHESIS_DIR="synthesis_branches_and_final/${RUN_ID}"
if [ -f "${SYNTHESIS_DIR}/final_synthesis.md" ]; then
    echo "Final synthesis already exists, skipping."
    exit 0
fi

# Count completed branches (check both possible locations)
# Stage 2 creates directory with full path (replace / with _) but truncates to 50 chars
FULL_DIR_NAME=$(echo "$TOPIC_FILE" | sed 's/\.txt$//' | tr '/' '_')
ACTUAL_SYNTHESIS_DIR="synthesis_branches_and_final/${FULL_DIR_NAME:0:50}"
# Also check with _txt suffix for edge cases
DIR_NAME_WITH_TXT="${FULL_DIR_NAME}_txt"
ACTUAL_SYNTHESIS_DIR_TXT="synthesis_branches_and_final/${DIR_NAME_WITH_TXT:0:50}"
BRANCH_COUNT=$(ls ${SYNTHESIS_DIR}/branch_*.md ${ACTUAL_SYNTHESIS_DIR}/branch_*.md ${ACTUAL_SYNTHESIS_DIR_TXT}/branch_*.md 2>/dev/null | wc -l)
echo "Found $BRANCH_COUNT completed branches"

if [ "$BRANCH_COUNT" -lt 3 ]; then
    echo "Warning: Only $BRANCH_COUNT/3 branches completed"
    echo "Proceeding anyway..."
fi

# Run the final synthesis Python script
python dtor_orchestration_dsi_cluster/tot_final_synthesis.py \
    --topic-file "$TOPIC_FILE" \
    --run-id "$RUN_ID" \
    --synthesis-dir "synthesis_branches_and_final"

echo "Final synthesis complete"