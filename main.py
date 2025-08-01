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
IMG_SIZE = (160, 160)
NUM_CLASSES = 60
model = None
class_names = None

# Pydantic models for request/response
class PredictionResponse(BaseModel):
    predicted_class: str
    confidence: float
    all_predictions: List[Dict[str, Any]]

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_path: str

def load_model_and_classes():
    """Load the trained model and class names"""
    global model, class_names
    
    try:
        # Load the model
        model = load_model(MODEL_PATH)
        print(f"✅ Model berhasil dimuat dari: {MODEL_PATH}")
        
        # Generate class names (since we don't have the original class names)
        # In a real scenario, you would load this from a file or database
        class_names = [f"batik_class_{i}" for i in range(NUM_CLASSES)]
        print(f"✅ Class names generated: {len(class_names)} classes")
        
        return True
    except Exception as e:
        print(f"❌ Error loading model: {str(e)}")
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
    success = load_model_and_classes()
    if not success:
        print("⚠️ Warning: Model could not be loaded. API will not function properly.")

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "Batik Classification API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "predict_batch": "/predict-batch"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        model_loaded=model is not None,
        model_path=MODEL_PATH
    )

@app.post("/predict", response_model=PredictionResponse)
async def predict_single_image(file: UploadFile = File(...)):
    """Predict single image"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
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
        raise HTTPException(status_code=503, detail="Model not loaded")
    
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
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "model_path": MODEL_PATH,
        "input_shape": IMG_SIZE + (3,),
        "num_classes": NUM_CLASSES,
        "class_names": class_names,
        "model_summary": "Model loaded successfully"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 