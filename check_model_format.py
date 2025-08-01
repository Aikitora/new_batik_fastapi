#!/usr/bin/env python3

import os
import json
import h5py
import tensorflow as tf
from tensorflow import keras

def check_model_format(model_path):
    """Check the format of the model file"""
    print(f"🔍 Checking model format: {model_path}")
    
    if not os.path.exists(model_path):
        print(f"❌ Model file not found: {model_path}")
        return False
    
    file_size = os.path.getsize(model_path)
    print(f"📁 File size: {file_size / (1024*1024):.2f} MB")
    
    try:
        # Try to open as HDF5 file
        with h5py.File(model_path, 'r') as f:
            print("✅ Model is in HDF5 format")
            print("📋 HDF5 keys:", list(f.keys()))
            
            # Check if it has the keras model structure
            if 'model_config' in f:
                print("✅ Contains model_config")
                config = json.loads(f['model_config'][()])
                print(f"📋 Model config keys: {list(config.keys())}")
                
                if 'config' in config:
                    layers = config['config']['layers']
                    print(f"📋 Number of layers: {len(layers)}")
                    
                    # Check first layer
                    if layers:
                        first_layer = layers[0]
                        print(f"📋 First layer: {first_layer['class_name']}")
                        if 'config' in first_layer:
                            config_keys = list(first_layer['config'].keys())
                            print(f"📋 First layer config keys: {config_keys}")
                            
                            if 'batch_shape' in config_keys:
                                print("⚠️ Found batch_shape in first layer config")
                                print(f"📋 batch_shape value: {first_layer['config']['batch_shape']}")
            
            return True
            
    except Exception as e:
        print(f"❌ Not a valid HDF5 file: {e}")
        
        try:
            # Try to read as text file
            with open(model_path, 'r') as f:
                first_line = f.readline().strip()
                print(f"📋 First line: {first_line}")
                
                if first_line.startswith('{'):
                    print("✅ Model appears to be in JSON format")
                    return True
                else:
                    print("❌ Unknown model format")
                    return False
                    
        except Exception as e2:
            print(f"❌ Cannot read as text file: {e2}")
            return False

def try_convert_model(model_path):
    """Try to convert the model to a compatible format"""
    print(f"🔄 Attempting to convert model: {model_path}")
    
    try:
        # Try loading with different strategies
        print("🔄 Strategy 1: Load with custom InputLayer")
        
        from tensorflow.keras.layers import InputLayer
        
        class CustomInputLayer(InputLayer):
            def __init__(self, **kwargs):
                # Remove problematic parameters
                for param in ['batch_shape', 'batch_input_shape']:
                    if param in kwargs:
                        print(f"🔄 Removing {param}: {kwargs[param]}")
                        del kwargs[param]
                super().__init__(**kwargs)
        
        # Try loading with custom objects
        model = keras.models.load_model(model_path, custom_objects={'InputLayer': CustomInputLayer}, compile=False)
        print("✅ Model loaded successfully with custom InputLayer!")
        
        # Save in a compatible format
        output_path = model_path.replace('.keras', '_converted.keras')
        model.save(output_path, save_format='keras')
        print(f"✅ Model converted and saved to: {output_path}")
        
        return output_path
        
    except Exception as e:
        print(f"❌ Strategy 1 failed: {e}")
        
        try:
            print("🔄 Strategy 2: Load with compile=False and save")
            model = keras.models.load_model(model_path, compile=False)
            print("✅ Model loaded successfully!")
            
            # Save in a compatible format
            output_path = model_path.replace('.keras', '_converted.keras')
            model.save(output_path, save_format='keras')
            print(f"✅ Model converted and saved to: {output_path}")
            
            return output_path
            
        except Exception as e2:
            print(f"❌ Strategy 2 failed: {e2}")
            return None

if __name__ == "__main__":
    model_path = "final_tuned_genetic_algorithm_model.keras"
    
    print("🔍 Model Format Analysis")
    print("=" * 50)
    
    # Check model format
    if check_model_format(model_path):
        print("\n🔄 Attempting Model Conversion")
        print("=" * 50)
        
        converted_path = try_convert_model(model_path)
        
        if converted_path and os.path.exists(converted_path):
            print(f"\n✅ Conversion successful!")
            print(f"📁 Original model: {model_path}")
            print(f"📁 Converted model: {converted_path}")
            print(f"📁 Converted size: {os.path.getsize(converted_path) / (1024*1024):.2f} MB")
        else:
            print("\n❌ Conversion failed")
    else:
        print("\n❌ Cannot analyze model format") 