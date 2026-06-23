#!/bin/bash
#SBATCH --job-name=deep_research_multisensor
#SBATCH --partition=yuxinchen-contrib      # Partition name
#SBATCH --gres=gpu:a40:4                   # Request 4 GPUs
#SBATCH --nodes=1                          # Request 1 node
#SBATCH --ntasks=1                         # Total number of tasks
#SBATCH --cpus-per-task=32                 # CPU cores per task
#SBATCH --time=4:00:00                     # Maximum runtime
#SBATCH --output=deep_research_%j.out
#SBATCH --error=deep_research_%j.err
#SBATCH --mem=150G                         # Request 150GB memory
#SBATCH --exclusive

source ~/.bashrc

# Ollama environment variables
export OLLAMA_LOAD_TIMEOUT=60m
export OLLAMA_HOST=127.0.0.1:21485

# Proxy settings for localhost
export no_proxy="localhost,127.0.0.1,::1"
export NO_PROXY="localhost,127.0.0.1,::1"  # Both cases for compatibility

# --- Ollama one-CUDA-backend fix (generic) ---
OLLAMA_BIN="$(command -v ollama)"
OLLAMA_HOME="$(realpath "$(dirname "$OLLAMA_BIN")/..")"
GGML_ROOT="$OLLAMA_HOME/lib/ollama"
for d in "$GGML_ROOT"/cuda_v{11,12}; do [ -f "$d/libggml-cuda.so" ] && mv -n "$d/libggml-cuda.so" "$d/libggml-cuda.so.disabled" || true; done
export LD_LIBRARY_PATH="$GGML_ROOT:${LD_LIBRARY_PATH:-}"
export OLLAMA_LIBRARY_PATH="$GGML_ROOT"  # 明确只用顶层
export OLLAMA_KEEP_ALIVE=-1
ulimit -n 1048575
# --- end fix ---


# Start Ollama service in the background
ollama serve &

# Wait for Ollama to start
sleep 30

source /opt/conda/etc/profile.d/conda.sh

conda activate /net/projects/yuxinlab/dtor_DR_agent_env

# Add src to Python path so it can find ollama_deep_researcher
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Run the cluster batch script
python dtor_orchestration/run_batch_cluster.py --topics-file research_topics.txt --wall-time 3.83
