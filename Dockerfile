FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Copy utility scripts
COPY fetch_existing_filters.py .
COPY create_folders.py .
COPY upload_filter_api.py .

# Create output directory for generated rules
RUN mkdir -p /app/output

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "src.main"]
