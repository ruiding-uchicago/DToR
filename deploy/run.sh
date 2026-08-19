#!/usr/bin/env bash
# Start DToR (Chainlit UI). Phoenix is optional: ./deploy/run.sh --with-phoenix
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f deploy/.env ] || { echo "missing deploy/.env  (cp deploy/env.example deploy/.env)"; exit 1; }
set -a; . deploy/.env; set +a
: "${OPENAI_API_KEY:?set OPENAI_API_KEY in deploy/.env}"

export PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}"
export LLM_PROVIDER=openai
export OPENAI_MODEL="${OPENAI_MODEL:-gpt-5.6-luna}"
export STRIP_THINKING_TOKENS=True
export USE_LOCAL_RAG=false ENABLE_FET_RAW_DATA=false \
       ENABLE_CODE_RETRIEVAL=false ENABLE_PAPER_RETRIEVAL=false
export SEARCH_API="${SEARCH_API:-tavily}" FETCH_FULL_PAGE="${FETCH_FULL_PAGE:-False}"
export RESEARCH_MODE=dtor
export MAX_BRANCHES="${MAX_BRANCHES:-3}" MAX_BRANCH_DEPTH="${MAX_BRANCH_DEPTH:-2}"
export MAX_WEB_RESEARCH_LOOPS="${MAX_WEB_RESEARCH_LOOPS:-2}" NODES_PER_BRANCH="${NODES_PER_BRANCH:-20}"
mkdir -p logs output

if [ "${1:-}" = "--with-phoenix" ]; then
  PXBIN=".venv-phoenix/bin/phoenix"
  [ -x "$PXBIN" ] || { echo "phoenix venv missing — see deploy/README.md step 3"; exit 1; }
  if ! curl -sf "http://127.0.0.1:${PHOENIX_PORT:-6006}/" >/dev/null 2>&1; then
    PHOENIX_WORKING_DIR="$PWD/.phoenix-data" nohup "$PXBIN" serve >logs/phoenix.log 2>&1 &
    for _ in $(seq 60); do
      curl -sf "http://127.0.0.1:${PHOENIX_PORT:-6006}/" >/dev/null 2>&1 && break; sleep 1
    done
  fi
  export PHOENIX_ENABLED=true PHOENIX_HOST=127.0.0.1 \
         PHOENIX_PORT="${PHOENIX_PORT:-6006}" PHOENIX_PROJECT_NAME="${PHOENIX_PROJECT_NAME:-dtor}"
  echo "phoenix  -> http://127.0.0.1:${PHOENIX_PORT:-6006}"
else
  export PHOENIX_ENABLED=false
fi

echo "chainlit -> http://${CHAINLIT_HOST:-127.0.0.1}:${CHAINLIT_PORT:-8000}  (model=$OPENAI_MODEL, mode=dtor)"
exec chainlit run src/ollama_deep_researcher/chainlit_app.py \
     --host "${CHAINLIT_HOST:-127.0.0.1}" --port "${CHAINLIT_PORT:-8000}"
