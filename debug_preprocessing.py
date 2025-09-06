#!/usr/bin/env python3
import pytesseract
from PIL import Image, ImageEnhance
import cv2
import numpy as np
import re

def debug_preprocessing_methods():
    """Debug each preprocessing method individually"""
    
    image_path = "/home/ubuntu/attachments/a8e442a5-3e0b-41b0-b2bc-d29c253dbda0/IMG_4547.jpeg"
    
    print(f"Loading medical card image: {image_path}")
    image = Image.open(image_path)
    
    # Convert to grayscale
    if image.mode != 'L':
        gray_image = image.convert('L')
    else:
        gray_image = image
    
    gray_array = np.array(gray_image)
    
    print("\nTesting each preprocessing method with different OCR configs:")
    print("=" * 70)
    
    configs = [
        r'--oem 3 --psm 8',  # Single word
        r'--oem 3 --psm 6',  # Default configuration
        r'--oem 3 --psm 7',  # Single text line
        r'--oem 3 --psm 11', # Sparse text
    ]
    
    print("\n1. OTSU + Median Blur Method:")
    _, thresh_otsu = cv2.threshold(gray_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    processed_otsu = cv2.medianBlur(thresh_otsu, 3)
    otsu_img = Image.fromarray(processed_otsu)
    
    for config in configs:
        try:
            text = pytesseract.image_to_string(otsu_img, config=config).strip()
            has_digits = bool(re.search(r'\d', text))
            print(f"  Config {config}: has_digits={has_digits}, text='{text[:50]}{'...' if len(text) > 50 else ''}'")
        except Exception as e:
            print(f"  Config {config}: ERROR - {e}")
    
    print("\n2. Enhanced Contrast + OTSU Method:")
    enhanced_contrast = np.array(ImageEnhance.Contrast(gray_image).enhance(2.0))
    _, thresh_enhanced = cv2.threshold(enhanced_contrast, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    denoised_enhanced = cv2.medianBlur(thresh_enhanced, 3)
    enhanced_img = Image.fromarray(denoised_enhanced)
    
    for config in configs:
        try:
            text = pytesseract.image_to_string(enhanced_img, config=config).strip()
            has_digits = bool(re.search(r'\d', text))
            print(f"  Config {config}: has_digits={has_digits}, text='{text[:50]}{'...' if len(text) > 50 else ''}'")
        except Exception as e:
            print(f"  Config {config}: ERROR - {e}")
    
    print("\n3. Adaptive Thresholding Method:")
    adaptive_thresh = cv2.adaptiveThreshold(gray_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    adaptive_img = Image.fromarray(adaptive_thresh)
    
    for config in configs:
        try:
            text = pytesseract.image_to_string(adaptive_img, config=config).strip()
            has_digits = bool(re.search(r'\d', text))
            print(f"  Config {config}: has_digits={has_digits}, text='{text[:50]}{'...' if len(text) > 50 else ''}'")
        except Exception as e:
            print(f"  Config {config}: ERROR - {e}")
    
    print("\n4. Original Grayscale Method:")
    for config in configs:
        try:
            text = pytesseract.image_to_string(gray_image, config=config).strip()
            has_digits = bool(re.search(r'\d', text))
            print(f"  Config {config}: has_digits={has_digits}, text='{text[:50]}{'...' if len(text) > 50 else ''}'")
        except Exception as e:
            print(f"  Config {config}: ERROR - {e}")

if __name__ == "__main__":
    debug_preprocessing_methods()
