# 🚀 Production Deployment Guide

## 📋 Prerequisites

1. **Server Requirements:**
   - Ubuntu 20.04+ or CentOS 8+
   - Docker and Docker Compose installed
   - Domain name pointing to your server
   - SSL certificate (Let's Encrypt or your provider)

2. **Domain Setup:**
   - Point `batik-fast-api.sgp.dom.my.id` to your server IP
   - Wait for DNS propagation (can take up to 24 hours)

## 🔧 Server Setup

### 1. Install Docker and Docker Compose

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again for group changes
```

### 2. Upload Your Files

```bash
# Create project directory
mkdir -p /opt/batik-api
cd /opt/batik-api

# Upload your files to this directory:
# - main.py
# - requirements.txt
# - Dockerfile
# - docker-compose.nginx.yml
# - nginx.conf
# - final_tuned_genetic_algorithm_model.keras
# - deploy.sh
```

### 3. SSL Certificate Setup

#### Option A: Let's Encrypt (Recommended)

```bash
# Install certbot
sudo apt install certbot

# Get SSL certificate
sudo certbot certonly --standalone -d batik-fast-api.sgp.dom.my.id --email your-email@example.com

# Copy certificates to project directory
sudo cp -r /etc/letsencrypt/live/batik-fast-api.sgp.dom.my.id /opt/batik-api/letsencrypt/
sudo chown -R $USER:$USER /opt/batik-api/letsencrypt/
```

#### Option B: Your Hosting Provider's SSL

```bash
# Place your SSL certificates in the letsencrypt directory
mkdir -p letsencrypt/live/batik-fast-api.sgp.dom.my.id
# Copy your fullchain.pem and privkey.pem to this directory
```

## 🚀 Deployment Options

### Option 1: Simple Deployment (HTTP only)

```bash
# Deploy without SSL
docker-compose -f docker-compose.simple.yml up -d
```

### Option 2: Production Deployment with SSL

```bash
# Run the deployment script
./deploy.sh
```

### Option 3: Manual Deployment

```bash
# Build and start services
docker-compose -f docker-compose.nginx.yml up --build -d

# Check status
docker-compose -f docker-compose.nginx.yml ps

# View logs
docker-compose -f docker-compose.nginx.yml logs -f
```

## 🔍 Verification

### 1. Check Service Status

```bash
docker-compose -f docker-compose.nginx.yml ps
```

### 2. Test API Endpoints

```bash
# Health check
curl https://batik-fast-api.sgp.dom.my.id/health

# Model info
curl https://batik-fast-api.sgp.dom.my.id/model-info

# Test prediction (replace with actual image)
curl -X POST -F "file=@test_image.jpg" https://batik-fast-api.sgp.dom.my.id/predict
```

### 3. Check SSL Certificate

```bash
curl -I https://batik-fast-api.sgp.dom.my.id
```

## 📊 Monitoring

### 1. View Logs

```bash
# All services
docker-compose -f docker-compose.nginx.yml logs -f

# Specific service
docker-compose -f docker-compose.nginx.yml logs -f batik-api
docker-compose -f docker-compose.nginx.yml logs -f nginx
```

### 2. Resource Usage

```bash
# Check container resource usage
docker stats

# Check disk usage
df -h
```

### 3. Health Monitoring

```bash
# Set up monitoring script
cat > /opt/batik-api/monitor.sh << 'EOF'
#!/bin/bash
while true; do
    response=$(curl -s -o /dev/null -w "%{http_code}" https://batik-fast-api.sgp.dom.my.id/health)
    if [ "$response" != "200" ]; then
        echo "$(date): API health check failed - Status: $response"
        # Add notification logic here
    fi
    sleep 60
done
EOF

chmod +x /opt/batik-api/monitor.sh
nohup /opt/batik-api/monitor.sh > /dev/null 2>&1 &
```

## 🔧 Maintenance

### 1. Update Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.nginx.yml down
docker-compose -f docker-compose.nginx.yml up --build -d
```

### 2. SSL Certificate Renewal

```bash
# Let's Encrypt certificates expire every 90 days
# Add to crontab for automatic renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -

# Or renew manually
sudo certbot renew
sudo cp -r /etc/letsencrypt/live/batik-fast-api.sgp.dom.my.id /opt/batik-api/letsencrypt/
sudo chown -R $USER:$USER /opt/batik-api/letsencrypt/
docker-compose -f docker-compose.nginx.yml restart nginx
```

### 3. Backup

```bash
# Create backup script
cat > /opt/batik-api/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/batik-api"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup model file
cp final_tuned_genetic_algorithm_model.keras $BACKUP_DIR/model_$DATE.keras

# Backup configuration
tar -czf $BACKUP_DIR/config_$DATE.tar.gz *.yml *.conf *.py *.txt *.sh

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.keras" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /opt/batik-api/backup.sh

# Add to crontab for daily backup
echo "0 2 * * * /opt/batik-api/backup.sh" | crontab -
```

## 🛠️ Troubleshooting

### Common Issues

1. **SSL Certificate Issues:**
   ```bash
   # Check certificate validity
   openssl x509 -in letsencrypt/live/batik-fast-api.sgp.dom.my.id/fullchain.pem -text -noout
   
   # Renew certificate
   sudo certbot renew
   ```

2. **Port Conflicts:**
   ```bash
   # Check what's using port 80/443
   sudo netstat -tlnp | grep :80
   sudo netstat -tlnp | grep :443
   ```

3. **Model Loading Issues:**
   ```bash
   # Check model file permissions
   ls -la final_tuned_genetic_algorithm_model.keras
   
   # Check container logs
   docker-compose -f docker-compose.nginx.yml logs batik-api
   ```

4. **Memory Issues:**
   ```bash
   # Check memory usage
   free -h
   docker stats
   
   # Increase swap if needed
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

## 📈 Performance Optimization

### 1. Enable Gzip Compression

Add to nginx.conf:
```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
```

### 2. Increase Worker Processes

Add to nginx.conf:
```nginx
worker_processes auto;
worker_connections 1024;
```

### 3. Enable Caching

Add to nginx.conf:
```nginx
location /static/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## 🔐 Security Considerations

1. **Firewall Setup:**
   ```bash
   sudo ufw allow 22
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```

2. **Regular Updates:**
   ```bash
   # Update system packages
   sudo apt update && sudo apt upgrade -y
   
   # Update Docker images
   docker-compose -f docker-compose.nginx.yml pull
   ```

3. **Access Control:**
   - Consider adding authentication to your API
   - Use API keys for production access
   - Implement rate limiting

## 📞 Support

For production issues:
1. Check logs: `docker-compose -f docker-compose.nginx.yml logs -f`
2. Verify SSL: `curl -I https://batik-fast-api.sgp.dom.my.id`
3. Test API: `curl https://batik-fast-api.sgp.dom.my.id/health`
4. Check resources: `docker stats`

---

**Your API will be available at: https://batik-fast-api.sgp.dom.my.id** 