#!/usr/bin/env python3

import os
import tensorflow as tf
from tensorflow import keras
import numpy as np

def test_model_weights():
    """Test if the model has proper weights"""
    model_path = "final_tuned_genetic_algorithm_model.keras"
    
    print(f"🔍 Testing model weights: {model_path}")
    print(f"📁 File exists: {os.path.exists(model_path)}")
    print(f"📁 File size: {os.path.getsize(model_path) / (1024*1024):.2f} MB")
    
    try:
        # Load the model
        print("🔄 Loading model...")
        model = keras.models.load_model(model_path, compile=False)
        print("✅ Model loaded successfully!")
        
        # Check model summary
        print("\n📋 Model Summary:")
        model.summary()
        
        # Check if model has weights
        print("\n🔍 Checking model weights...")
        total_params = model.count_params()
        trainable_params = sum([tf.size(w).numpy() for w in model.trainable_weights])
        non_trainable_params = sum([tf.size(w).numpy() for w in model.non_trainable_weights])
        
        print(f"📊 Total parameters: {total_params:,}")
        print(f"📊 Trainable parameters: {trainable_params:,}")
        print(f"📊 Non-trainable parameters: {non_trainable_params:,}")
        
        # Test prediction
        print("\n🧪 Testing prediction...")
        test_input = np.random.random((1, 160, 160, 3))
        prediction = model.predict(test_input, verbose=0)
        
        print(f"📊 Prediction shape: {prediction.shape}")
        print(f"📊 Prediction sum: {np.sum(prediction):.6f}")
        print(f"📊 Prediction min: {np.min(prediction):.6f}")
        print(f"📊 Prediction max: {np.max(prediction):.6f}")
        
        # Check if predictions are random
        unique_values = np.unique(prediction)
        print(f"📊 Unique prediction values: {len(unique_values)}")
        
        if len(unique_values) == 1:
            print("⚠️ WARNING: All predictions are the same! Model may not be trained properly.")
        elif len(unique_values) < 10:
            print("⚠️ WARNING: Very few unique prediction values. Model may not be trained properly.")
        else:
            print("✅ Model predictions look good!")
        
        # Show top predictions
        top_indices = np.argsort(prediction[0])[-5:][::-1]
        print(f"\n🏆 Top 5 predictions:")
        for i, idx in enumerate(top_indices):
            print(f"  {i+1}. Class {idx}: {prediction[0][idx]:.6f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing model: {e}")
        return False

if __name__ == "__main__":
    success = test_model_weights()
    if success:
        print("\n✅ Model weights test completed!")
    else:
        print("\n❌ Model weights test failed!") 