# 🔧 Troubleshooting Production Deployment

## 🚨 Current Issue: "Model not loaded" (503 Error)

### Quick Fix Steps:

1. **Check if you're on the production server:**
   ```bash
   # SSH into your production server
   ssh user@your-server-ip
   ```

2. **Navigate to the project directory:**
   ```bash
   cd /opt/batik-api  # or wherever you deployed the files
   ```

3. **Run the fix script:**
   ```bash
   ./fix_production.sh
   ```

4. **If the fix script doesn't work, try manual steps:**
   ```bash
   # Stop all containers
   docker-compose -f docker-compose.nginx.yml down
   docker-compose -f docker-compose.simple.yml down
   
   # Remove old images
   docker rmi batik-deploy_batik-api 2>/dev/null || true
   
   # Deploy with simple configuration first
   docker-compose -f docker-compose.simple.yml up --build -d
   
   # Check logs
   docker-compose -f docker-compose.simple.yml logs -f
   ```

## 🔍 Diagnostic Steps

### 1. Check Model File
```bash
# Verify model file exists and has correct size
ls -lh final_tuned_genetic_algorithm_model.keras

# Should show: -rw-r--r-- 1 user user 12M date final_tuned_genetic_algorithm_model.keras
```

### 2. Check Docker Containers
```bash
# List running containers
docker ps

# Check container logs
docker-compose -f docker-compose.nginx.yml logs batik-api
```

### 3. Test API Endpoints
```bash
# Test health endpoint
curl -k https://batik-fast-api.sgp.dom.my.id/health

# Test debug endpoint (new)
curl -k https://batik-fast-api.sgp.dom.my.id/debug
```

### 4. Check File Permissions
```bash
# Ensure model file is readable
chmod 644 final_tuned_genetic_algorithm_model.keras

# Check ownership
ls -la final_tuned_genetic_algorithm_model.keras
```

## 🐳 Docker-Specific Issues

### Issue 1: Model file not found in container
**Symptoms:** `Model file not found: final_tuned_genetic_algorithm_model.keras`

**Solution:**
```bash
# Check if model file is in the right location
ls -la final_tuned_genetic_algorithm_model.keras

# If not, copy it to the project directory
cp /path/to/your/model.keras ./final_tuned_genetic_algorithm_model.keras

# Rebuild and restart
docker-compose -f docker-compose.nginx.yml down
docker-compose -f docker-compose.nginx.yml up --build -d
```

### Issue 2: Permission denied
**Symptoms:** `Permission denied` in container logs

**Solution:**
```bash
# Fix file permissions
chmod 644 final_tuned_genetic_algorithm_model.keras
chown 1000:1000 final_tuned_genetic_algorithm_model.keras

# Restart containers
docker-compose -f docker-compose.nginx.yml restart
```

### Issue 3: Memory issues
**Symptoms:** Container crashes or model loading fails

**Solution:**
```bash
# Check available memory
free -h

# Increase Docker memory limit
# Edit /etc/docker/daemon.json
sudo nano /etc/docker/daemon.json
# Add: {"default-shm-size": "2G"}
sudo systemctl restart docker

# Or increase swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 🔧 Manual Deployment Steps

### Step 1: Prepare Files
```bash
# Create project directory
mkdir -p /opt/batik-api
cd /opt/batik-api

# Upload all files:
# - main.py (updated version)
# - requirements.txt
# - Dockerfile
# - docker-compose.nginx.yml
# - nginx.conf
# - final_tuned_genetic_algorithm_model.keras
# - fix_production.sh
```

### Step 2: Set Permissions
```bash
# Make scripts executable
chmod +x fix_production.sh
chmod +x deploy.sh

# Set model file permissions
chmod 644 final_tuned_genetic_algorithm_model.keras
```

### Step 3: Deploy
```bash
# Option A: Use fix script
./fix_production.sh

# Option B: Manual deployment
docker-compose -f docker-compose.nginx.yml up --build -d
```

### Step 4: Verify
```bash
# Check container status
docker-compose -f docker-compose.nginx.yml ps

# Check logs
docker-compose -f docker-compose.nginx.yml logs -f

# Test API
curl -k https://batik-fast-api.sgp.dom.my.id/health
curl -k https://batik-fast-api.sgp.dom.my.id/debug
```

## 🚨 Emergency Fixes

### If SSL certificate is missing:
```bash
# Deploy without SSL temporarily
docker-compose -f docker-compose.simple.yml up --build -d

# Get SSL certificate
sudo certbot certonly --standalone -d batik-fast-api.sgp.dom.my.id --email your-email@example.com

# Copy certificates
sudo cp -r /etc/letsencrypt/live/batik-fast-api.sgp.dom.my.id /opt/batik-api/letsencrypt/
sudo chown -R $USER:$USER /opt/batik-api/letsencrypt/

# Deploy with SSL
docker-compose -f docker-compose.simple.yml down
docker-compose -f docker-compose.nginx.yml up --build -d
```

### If Docker is not installed:
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again
```

## 📊 Monitoring Commands

### Check API Status:
```bash
# Health check
curl -s https://batik-fast-api.sgp.dom.my.id/health | python -m json.tool

# Debug info
curl -s https://batik-fast-api.sgp.dom.my.id/debug | python -m json.tool

# Model info
curl -s https://batik-fast-api.sgp.dom.my.id/model-info | python -m json.tool
```

### Check Container Status:
```bash
# List containers
docker ps

# Check resource usage
docker stats

# View logs
docker-compose -f docker-compose.nginx.yml logs -f
```

### Check System Resources:
```bash
# Memory usage
free -h

# Disk usage
df -h

# CPU usage
top
```

## 🔄 Recovery Procedures

### Complete Reset:
```bash
# Stop everything
docker-compose -f docker-compose.nginx.yml down
docker-compose -f docker-compose.simple.yml down

# Remove all images
docker rmi $(docker images -q) 2>/dev/null || true

# Clean up
docker system prune -f

# Redeploy
./fix_production.sh
```

### Model File Issues:
```bash
# Verify model file integrity
file final_tuned_genetic_algorithm_model.keras

# Check file size
ls -lh final_tuned_genetic_algorithm_model.keras

# If file is corrupted, re-upload it
# Then restart containers
docker-compose -f docker-compose.nginx.yml restart
```

## 📞 Support Information

### Debug Information to Collect:
1. **Container logs:** `docker-compose -f docker-compose.nginx.yml logs`
2. **Debug endpoint:** `curl -k https://batik-fast-api.sgp.dom.my.id/debug`
3. **System info:** `uname -a && docker --version`
4. **File permissions:** `ls -la final_tuned_genetic_algorithm_model.keras`

### Common Error Messages:
- `Model file not found`: File missing or wrong path
- `Permission denied`: File permission issues
- `Memory error`: Insufficient memory
- `SSL certificate error`: SSL configuration issues

---

**Remember:** The updated `main.py` includes better error reporting and a `/debug` endpoint to help diagnose issues! 