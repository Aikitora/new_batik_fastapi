#!/bin/bash

echo "🏭 Production rebuild with detailed model validation..."

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

# Test model locally first
echo "🧪 Testing model locally before deployment..."
python test_model_weights.py

if [ $? -ne 0 ]; then
    echo "❌ Local model test failed! Aborting deployment."
    exit 1
fi

echo "✅ Local model test passed!"

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.nginx.yml down 2>/dev/null || true
docker-compose -f docker-compose.simple.yml down 2>/dev/null || true

# Remove old images and containers
echo "🧹 Cleaning up old images and containers..."
docker rmi batik-deploy_batik-api 2>/dev/null || true
docker system prune -f

# Rebuild and start
echo "🚀 Rebuilding and starting containers for production..."
if [ -f "letsencrypt/live/batik-fast-api.sgp.dom.my.id/fullchain.pem" ]; then
    echo "Using nginx configuration with SSL..."
    docker-compose -f docker-compose.nginx.yml up --build -d
else
    echo "Using simple configuration without SSL..."
    docker-compose -f docker-compose.simple.yml up --build -d
fi

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 60

# Check service status
echo "🔍 Checking service status..."
if [ -f "letsencrypt/live/batik-fast-api.sgp.dom.my.id/fullchain.pem" ]; then
    docker-compose -f docker-compose.nginx.yml ps
else
    docker-compose -f docker-compose.simple.yml ps
fi

# Test the API with detailed logging
echo "🧪 Testing API endpoints with detailed validation..."

# Test health endpoint
echo "📋 Testing health endpoint..."
if [ -f "letsencrypt/live/batik-fast-api.sgp.dom.my.id/fullchain.pem" ]; then
    HEALTH_RESPONSE=$(curl -s -k https://batik-fast-api.sgp.dom.my.id/health)
else
    HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
fi

echo "📋 Health response: $HEALTH_RESPONSE"

# Test debug endpoint
echo "📋 Testing debug endpoint..."
if [ -f "letsencrypt/live/batik-fast-api.sgp.dom.my.id/fullchain.pem" ]; then
    DEBUG_RESPONSE=$(curl -s -k https://batik-fast-api.sgp.dom.my.id/debug)
else
    DEBUG_RESPONSE=$(curl -s http://localhost:8000/debug)
fi

echo "📋 Debug response: $DEBUG_RESPONSE"

# Test model info endpoint
echo "📋 Testing model info endpoint..."
if [ -f "letsencrypt/live/batik-fast-api.sgp.dom.my.id/fullchain.pem" ]; then
    MODEL_INFO_RESPONSE=$(curl -s -k https://batik-fast-api.sgp.dom.my.id/model-info)
else
    MODEL_INFO_RESPONSE=$(curl -s http://localhost:8000/model-info)
fi

echo "📋 Model info response: $MODEL_INFO_RESPONSE"

echo ""
echo "✅ Production rebuild complete with detailed validation!"
echo "🎯 Your API should now use the original trained model"
echo "🔧 To view logs:"
if [ -f "letsencrypt/live/batik-fast-api.sgp.dom.my.id/fullchain.pem" ]; then
    echo "  docker-compose -f docker-compose.nginx.yml logs -f"
else
    echo "  docker-compose -f docker-compose.simple.yml logs -f"
fi

echo ""
echo "📋 Next steps:"
echo "1. Check the logs above for any model loading errors"
echo "2. Test a prediction to verify the model is working"
echo "3. If still using fallback, check the container logs for detailed error messages" 