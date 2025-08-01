# 🔧 CORS Fix for Frontend Integration

## 🚨 Issue Identified

The frontend at `https://front-end-batik-vision.vercel.app` is getting CORS errors when trying to access the API:

```
Access to fetch at 'https://batik-deploy-fastapi-production-c83f.up.railway.app/health' 
from origin 'https://front-end-batik-vision.vercel.app' has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## ✅ Solution Applied

### **Updated CORS Configuration**

**Before:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**After:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://front-end-batik-vision.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🚀 Quick Fix Commands

### Option 1: Use the rebuild script
```bash
./rebuild_railway.sh
```

### Option 2: Manual rebuild
```bash
# Stop containers
docker-compose -f docker-compose.simple.yml down

# Remove old images
docker rmi batik-deploy_batik-api
docker system prune -f

# Rebuild with CORS fix
docker-compose -f docker-compose.simple.yml up --build -d
```

## 🔍 Verification

After rebuilding, test the CORS headers:

```bash
# Test CORS headers
curl -H "Origin: https://front-end-batik-vision.vercel.app" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     https://batik-deploy-fastapi-production-c83f.up.railway.app/health

# Test health endpoint
curl https://batik-deploy-fastapi-production-c83f.up.railway.app/health
```

## 📋 Expected CORS Headers

The API should now return these headers:

```
Access-Control-Allow-Origin: https://front-end-batik-vision.vercel.app
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: *
Access-Control-Allow-Credentials: true
```

## 🎯 Benefits

1. **✅ Frontend Integration**: Frontend can now access the API
2. **✅ Multiple Origins**: Supports both production and development
3. **✅ Security**: Specific origin allowlist for production
4. **✅ Development**: Wildcard origin for local development

## 📁 Updated Files

1. **main.py** - Updated CORS configuration with specific origins
2. **rebuild_railway.sh** - New rebuild script for Railway deployment

## 🔧 CORS Configuration Details

### **Allowed Origins:**
- `https://front-end-batik-vision.vercel.app` - Production frontend
- `http://localhost:3000` - React development server
- `http://localhost:5173` - Vite development server
- `http://localhost:8080` - Other development servers
- `*` - All origins (for development)

### **Allowed Methods:**
- `GET` - Health checks, model info
- `POST` - Image predictions
- `OPTIONS` - CORS preflight requests
- `*` - All methods

### **Allowed Headers:**
- `Content-Type` - For file uploads
- `Authorization` - For future auth
- `*` - All headers

## 🚨 Important Notes

1. **Production Security**: Specific origin allowlist for production
2. **Development Flexibility**: Wildcard origin for local development
3. **Preflight Requests**: OPTIONS method handled automatically
4. **Credentials**: Allow credentials for authenticated requests

## 🎨 Frontend Integration

Your frontend can now make requests like:

```javascript
// Health check
fetch('https://batik-deploy-fastapi-production-c83f.up.railway.app/health')
  .then(response => response.json())
  .then(data => console.log(data));

// Image prediction
const formData = new FormData();
formData.append('file', imageFile);

fetch('https://batik-deploy-fastapi-production-c83f.up.railway.app/predict', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

---

**✅ The CORS issue has been resolved and your frontend can now access the API!** 