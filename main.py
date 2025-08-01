import os
import io
import json
import numpy as np
from typing import List, Dict, Any
from PIL import Image
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="Batik Classification API",
    description="API untuk klasifikasi gambar batik menggunakan model Genetic Algorithm",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
MODEL_PATH = "final_tuned_genetic_algorithm_model.keras"
LABELS_PATH = "labels.txt"
IMG_SIZE = (160, 160)
NUM_CLASSES = 60
model = None
class_names = None
model_loading_error = None

# Pydantic models for request/response
class PredictionResponse(BaseModel):
    predicted_class: str
    confidence: float
    all_predictions: List[Dict[str, Any]]

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_path: str
    model_error: str | None = None

def load_batik_names():
    """Load batik names from labels.txt"""
    try:
        if os.path.exists(LABELS_PATH):
            with open(LABELS_PATH, 'r', encoding='utf-8') as f:
                names = [line.strip() for line in f.readlines() if line.strip()]
            print(f"✅ Loaded {len(names)} batik names from {LABELS_PATH}")
            return names
        else:
            print(f"⚠️ Labels file not found: {LABELS_PATH}, using generic names")
            return [f"batik_class_{i}" for i in range(NUM_CLASSES)]
    except Exception as e:
        print(f"❌ Error loading labels: {e}, using generic names")
        return [f"batik_class_{i}" for i in range(NUM_CLASSES)]

def load_model_and_classes():
    """Load the trained model and class names"""
    global model, class_names, model_loading_error
    
    try:
        # Check if model file exists
        if not os.path.exists(MODEL_PATH):
            error_msg = f"Model file not found: {MODEL_PATH}"
            print(f"❌ {error_msg}")
            model_loading_error = error_msg
            return False
        
        # Check file size
        file_size = os.path.getsize(MODEL_PATH)
        print(f"📁 Model file found: {MODEL_PATH} ({file_size / (1024*1024):.2f} MB)")
        
        # Load the model
        model = load_model(MODEL_PATH)
        print(f"✅ Model berhasil dimuat dari: {MODEL_PATH}")
        
        # Load batik names from labels.txt
        class_names = load_batik_names()
        print(f"✅ Batik names loaded: {len(class_names)} classes")
        
        # Test model with a dummy input
        test_input = np.random.random((1, *IMG_SIZE, 3))
        test_prediction = model.predict(test_input, verbose=0)
        print(f"✅ Model test prediction successful: {test_prediction.shape}")
        
        model_loading_error = None
        return True
        
    except Exception as e:
        error_msg = f"Error loading model: {str(e)}"
        print(f"❌ {error_msg}")
        model_loading_error = error_msg
        return False

def preprocess_image(image_file: bytes) -> np.ndarray:
    """Preprocess image for model prediction"""
    try:
        # Convert bytes to PIL Image
        img = Image.open(io.BytesIO(image_file))
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize image
        img = img.resize(IMG_SIZE)
        
        # Convert to numpy array
        img_array = image.img_to_array(img)
        
        # Normalize pixel values to [0, 1]
        img_array = img_array / 255.0
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error preprocessing image: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    print("🚀 Starting Batik Classification API...")
    print(f"📂 Current working directory: {os.getcwd()}")
    print(f"📁 Model path: {os.path.abspath(MODEL_PATH)}")
    print(f"📁 Labels path: {os.path.abspath(LABELS_PATH)}")
    
    # List files in current directory
    print("📋 Files in current directory:")
    for file in os.listdir('.'):
        if file.endswith('.keras') or file.endswith('.h5') or file.endswith('.txt'):
            file_size = os.path.getsize(file)
            print(f"  - {file} ({file_size / (1024*1024):.2f} MB)")
    
    success = load_model_and_classes()
    if not success:
        print("⚠️ Warning: Model could not be loaded. API will not function properly.")
        print(f"🔍 Model loading error: {model_loading_error}")

