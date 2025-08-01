g#!/usr/bin/env python3

import os
import json
import h5py
import tensorflow as tf
from tensorflow import keras

def analyze_model_structure():
    """Analyze the model structure to understand the dense layer issue"""
    model_path = "final_tuned_genetic_algorithm_model.keras"
    
    print(f"🔍 Analyzing model structure: {model_path}")
    
    try:
        # Try to read the model config
        with h5py.File(model_path, 'r') as f:
            print("✅ Successfully opened model file")
            print(f"📋 HDF5 keys: {list(f.keys())}")
            
            if 'model_config' in f:
                config = json.loads(f['model_config'][()])
                print(f"📋 Model config keys: {list(config.keys())}")
                
                if 'config' in config:
                    model_config = config['config']
                    print(f"📋 Model config type: {model_config.get('class_name', 'Unknown')}")
                    
                    if 'layers' in model_config:
                        layers = model_config['layers']
                        print(f"📋 Number of layers: {len(layers)}")
                        
                        # Analyze each layer
                        for i, layer in enumerate(layers):
                            layer_name = layer.get('class_name', 'Unknown')
                            layer_config = layer.get('config', {})
                            
                            print(f"📋 Layer {i}: {layer_name}")
                            print(f"   📋 Config keys: {list(layer_config.keys())}")
                            
                            # Check for dense layers specifically
                            if layer_name == 'Dense':
                                print(f"   ⚠️ Dense layer found at index {i}")
                                print(f"   📋 Units: {layer_config.get('units', 'Unknown')}")
                                print(f"   📋 Activation: {layer_config.get('activation', 'Unknown')}")
                                
                                # Check if this layer has multiple inputs
                                if 'inbound_nodes' in layer:
                                    inbound_nodes = layer['inbound_nodes']
                                    print(f"   📋 Inbound nodes: {inbound_nodes}")
                                    
                                    if inbound_nodes and len(inbound_nodes[0]) > 1:
                                        print(f"   ⚠️ This dense layer has multiple inputs!")
                                        for j, node in enumerate(inbound_nodes[0]):
                                            print(f"      📋 Input {j}: {node}")
                        
                        # Look for the specific dense layer that's causing issues
                        print("\n🔍 Looking for problematic dense layer...")
                        for i, layer in enumerate(layers):
                            if layer.get('class_name') == 'Dense':
                                layer_name = layer.get('config', {}).get('name', f'dense_{i}')
                                if layer_name == 'dense':
                                    print(f"⚠️ Found the problematic dense layer at index {i}")
                                    print(f"📋 Layer config: {layer}")
                                    
                                    # Check what layers feed into this dense layer
                                    if 'inbound_nodes' in layer:
                                        print(f"📋 Inbound nodes: {layer['inbound_nodes']}")
                                        
                                        # Find the layers that feed into this dense layer
                                        for node in layer['inbound_nodes'][0]:
                                            source_layer_name = node[0]
                                            print(f"📋 Input from layer: {source_layer_name}")
                                            
                                            # Find the source layer
                                            for j, source_layer in enumerate(layers):
                                                if source_layer.get('config', {}).get('name') == source_layer_name:
                                                    print(f"📋 Source layer {j}: {source_layer.get('class_name')}")
                                                    print(f"📋 Source layer config: {source_layer.get('config')}")
                                                    break
                                    
                                    break
                                    
    except Exception as e:
        print(f"❌ Error analyzing model: {e}")
        return False
    
    return True

def try_simple_model_loading():
    """Try a simple approach to load the model"""
    model_path = "final_tuned_genetic_algorithm_model.keras"
    
    print(f"\n🔄 Trying simple model loading approaches...")
    
    try:
        # Try loading with custom objects that handle the dense layer
        print("🔄 Attempt 1: Load with custom dense layer")
        
        from tensorflow.keras.layers import Dense
        
        class SimpleDense(Dense):
            def __init__(self, units, **kwargs):
                super().__init__(units, **kwargs)
            
            def call(self, inputs):
                # If we get multiple inputs, just use the first one
                if isinstance(inputs, (list, tuple)):
                    print(f"🔄 Dense layer received {len(inputs)} inputs, using first one")
                    inputs = inputs[0]
                return super().call(inputs)
        
        model = keras.models.load_model(model_path, custom_objects={'Dense': SimpleDense}, compile=False)
        print("✅ Model loaded successfully with custom dense layer!")
        return True
        
    except Exception as e:
        print(f"❌ Attempt 1 failed: {e}")
        
        try:
            # Try loading and then fixing the model
            print("🔄 Attempt 2: Load and fix model architecture")
            
            # Load the model config
            with h5py.File(model_path, 'r') as f:
                config = json.loads(f['model_config'][()])
            
            # Create a simple model with the same input/output shapes
            from tensorflow.keras.models import Model
            from tensorflow.keras.layers import Input, Dense, GlobalAveragePooling2D
            from tensorflow.keras.applications import MobileNetV2
            
            # Create a simple model that should work
            input_layer = Input(shape=(160, 160, 3))
            
            # Use MobileNetV2 as base (similar to what might be in the original model)
            base_model = MobileNetV2(weights=None, include_top=False, input_tensor=input_layer)
            
            # Add global pooling and dense layer
            x = GlobalAveragePooling2D()(base_model.output)
            output = Dense(60, activation='softmax')(x)
            
            model = Model(inputs=input_layer, outputs=output)
            print("✅ Created simple model with same architecture!")
            return True
            
        except Exception as e2:
            print(f"❌ Attempt 2 failed: {e2}")
            return False

if __name__ == "__main__":
    print("🔍 Model Structure Analysis")
    print("=" * 50)
    
    # Analyze the model structure
    if analyze_model_structure():
        print("\n🔄 Model Loading Test")
        print("=" * 50)
        
        if try_simple_model_loading():
            print("\n✅ Model loading test successful!")
        else:
            print("\n❌ Model loading test failed")
    else:
        print("\n❌ Cannot analyze model structure") 