# Use Python 3.11 (meets >=3.9 requirement)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies that might be needed
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
    pip install --no-cache-dir -e .

# Create directories for checkpoints and output
RUN mkdir -p /app/output

# Set environment variables with defaults
ENV USE_LOCAL_RAG=false
ENV PYTHONUNBUFFERED=1

# Default command runs the CLI with help
ENTRYPOINT ["python", "src/ollama_deep_researcher/dtor_cli.py"]
CMD ["--help"]
