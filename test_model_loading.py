#!/usr/bin/env python3

import os
import tensorflow as tf
from tensorflow import keras
import numpy as np

def test_model_loading():
    """Test different model loading approaches"""
    model_path = "final_tuned_genetic_algorithm_model.keras"
    
    print(f"🔍 Testing model loading: {model_path}")
    print(f"📁 File exists: {os.path.exists(model_path)}")
    print(f"📁 File size: {os.path.getsize(model_path) / (1024*1024):.2f} MB")
    print(f"🔧 TensorFlow version: {tf.__version__}")
    
    # Test 1: Basic load
    print("\n🔄 Test 1: Basic load_model")
    try:
        model = keras.models.load_model(model_path)
        print("✅ Basic load successful!")
        return True
    except Exception as e:
        print(f"❌ Basic load failed: {e}")
    
    # Test 2: Load with compile=False
    print("\n🔄 Test 2: Load with compile=False")
    try:
        model = keras.models.load_model(model_path, compile=False)
        print("✅ Load with compile=False successful!")
        return True
    except Exception as e:
        print(f"❌ Load with compile=False failed: {e}")
    
    # Test 3: Load with custom InputLayer
    print("\n🔄 Test 3: Load with custom InputLayer")
    try:
        from tensorflow.keras.layers import InputLayer
        
        class CustomInputLayer(InputLayer):
            def __init__(self, **kwargs):
                # Remove problematic parameters
                for param in ['batch_shape', 'batch_input_shape']:
                    if param in kwargs:
                        print(f"🔄 Removing {param}: {kwargs[param]}")
                        del kwargs[param]
                super().__init__(**kwargs)
        
        model = keras.models.load_model(model_path, custom_objects={'InputLayer': CustomInputLayer}, compile=False)
        print("✅ Load with custom InputLayer successful!")
        return True
    except Exception as e:
        print(f"❌ Load with custom InputLayer failed: {e}")
    
    # Test 4: Try with different TensorFlow settings
    print("\n🔄 Test 4: Load with TensorFlow settings")
    try:
        tf.keras.backend.clear_session()
        model = keras.models.load_model(model_path, compile=False)
        print("✅ Load with TensorFlow settings successful!")
        return True
    except Exception as e:
        print(f"❌ Load with TensorFlow settings failed: {e}")
    
    # Test 5: Try to read the file directly
    print("\n🔄 Test 5: Read file directly")
    try:
        with open(model_path, 'rb') as f:
            header = f.read(100)
            print(f"📋 File header (hex): {header.hex()}")
            
            # Check if it's a zip file
            if header.startswith(b'PK'):
                print("✅ File appears to be a zip file (Keras format)")
            else:
                print("❌ File is not a zip file")
    except Exception as e:
        print(f"❌ Cannot read file: {e}")
    
    return False

if __name__ == "__main__":
    success = test_model_loading()
    if success:
        print("\n✅ Model loading test successful!")
    else:
        print("\n❌ All model loading tests failed") 