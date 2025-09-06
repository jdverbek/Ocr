#!/usr/bin/env python3
import base64
import json
import requests
import time

def test_accuracy_fix():
    """Test OCR accuracy fix with the problematic image"""
    
    image_path = "/home/ubuntu/attachments/55d98a9d-4959-4f08-a404-cbc96f6e22db/IMG_4566.png"
    
    print(f"Testing OCR accuracy fix with: {image_path}")
    
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        img_base64 = base64.b64encode(image_data).decode()
        
        print("Sending OCR request...")
        response = requests.post('http://localhost:10000/process_ocr', 
                               json={'image': img_base64},
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            extracted = result.get('patient_number', 'None')
            expected = '3912171035'
            
            print(f"Expected: {expected}")
            print(f"Extracted: {extracted}")
            print(f"Success: {extracted == expected}")
            
            return extracted == expected
        else:
            print(f"Request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    print("Waiting for Flask server...")
    time.sleep(3)
    
    success = test_accuracy_fix()
    if success:
        print("✅ OCR accuracy fix successful!")
    else:
        print("❌ OCR accuracy fix failed!")
