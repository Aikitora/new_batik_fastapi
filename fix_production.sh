#!/bin/bash

echo "🔧 Fixing production deployment issue..."

# Check if we're in the right directory
if [ ! -f "final_tuned_genetic_algorithm_model.keras" ]; then
    echo "❌ Error: Model file not found in current directory"
    echo "Please ensure final_tuned_genetic_algorithm_model.keras is in the current directory"
    exit 1
fi

echo "✅ Model file found: $(ls -lh final_tuned_genetic_algorithm_model.keras)"

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
else
    echo "⚠️ SSL certificate not found. Using HTTP deployment for now."
    echo "To get SSL certificate, run:"
    echo "sudo certbot certonly --standalone -d batik-fast-api.sgp.dom.my.id --email your-email@example.com"
    echo ""
    echo "Deploying with HTTP for now..."
    docker-compose -f docker-compose.simple.yml up --build -d
    echo "✅ Deployed with HTTP. API available at: http://batik-fast-api.sgp.dom.my.id"
    exit 0
fi

# Deploy with nginx and SSL
echo "🚀 Deploying with nginx and SSL..."
docker-compose -f docker-compose.nginx.yml up --build -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 15

# Check service status
echo "🔍 Checking service status..."
docker-compose -f docker-compose.nginx.yml ps

# Test the API
echo "🧪 Testing API endpoints..."
echo "Testing health endpoint..."
curl -k https://batik-fast-api.sgp.dom.my.id/health
echo ""

echo "Testing debug endpoint..."
curl -k https://batik-fast-api.sgp.dom.my.id/debug
echo ""

echo "✅ Deployment complete!"
echo "🌐 Your API is now available at: https://batik-fast-api.sgp.dom.my.id"
echo "📚 API Documentation: https://batik-fast-api.sgp.dom.my.id/docs"
echo "🔍 Debug info: https://batik-fast-api.sgp.dom.my.id/debug"
echo ""
echo "🔧 To view logs: docker-compose -f docker-compose.nginx.yml logs -f"
echo "🛑 To stop: docker-compose -f docker-compose.nginx.yml down" 