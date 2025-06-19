# Use a more complete base image
FROM python:3.13-slim-bullseye

# Set working directory
WORKDIR /app

# Install SSL certs and basic build tools
RUN apt-get update && apt-get install -y \
    ca-certificates \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
