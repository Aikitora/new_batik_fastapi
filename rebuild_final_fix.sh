#!/bin/bash

echo "🔧 Final rebuild with dependency conflict resolution..."

# Check if model file exists
if [ ! -f "final_tuned_genetic_algorithm_model.keras" ]; then
    echo "❌ Error: Model file not found in current directory"
    echo "Please ensure final_tuned_genetic_algorithm_model.keras is in the current directory"
    exit 1
fi

if [ ! -f "labels.txt" ]; then
    echo "❌ Error: Labels file not found in current directory"
    echo "Please ensure labels.txt is in the current directory"
    exit 1
fi

echo "✅ Model file found: $(ls -lh final_tuned_genetic_algorithm_model.keras)"
echo "✅ Labels file found: $(ls -lh labels.txt)"
echo "✅ Using compatible package versions"

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.nginx.yml down 2>/dev/null || true
docker-compose -f docker-compose.simple.yml down 2>/dev/null || true

# Remove old images and containers
echo "🧹 Cleaning up old images and containers..."
docker rmi batik-deploy_batik-api 2>/dev/null || true
docker system prune -f

# Create a temporary Dockerfile with pip install fix
echo "🔧 Creating temporary Dockerfile with pip install fix..."
cat > Dockerfile.temp << 'EOF'
# Use Python 3.10 slim image for better type hint support
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with conflict resolution
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --no-deps -r requirements.txt && \
    pip install --no-cache-dir typing-extensions==4.4.0 && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .
COPY labels.txt .
COPY final_tuned_genetic_algorithm_model.keras .

# Create a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Replace the original Dockerfile
mv Dockerfile.temp Dockerfile

# Rebuild and start
echo "🚀 Rebuilding and starting containers with dependency fix..."
if [ -f "letsencrypt/live/batik-fast-api.sgp.dom.my.id/fullchain.pem" ]; then
    echo "Using nginx configuration with SSL..."
    docker-compose -f docker-compose.nginx.yml up --build -d
else
    echo "Using simple configuration without SSL..."
    docker-compose -f docker-compose.simple.yml up --build -d
fi

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check service status
echo "🔍 Checking service status..."
if [ -f "letsencrypt/live/batik-fast-api.sgp.dom.my.id/fullchain.pem" ]; then
    docker-compose -f docker-compose.nginx.yml ps
else
    docker-compose -f docker-compose.simple.yml ps
fi

# Test the API
echo "🧪 Testing API endpoints..."
if [ -f "letsencrypt/live/batik-fast-api.sgp.dom.my.id/fullchain.pem" ]; then
    echo "Testing health endpoint..."
    curl -k https://batik-fast-api.sgp.dom.my.id/health
    echo ""
    echo "Testing debug endpoint..."
    curl -k https://batik-fast-api.sgp.dom.my.id/debug
else
    echo "Testing health endpoint..."
    curl http://localhost:8000/health
    echo ""
    echo "Testing debug endpoint..."
    curl http://localhost:8000/debug
fi
echo ""

echo "✅ Final rebuild complete with dependency conflict resolution!"
echo "🎯 Your API should now work on both local and server environments"
echo "🔧 To view logs:"
if [ -f "letsencrypt/live/batik-fast-api.sgp.dom.my.id/fullchain.pem" ]; then
    echo "  docker-compose -f docker-compose.nginx.yml logs -f"
else
    echo "  docker-compose -f docker-compose.simple.yml logs -f"
fi 