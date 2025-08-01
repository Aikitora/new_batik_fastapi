#!/usr/bin/env python3

import os
import json
import h5py
import tensorflow as tf
from tensorflow import keras
import numpy as np

def analyze_model_architecture():
    """Analyze the model architecture to understand the multiple inputs issue"""
    model_path = "final_tuned_genetic_algorithm_model.keras"
    
    print(f"🔍 Analyzing model architecture: {model_path}")
    
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
                        
                        # Find the problematic dense layer
                        print("\n🔍 Looking for dense layer with multiple inputs...")
                        for i, layer in enumerate(layers):
                            layer_name = layer.get('class_name', 'Unknown')
                            layer_config = layer.get('config', {})
                            
                            if layer_name == 'Dense':
                                layer_name_config = layer_config.get('name', f'dense_{i}')
                                print(f"📋 Layer {i}: {layer_name} ({layer_name_config})")
                                
                                # Check inbound nodes for multiple inputs
                                if 'inbound_nodes' in layer:
                                    inbound_nodes = layer['inbound_nodes']
                                    print(f"  📋 Inbound nodes: {inbound_nodes}")
                                    
                                    if inbound_nodes and len(inbound_nodes[0]) > 1:
                                        print(f"  ⚠️ This dense layer has multiple inputs!")
                                        print(f"  📋 Number of inputs: {len(inbound_nodes[0])}")
                                        
                                        for j, node in enumerate(inbound_nodes[0]):
                                            source_layer_name = node[0]
                                            print(f"    📋 Input {j+1} from layer: {source_layer_name}")
                                            
                                            # Find the source layer
                                            for k, source_layer in enumerate(layers):
                                                if source_layer.get('config', {}).get('name') == source_layer_name:
                                                    source_class = source_layer.get('class_name', 'Unknown')
                                                    print(f"    📋 Source layer {k}: {source_class}")
                                                    
                                                    # Check if it's a concatenation layer
                                                    if source_class == 'Concatenate':
                                                        print(f"    ⚠️ Input comes from Concatenate layer!")
                                                        if 'inbound_nodes' in source_layer:
                                                            concat_inputs = source_layer['inbound_nodes']
                                                            print(f"    📋 Concatenate inputs: {concat_inputs}")
                                                    break
                                        
                                        # This is the problematic layer
                                        print(f"\n🎯 Found problematic dense layer: {layer_name_config}")
                                        print(f"📋 Layer config: {layer_config}")
                                        return layer_name_config, inbound_nodes[0]
                        
                        print("\n❌ No dense layer with multiple inputs found")
                        return None, None
                        
    except Exception as e:
        print(f"❌ Error analyzing model: {e}")
        return None, None

def create_custom_model_loader():
    """Create a custom model loader based on the architecture analysis"""
    print("\n🔧 Creating custom model loader...")
    
    # Based on the error, we know there are 2 inputs with shape (None, 5, 5, 1280)
    # This suggests a model with feature fusion or concatenation
    
    from tensorflow.keras.layers import Dense, Concatenate, GlobalAveragePooling2D
    
    class CustomDense(Dense):
        def __init__(self, units, **kwargs):
            super().__init__(units, **kwargs)
        
        def call(self, inputs):
            # Handle multiple inputs by concatenating them
            if isinstance(inputs, (list, tuple)):
                print(f"🔄 CustomDense: Received {len(inputs)} inputs")
                
                processed_inputs = []
                for i, inp in enumerate(inputs):
                    print(f"  📋 Input {i+1} shape: {inp.shape}")
                    
                    # Apply global pooling if 4D
                    if len(inp.shape) == 4:
                        inp = GlobalAveragePooling2D()(inp)
                        print(f"  📋 Input {i+1} after pooling: {inp.shape}")
                    
                    processed_inputs.append(inp)
                
                # Concatenate all inputs
                if len(processed_inputs) > 1:
                    inputs = Concatenate()(processed_inputs)
                    print(f"  📋 Final concatenated shape: {inputs.shape}")
                else:
                    inputs = processed_inputs[0]
            
            return super().call(inputs)
    
    return CustomDense

def test_custom_loader():
    """Test the custom model loader"""
    model_path = "final_tuned_genetic_algorithm_model.keras"
    
    print("\n🧪 Testing custom model loader...")
    
    try:
        # Create custom dense layer
        CustomDense = create_custom_model_loader()
        
        # Load model with custom dense layer
        model = keras.models.load_model(model_path, custom_objects={'Dense': CustomDense}, compile=False)
        print("✅ Model loaded successfully with custom dense layer!")
        
        # Test prediction
        test_input = np.random.random((1, 160, 160, 3))
        prediction = model.predict(test_input, verbose=0)
        
        print(f"✅ Prediction successful: {prediction.shape}")
        print(f"✅ Prediction sum: {np.sum(prediction):.6f}")
        print(f"✅ Unique values: {len(np.unique(prediction))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Custom loader test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Model Architecture Analysis")
    print("=" * 50)
    
    # Analyze the model architecture
    dense_layer_name, inbound_nodes = analyze_model_architecture()
    
    if dense_layer_name:
        print(f"\n🎯 Problematic layer: {dense_layer_name}")
        print(f"📋 Inbound nodes: {inbound_nodes}")
        
        # Test custom loader
        if test_custom_loader():
            print("\n✅ Custom loader test successful!")
        else:
            print("\n❌ Custom loader test failed!")
    else:
        print("\n❌ Could not identify problematic layer") 