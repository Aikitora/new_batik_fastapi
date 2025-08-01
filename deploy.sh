#!/bin/bash

echo "🚀 Deploying Batik API to production..."

# Check if domain is provided
DOMAIN="batik-fast-api.sgp.dom.my.id"
EMAIL="your-email@example.com"  # Change this to your email

echo "📍 Domain: $DOMAIN"
echo "📧 Email: $EMAIL"

# Create necessary directories
mkdir -p letsencrypt

# Check if SSL certificate exists
if [ ! -f "letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo "🔒 SSL certificate not found. Please obtain SSL certificate first."
    echo "You can use Let's Encrypt:"
    echo "sudo certbot certonly --standalone -d $DOMAIN --email $EMAIL"
    echo ""
    echo "Or use your hosting provider's SSL certificate."
    exit 1
fi

# Build and deploy with nginx
echo "🐳 Building and deploying with Docker Compose..."
docker-compose -f docker-compose.nginx.yml down
docker-compose -f docker-compose.nginx.yml up --build -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
docker-compose -f docker-compose.nginx.yml ps

# Test the API
echo "🧪 Testing API endpoints..."
curl -k https://$DOMAIN/health
echo ""

echo "✅ Deployment complete!"
echo "🌐 Your API is now available at: https://$DOMAIN"
echo "📚 API Documentation: https://$DOMAIN/docs"
echo "📖 ReDoc: https://$DOMAIN/redoc"
echo ""
echo "🔧 To view logs: docker-compose -f docker-compose.nginx.yml logs -f"
echo "🛑 To stop: docker-compose -f docker-compose.nginx.yml down" 