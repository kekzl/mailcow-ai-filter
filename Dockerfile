FROM python:3.11-slim

WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
    gcc \
    libxml2-dev \
    libxslt-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy requirements first for better caching
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Copy utility scripts
COPY fetch_existing_filters.py .
COPY create_folders.py .
COPY upload_filter_api.py .
COPY apply_filters_retroactive.py .

# Create output and logs directories
RUN mkdir -p /app/output /app/logs

ENV PYTHONUNBUFFERED=1

# Health check - verify Python and core dependencies are working
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from src.config import Config; print('OK')" || exit 1

CMD ["python", "-m", "src.main"]
