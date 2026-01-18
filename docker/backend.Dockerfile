FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install libraries as editable packages
COPY libs/intelligence-scraper /app/libs/intelligence-scraper
COPY libs/intelligence-analyzer /app/libs/intelligence-analyzer
RUN pip install -e /app/libs/intelligence-scraper
RUN pip install -e /app/libs/intelligence-analyzer

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy backend source
COPY backend/src /app/src

# Create logs directory
RUN mkdir -p /app/logs

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
