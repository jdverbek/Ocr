#!/usr/bin/env python3
import base64
import json
import requests
from PIL import Image
import io
import sys

def test_medical_card_ocr():
    """Test OCR with the real medical card images"""
    
    test_cases = [
        (
            "/home/ubuntu/attachments/a8e442a5-3e0b-41b0-b2bc-d29c253dbda0/IMG_4547.jpeg",
            "3912171035",
            "Real medical card with patient number 3912171035"
        ),
        (
            "/home/ubuntu/attachments/b993fb49-dc23-45af-93ce-a9b3707e941c/IMG_4564.jpeg",
            None,
            "Mobile app error screen (should fail gracefully)"
        )
    ]
    
    print("Testing Medical Card OCR Improvements")
    print("=" * 50)
    
    all_passed = True
    
    for image_path, expected_number, description in test_cases:
        print(f"\nTesting: {description}")
        print(f"Image: {image_path}")
        print(f"Expected: {expected_number}")
        
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            img_base64 = base64.b64encode(image_data).decode()
            
            response = requests.post('http://localhost:10000/process_ocr', 
                                   json={'image': img_base64},
                                   timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ OCR request successful")
                print(f"Response: {json.dumps(result, indent=2)}")
                
                if expected_number:
                    if result.get('success') and result.get('patient_number') == expected_number:
                        print(f"✓ SUCCESS: Correctly extracted patient number {expected_number}")
                    else:
                        print(f"✗ FAILED: Expected {expected_number}, got {result.get('patient_number', 'None')}")
                        all_passed = False
                else:
                    if not result.get('success'):
                        print(f"✓ SUCCESS: Correctly failed on error screen image")
                    else:
                        print(f"~ WARNING: Unexpectedly extracted number from error screen: {result.get('patient_number')}")
                        
            else:
                print(f"✗ OCR request failed with status {response.status_code}")
                print(f"Response: {response.text}")
                all_passed = False
                
        except Exception as e:
            print(f"✗ Test failed with error: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL MEDICAL CARD OCR TESTS PASSED!")
        print("The OCR robustness improvements are working correctly.")
    else:
        print("❌ SOME MEDICAL CARD OCR TESTS FAILED!")
        print("The OCR improvements need further investigation.")
    
    return all_passed

def test_synthetic_image_regression():
    """Test that synthetic images still work (regression test)"""
    print("\nTesting Synthetic Image Regression")
    print("=" * 40)
    
    from PIL import Image, ImageDraw, ImageFont
    
    img = Image.new('RGB', (400, 100), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except:
        font = ImageFont.load_default()
    
    test_number = "1234567890"
    draw.text((50, 30), test_number, fill='black', font=font)
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    try:
        response = requests.post('http://localhost:10000/process_ocr', 
                               json={'image': img_base64},
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('patient_number') == test_number:
                print(f"✓ SUCCESS: Synthetic image regression test passed")
                return True
            else:
                print(f"✗ FAILED: Synthetic image regression test failed")
                print(f"Expected: {test_number}, got: {result.get('patient_number')}")
                return False
        else:
            print(f"✗ Synthetic test request failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Synthetic test failed with error: {e}")
        return False

if __name__ == "__main__":
    print("Starting OCR Medical Card Test Suite")
    print("Waiting for Flask server to be ready...")
    
    medical_card_success = test_medical_card_ocr()
    
    synthetic_success = test_synthetic_image_regression()
    
    print("\n" + "=" * 60)
    print("FINAL TEST RESULTS:")
    print(f"Medical Card OCR: {'PASS' if medical_card_success else 'FAIL'}")
    print(f"Synthetic Regression: {'PASS' if synthetic_success else 'FAIL'}")
    
    if medical_card_success and synthetic_success:
        print("\n🎉 ALL TESTS PASSED - OCR improvements are working correctly!")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED - OCR improvements need investigation!")
        sys.exit(1)
