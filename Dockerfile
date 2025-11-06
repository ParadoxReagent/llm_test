# Multi-stage build for LLM Compare
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements-lock.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements-lock.txt

# Final stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY llm_compare/ ./llm_compare/
COPY models.py .
COPY pyproject.toml .

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Install the package in editable mode
RUN pip install --no-cache-dir -e .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LITELLM_API_KEY=""

# Create a non-root user (optional, for better security)
RUN useradd -m -u 1000 llmuser && \
    chown -R llmuser:llmuser /app

USER llmuser

# Default command
ENTRYPOINT ["llm-compare"]
CMD ["--help"]
