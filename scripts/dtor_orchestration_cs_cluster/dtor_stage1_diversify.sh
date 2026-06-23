#!/bin/bash
#SBATCH --job-name=DToR_Diversify
#SBATCH --partition=yuxinchen-contrib
#SBATCH --gres=gpu:a40:4
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=0:30:00                     # 30 minutes should be enough for diversify
#SBATCH --output=dtor_diversify_%j.out
#SBATCH --error=dtor_diversify_%j.err
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

# Load .env file if it exists
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Get topic file from argument
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
echo "DToR Stage 1: Diversify"
echo "Topic: $TOPIC_FILE"
echo "Run ID: $RUN_ID"
echo "Time: $(date)"
echo "========================================="

# Run the diversify-only script
python dtor_orchestration/run_diversify_only.py \
    --topics-file "$TOPIC_FILE" \
    --run-id "$RUN_ID" \
    --checkpoint-dir "cluster_checkpoints"

echo "Diversify stage complete"
