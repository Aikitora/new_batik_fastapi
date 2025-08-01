# 🎨 Batik Classification API

API FastAPI untuk klasifikasi gambar batik menggunakan model Genetic Algorithm yang telah di-tune.

## 📋 Fitur

- ✅ **Single Image Prediction**: Prediksi satu gambar batik
- ✅ **Batch Prediction**: Prediksi multiple gambar sekaligus
- ✅ **Health Check**: Monitoring kesehatan API
- ✅ **Model Info**: Informasi detail model
- ✅ **Docker Support**: Containerization dengan Docker
- ✅ **CORS Enabled**: Support untuk frontend applications

## 🚀 Deployment

### Option 1: Local Development

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the API:**
```bash
python main.py
```

atau

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Option 2: Docker Deployment

1. **Build and run with Docker Compose:**
```bash
docker-compose up --build
```

2. **Or build and run manually:**
```bash
# Build image
docker build -t batik-api .

# Run container
docker run -p 8000:8000 batik-api
```

## 📚 API Endpoints

### 1. Root Endpoint
```http
GET /
```
**Response:**
```json
{
  "message": "Batik Classification API",
  "version": "1.0.0",
  "endpoints": {
    "health": "/health",
    "predict": "/predict",
    "predict_batch": "/predict-batch"
  }
}
```

### 2. Health Check
```http
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_path": "final_tuned_genetic_algorithm_model.keras"
}
```

### 3. Model Information
```http
GET /model-info
```
**Response:**
```json
{
  "model_path": "final_tuned_genetic_algorithm_model.keras",
  "input_shape": [160, 160, 3],
  "num_classes": 60,
  "class_names": ["batik_class_0", "batik_class_1", ...],
  "model_summary": "Model loaded successfully"
}
```

### 4. Single Image Prediction
```http
POST /predict
```
**Request:** Form data with image file
**Response:**
```json
{
  "predicted_class": "batik_class_15",
  "confidence": 0.8542,
  "all_predictions": [
    {
      "class": "batik_class_15",
      "confidence": 0.8542,
      "rank": 1
    },
    {
      "class": "batik_class_23",
      "confidence": 0.1234,
      "rank": 2
    }
  ]
}
```

### 5. Batch Prediction
```http
POST /predict-batch
```
**Request:** Multiple image files (max 10)
**Response:**
```json
{
  "predictions": [
    {
      "filename": "image1.jpg",
      "predicted_class": "batik_class_15",
      "confidence": 0.8542,
      "success": true
    },
    {
      "filename": "image2.jpg",
      "error": "File must be an image",
      "success": false
    }
  ]
}
```

## 🧪 Testing

### Run Test Script
```bash
python test_api.py
```

### Manual Testing with curl

1. **Health Check:**
```bash
curl http://localhost:8000/health
```

2. **Single Prediction:**
```bash
curl -X POST -F "file=@path/to/your/image.jpg" http://localhost:8000/predict
```

3. **Batch Prediction:**
```bash
curl -X POST -F "files=@image1.jpg" -F "files=@image2.jpg" http://localhost:8000/predict-batch
```

## 📊 Model Specifications

- **Input Size**: 160x160 pixels (RGB)
- **Number of Classes**: 60 batik classes
- **Model Type**: Transfer Learning with MobileNetV2
- **Optimization**: Genetic Algorithm tuning
- **Preprocessing**: Normalization to [0, 1] range

## 🔧 Configuration

### Environment Variables
- `PYTHONUNBUFFERED=1`: For better logging in Docker

### Model Parameters
- `IMG_SIZE = (160, 160)`: Input image size
- `NUM_CLASSES = 60`: Number of batik classes
- `MODEL_PATH = "final_tuned_genetic_algorithm_model.keras"`: Model file path

## 📁 Project Structure

```
batik-deploy/
├── main.py                              # FastAPI application
├── requirements.txt                     # Python dependencies
├── Dockerfile                          # Docker configuration
├── docker-compose.yml                  # Docker Compose configuration
├── test_api.py                         # API testing script
├── README.md                           # This file
└── final_tuned_genetic_algorithm_model.keras  # Trained model
```

## 🌐 API Documentation

Once the API is running, you can access:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

## 🔍 Monitoring

### Health Check
The API includes a health check endpoint that monitors:
- Model loading status
- API availability
- Model file existence

### Docker Health Check
The Docker container includes health checks that verify API availability every 30 seconds.

## 🚨 Error Handling

The API handles various error scenarios:
- Model not loaded (503 Service Unavailable)
- Invalid file type (400 Bad Request)
- Image processing errors (400 Bad Request)
- Prediction errors (500 Internal Server Error)

## 📈 Performance

- **Model Loading**: ~2-5 seconds on startup
- **Prediction Time**: ~100-500ms per image
- **Memory Usage**: ~500MB-1GB depending on model size
- **Concurrent Requests**: Supports multiple simultaneous predictions

## 🔐 Security Considerations

- Input validation for image files
- File size limits (handled by FastAPI)
- CORS configuration for web applications
- Non-root user in Docker container

## 🛠️ Troubleshooting

### Common Issues

1. **Model not loading:**
   - Check if model file exists
   - Verify file permissions
   - Check TensorFlow version compatibility

2. **Memory issues:**
   - Increase Docker memory limits
   - Use GPU if available
   - Optimize batch size

3. **Port conflicts:**
   - Change port in docker-compose.yml
   - Use different port in uvicorn command

### Logs
Check application logs for detailed error information:
```bash
# Docker logs
docker-compose logs batik-api

# Direct logs
tail -f logs/app.log
```

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the API documentation at `/docs`
3. Test with the provided test script
4. Check application logs for errors

---

**Note**: This API is designed for batik classification using a Genetic Algorithm-tuned model. The model expects 160x160 RGB images and outputs predictions for 60 different batik classes. 