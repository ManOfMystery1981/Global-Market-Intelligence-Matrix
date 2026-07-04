FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Create output directories
RUN mkdir -p reports

# Expose Flask port
EXPOSE 5000

# Start Flask server
CMD ["python", "flask_server/server.py"]
