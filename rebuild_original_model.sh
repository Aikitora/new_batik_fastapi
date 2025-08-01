#!/bin/bash

echo "🎯 Rebuilding with original model loading (no fallback)..."

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
echo "✅ Using original model loading (no fallback)"

# Test model locally first
echo "🧪 Testing model locally..."
python test_model_weights.py

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.nginx.yml down 2>/dev/null || true
docker-compose -f docker-compose.simple.yml down 2>/dev/null || true

# Remove old images and containers
echo "🧹 Cleaning up old images and containers..."
docker rmi batik-deploy_batik-api 2>/dev/null || true
docker system prune -f

# Rebuild and start
echo "🚀 Rebuilding and starting containers with original model..."
if [ -f "letsencrypt/live/batik-fast-api.sgp.dom.my.id/fullchain.pem" ]; then
    echo "Using nginx configuration with SSL..."
    docker-compose -f docker-compose.nginx.yml up --build -d
else
    echo "Using simple configuration without SSL..."
    docker-compose -f docker-compose.simple.yml up --build -d
fi

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 45

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

echo "✅ Original model rebuild complete!"
echo "🎯 Your API should now use the original trained model"
echo "🔧 To view logs:"
if [ -f "letsencrypt/live/batik-fast-api.sgp.dom.my.id/fullchain.pem" ]; then
    echo "  docker-compose -f docker-compose.nginx.yml logs -f"
else
    echo "  docker-compose -f docker-compose.simple.yml logs -f"
fi 