@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint"""
    return {
        "message": "Batik Classification API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "predict_batch": "/predict-batch",
            "model_info": "/model-info",
            "debug": "/debug"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        model_loaded=model is not None,
        model_path=MODEL_PATH,
        model_error=model_loading_error
    )

@app.post("/predict", response_model=PredictionResponse)
async def predict_single_image(file: UploadFile = File(...)):
    """Predict single image"""
    if model is None:
        raise HTTPException(
            status_code=503, 
            detail=f"Model not loaded. Error: {model_loading_error or 'Unknown error'}"
        )
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read image file
        image_bytes = await file.read()
        
        # Preprocess image
        processed_image = preprocess_image(image_bytes)
        
        # Make prediction
        predictions = model.predict(processed_image, verbose=0)
        
        # Get predicted class and confidence
        predicted_class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_idx])
        predicted_class = class_names[predicted_class_idx]
        
        # Prepare all predictions
        all_predictions = []
        for i, (class_name, prob) in enumerate(zip(class_names, predictions[0])):
            all_predictions.append({
                "class": class_name,
                "confidence": float(prob),
                "rank": i + 1
            })
        
        # Sort by confidence (descending)
        all_predictions.sort(key=lambda x: x["confidence"], reverse=True)
        
        return PredictionResponse(
            predicted_class=predicted_class,
            confidence=confidence,
            all_predictions=all_predictions[:10]  # Return top 10 predictions
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/predict-batch")
async def predict_batch_images(files: List[UploadFile] = File(...)):
    """Predict multiple images"""
    if model is None:
        raise HTTPException(
            status_code=503, 
            detail=f"Model not loaded. Error: {model_loading_error or 'Unknown error'}"
        )
    
    if len(files) > 10:  # Limit batch size
        raise HTTPException(status_code=400, detail="Maximum 10 images per batch")
    
    results = []
    
    for file in files:
        try:
            # Validate file type
            if not file.content_type.startswith('image/'):
                results.append({
                    "filename": file.filename,
                    "error": "File must be an image"
                })
                continue
            
            # Read image file
            image_bytes = await file.read()
            
            # Preprocess image
            processed_image = preprocess_image(image_bytes)
            
            # Make prediction
            predictions = model.predict(processed_image, verbose=0)
            
            # Get predicted class and confidence
            predicted_class_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class_idx])
            predicted_class = class_names[predicted_class_idx]
            
            results.append({
                "filename": file.filename,
                "predicted_class": predicted_class,
                "confidence": confidence,
                "success": True
            })
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": str(e),
                "success": False
            })
    
    return {"predictions": results}

@app.get("/model-info")
async def get_model_info():
    """Get model information"""
    if model is None:
        raise HTTPException(
            status_code=503, 
            detail=f"Model not loaded. Error: {model_loading_error or 'Unknown error'}"
        )
    
    return {
        "model_path": MODEL_PATH,
        "input_shape": IMG_SIZE + (3,),
        "num_classes": NUM_CLASSES,
        "class_names": class_names,
        "model_summary": "Model loaded successfully",
        "model_error": model_loading_error
    }

@app.get("/debug")
async def debug_info():
    """Debug endpoint to check system status"""
    return {
        "current_directory": os.getcwd(),
        "model_path": os.path.abspath(MODEL_PATH),
        "model_file_exists": os.path.exists(MODEL_PATH),
        "model_file_size": os.path.getsize(MODEL_PATH) if os.path.exists(MODEL_PATH) else None,
        "labels_path": os.path.abspath(LABELS_PATH),
        "labels_file_exists": os.path.exists(LABELS_PATH),
        "model_loaded": model is not None,
        "model_loading_error": model_loading_error,
        "available_files": [f for f in os.listdir('.') if f.endswith('.keras') or f.endswith('.h5') or f.endswith('.txt')],
        "environment": os.environ.get('ENVIRONMENT', 'development'),
        "batik_names_count": len(class_names) if class_names else 0
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 