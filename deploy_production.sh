#!/bin/bash

echo "🚀 Deploying Batik API to Production..."

# Check if we're in the right directory
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

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.nginx.yml down 2>/dev/null || true
docker-compose -f docker-compose.simple.yml down 2>/dev/null || true

# Remove old images
echo "🧹 Cleaning up old images..."
docker rmi batik-deploy_batik-api 2>/dev/null || true

# Create letsencrypt directory if it doesn't exist
mkdir -p letsencrypt

# Check SSL certificate
if [ -f "letsencrypt/live/batik-fast-api.sgp.dom.my.id/fullchain.pem" ]; then
    echo "✅ SSL certificate found"
    echo "🚀 Deploying with nginx and SSL..."
    docker-compose -f docker-compose.nginx.yml up --build -d
else
    echo "⚠️ SSL certificate not found. Using HTTP deployment for now."
    echo "To get SSL certificate, run:"
    echo "sudo certbot certonly --standalone -d batik-fast-api.sgp.dom.my.id --email your-email@example.com"
    echo ""
    echo "Deploying with HTTP for now..."
    docker-compose -f docker-compose.simple.yml up --build -d
fi

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 15

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

echo "✅ Deployment complete!"
if [ -f "letsencrypt/live/batik-fast-api.sgp.dom.my.id/fullchain.pem" ]; then
    echo "🌐 Your API is now available at: https://batik-fast-api.sgp.dom.my.id"
    echo "📚 API Documentation: https://batik-fast-api.sgp.dom.my.id/docs"
    echo "🔍 Debug info: https://batik-fast-api.sgp.dom.my.id/debug"
else
    echo "🌐 Your API is now available at: http://localhost:8000"
    echo "📚 API Documentation: http://localhost:8000/docs"
    echo "🔍 Debug info: http://localhost:8000/debug"
fi
echo ""
echo "🔧 To view logs:"
if [ -f "letsencrypt/live/batik-fast-api.sgp.dom.my.id/fullchain.pem" ]; then
    echo "  docker-compose -f docker-compose.nginx.yml logs -f"
    echo "🛑 To stop: docker-compose -f docker-compose.nginx.yml down"
else
    echo "  docker-compose -f docker-compose.simple.yml logs -f"
    echo "🛑 To stop: docker-compose -f docker-compose.simple.yml down"
fi 