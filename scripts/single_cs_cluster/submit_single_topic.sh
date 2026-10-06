#!/bin/bash
#SBATCH --job-name=SingleDR
#SBATCH --partition=yuxinchen-contrib
#SBATCH --gres=gpu:a40:4
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=01:00:00
#SBATCH --output=logs/single_topic_%j.out
#SBATCH --error=logs/single_topic_%j.err
#SBATCH --mem=450G
#SBATCH --exclusive

# ============================================================================
# Single Topic Research Job - For Parallel Execution
# This script runs ONE topic in single mode
# ============================================================================

# Get topic file from argument
TOPIC_FILE="$1"

if [ -z "$TOPIC_FILE" ]; then
    echo "Error: No topic file provided"
    echo "Usage: sbatch submit_single_topic.sh <topic_file>"
    exit 1
fi

if [ ! -f "$TOPIC_FILE" ]; then
    echo "Error: Topic file not found: $TOPIC_FILE"
    exit 1
fi

# Extract topic name for display
TOPIC_NAME=$(basename "$TOPIC_FILE" .txt)

echo "=================================================="
echo "Single Topic Deep Research Job"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURMD_NODENAME"
echo "Topic File: $TOPIC_FILE"
echo "Topic Name: $TOPIC_NAME"
echo "Start time: $(date)"
echo "=================================================="

# Create logs directory
mkdir -p logs

# Source bashrc
source ~/.bashrc

# Ollama environment variables
export OLLAMA_LOAD_TIMEOUT=60m
export OLLAMA_HOST=127.0.0.1:21485

# Proxy settings
export no_proxy="localhost,127.0.0.1,::1"
export NO_PROXY="localhost,127.0.0.1,::1"

# Ollama CUDA fix
OLLAMA_BIN="$(command -v ollama)"
OLLAMA_HOME="$(realpath "$(dirname "$OLLAMA_BIN")/..")"
export OLLAMA_CONTEXT_LENGTH=131072
GGML_ROOT="$OLLAMA_HOME/lib/ollama"
for d in "$GGML_ROOT"/cuda_v{11,12}; do [ -f "$d/libggml-cuda.so" ] && mv -n "$d/libggml-cuda.so" "$d/libggml-cuda.so.disabled" || true; done
export LD_LIBRARY_PATH="$GGML_ROOT:${LD_LIBRARY_PATH:-}"
export OLLAMA_LIBRARY_PATH="$GGML_ROOT"
export OLLAMA_KEEP_ALIVE=-1
ulimit -n 1048575

# Start Ollama
echo "Starting Ollama service..."
ollama serve &
sleep 30

# Activate conda environment
source /opt/conda/etc/profile.d/conda.sh
conda activate /net/projects/yuxinlab/tot_DR_agent_env
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
export PYTHONUNBUFFERED=1

# Load .env
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

echo ""
echo "Running research for: $TOPIC_NAME"
echo ""

# Run single topic research (no checkpointing - completes in 20-40 min)
python single_cs_cluster/run_single_topic.py "$TOPIC_FILE" \
    --output-dir Single_DR_final \
    --log-level INFO

# Capture exit code
EXIT_CODE=$?

echo ""
echo "=================================================="
echo "Job completed at: $(date)"
echo "Exit code: $EXIT_CODE"
echo "=================================================="

if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ Research completed successfully for: $TOPIC_NAME"
else
    echo "✗ Research failed for: $TOPIC_NAME"
fi

exit $EXIT_CODE
