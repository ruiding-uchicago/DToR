# Use Python 3.11 (meets >=3.9 requirement)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first for better caching
COPY pyproject.toml README.md ./

# Copy source code
COPY src/ ./src/

# Install the package and dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -e '.[ui]'

# # Install Phoenix and Chainlit dependencies (if not already in pyproject.toml)
# RUN pip install --no-cache-dir \
#     arize-phoenix \
#     openinference-instrumentation-langchain \
#     chainlit>=2.0.0

# Create directories for checkpoints, output, and logs
RUN mkdir -p /app/checkpoints /app/output /app/logs

# Set environment variables with defaults
ENV USE_LOCAL_RAG=false
ENV PYTHONUNBUFFERED=1
ENV CHAINLIT_HOST=0.0.0.0
ENV CHAINLIT_PORT=8000
ENV PHOENIX_ENABLED=false
ENV PHOENIX_HOST=0.0.0.0
ENV PHOENIX_PORT=6006

# Expose ports
# 8000 for Chainlit UI
# 6006 for Phoenix UI
# 4317 for OpenTelemetry gRPC (Phoenix collector)
# 4318 for OpenTelemetry HTTP (Phoenix collector)
EXPOSE 8000 6006 4317 4318

# Default command runs Chainlit
# Phoenix should be started separately or via docker-compose
CMD ["chainlit", "run", "src/ollama_deep_researcher/chainlit_app.py", "--host", "0.0.0.0", "--port", "8000"]
