#!/usr/bin/env python3
"""
Test script untuk API Batik Classification
"""

import requests
import json
from PIL import Image
import io
import numpy as np

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_model_info():
    """Test model info endpoint"""
    print("\n🔍 Testing model info endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/model-info")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_test_image():
    """Create a test image"""
    # Create a simple test image (160x160 RGB)
    img_array = np.random.randint(0, 255, (160, 160, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return img_bytes.getvalue()

def test_prediction():
    """Test prediction endpoint"""
    print("\n🔍 Testing prediction endpoint...")
    try:
        # Create test image
        test_image = create_test_image()
        
        # Make prediction request
        files = {'file': ('test_image.jpg', test_image, 'image/jpeg')}
        response = requests.post(f"{BASE_URL}/predict", files=files)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Predicted Class: {result['predicted_class']}")
            print(f"Confidence: {result['confidence']:.4f}")
            print(f"Top 5 Predictions:")
            for i, pred in enumerate(result['all_predictions'][:5]):
                print(f"  {i+1}. {pred['class']}: {pred['confidence']:.4f}")
        else:
            print(f"Error: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_batch_prediction():
    """Test batch prediction endpoint"""
    print("\n🔍 Testing batch prediction endpoint...")
    try:
        # Create multiple test images
        test_images = []
        for i in range(3):
            test_image = create_test_image()
            test_images.append(('files', (f'test_image_{i}.jpg', test_image, 'image/jpeg')))
        
        # Make batch prediction request
        response = requests.post(f"{BASE_URL}/predict-batch", files=test_images)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Batch Results:")
            for pred in result['predictions']:
                if pred.get('success'):
                    print(f"  {pred['filename']}: {pred['predicted_class']} ({pred['confidence']:.4f})")
                else:
                    print(f"  {pred['filename']}: Error - {pred.get('error', 'Unknown error')}")
        else:
            print(f"Error: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting API tests...")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Model Info", test_model_info),
        ("Single Prediction", test_prediction),
        ("Batch Prediction", test_batch_prediction)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 30)
        success = test_func()
        results.append((test_name, success))
        print(f"{'✅ PASS' if success else '❌ FAIL'}: {test_name}")
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the API deployment.")

if __name__ == "__main__":
    main() 