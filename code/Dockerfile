# Multi-stage build for FastAPI application

# Build stage for dependencies
FROM python:3.12-slim AS builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /code

# Copy requirements first for better caching
COPY _requirements/ /code/_requirements/

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /code/_requirements/main.txt

# Production stage
FROM python:3.12-slim AS production

# Install only runtime system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r qurtesy && useradd -r -g qurtesy qurtesy

# Set working directory
WORKDIR /code

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . /code

# Create necessary directories and set permissions
RUN mkdir -p /code/db_dump /code/statements && \
    chown -R qurtesy:qurtesy /code

# Switch to non-root user
USER qurtesy

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8085/docs')" || exit 1

# Expose port
EXPOSE 8085

# Start application with optimized settings for production
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8085", "--workers", "4", "--access-log"]

# Development stage
FROM builder AS development

# Install development dependencies
RUN pip install --no-cache-dir -r /code/_requirements/dev.txt

# Copy application code
COPY . /code

# Expose port
EXPOSE 8085

# Start application with hot reloading for development
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8085", "--reload", "--log-level", "debug"]
