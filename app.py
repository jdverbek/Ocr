import os
import re
import base64
from io import BytesIO
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from PIL import Image
import cv2
import numpy as np

app = Flask(__name__)
CORS(app)

# Try to import pytesseract, but handle gracefully if not available
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({"service": "OCR Patient Scanner", "status": "healthy", "tesseract": TESSERACT_AVAILABLE})

@app.route('/api/status')
def api_status():
    return jsonify({
        "service": "OCR Patient Scanner",
        "version": "2.0.0",
        "ocr_engine": "Tesseract (Server-side)" if TESSERACT_AVAILABLE else "Fallback OCR",
        "status": "operational"
    })


@app.route('/process_ocr', methods=['POST'])
def process_ocr():
    try:
        data = request.get_json()
        image_data = base64.b64decode(data['image'])
        
        # Convert to PIL Image once
        image = Image.open(BytesIO(image_data))
        
        # Convert to grayscale directly with PIL (more efficient)
        if image.mode != 'L':
            gray_image = image.convert('L')
        else:
            gray_image = image
        
        # Convert to numpy array for OpenCV operations (single conversion)
        gray_array = np.array(gray_image)
        
        # Apply thresholding and denoising in one pipeline
        _, thresh = cv2.threshold(gray_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed_array = cv2.medianBlur(thresh, 3)
        
        # Convert back to PIL Image once
        processed_image = Image.fromarray(processed_array)
        
        text = ""
        
        if TESSERACT_AVAILABLE:
            try:
                configs = [
                    r'--oem 3 --psm 8',  # Single word - most effective for patient numbers
                    r'--oem 3 --psm 6',  # Default configuration
                    r'--oem 3 --psm 7',  # Single text line
                    r'--oem 3 --psm 11', # Sparse text
                ]
                
                for config in configs:
                    try:
                        text = pytesseract.image_to_string(processed_image, config=config).strip()
                        if text and re.search(r'\d{8,}', text):  # Early termination if digits found
                            print(f"OCR successful with config: {config}")
                            print(f"Extracted text: {text}")
                            break
                    except Exception as config_error:
                        print(f"Config {config} failed: {config_error}")
                        continue
                
                if not text or not re.search(r'\d{8,}', text):
                    print("Trying OCR on original image...")
                    for config in configs:
                        try:
                            text = pytesseract.image_to_string(gray_image, config=config).strip()
                            if text and re.search(r'\d{8,}', text):
                                print(f"OCR successful on original with config: {config}")
                                print(f"Extracted text: {text}")
                                break
                        except Exception as config_error:
                            continue
                            
            except Exception as tesseract_error:
                print(f"Tesseract error: {tesseract_error}")
                text = ""
        else:
            # Fallback when Tesseract is not available
            text = ""
        
        # Find 10-digit patient number with improved pattern matching
        # First, try to find exactly 10 consecutive digits
        ten_digit_pattern = re.findall(r'\b\d{10}\b', text)
        if ten_digit_pattern:
            return jsonify({
                'success': True,
                'patient_number': ten_digit_pattern[0],
                'raw_text': text,
                'method': 'tesseract' if TESSERACT_AVAILABLE else 'fallback',
                'pattern_type': 'exact_10_digits'
            })
        
        # If no exact 10-digit match, look for longer sequences and extract 10 digits
        all_digits = re.sub(r'\D', '', text)
        digit_sequences = re.findall(r'\d{8,}', text)  # Find sequences of 8+ digits
        
        # Prioritize sequences that are exactly 10 digits or longer
        for sequence in sorted(digit_sequences, key=len, reverse=True):
            if len(sequence) >= 10:
                patient_number = sequence[:10]  # Take first 10 digits
                return jsonify({
                    'success': True,
                    'patient_number': patient_number,
                    'raw_text': text,
                    'method': 'tesseract' if TESSERACT_AVAILABLE else 'fallback',
                    'pattern_type': 'extracted_from_longer',
                    'original_sequence': sequence
                })
        
        # If still no match, check if we have at least 10 total digits
        if len(all_digits) >= 10:
            return jsonify({
                'success': True,
                'patient_number': all_digits[:10],
                'raw_text': text,
                'method': 'tesseract' if TESSERACT_AVAILABLE else 'fallback',
                'pattern_type': 'combined_digits',
                'note': 'Combined from multiple number sequences'
            })
        
        # Provide helpful feedback about what was found
        found_numbers = re.findall(r'\d+', text)
        return jsonify({
            'success': False,
            'message': 'No 10-digit patient number found',
            'raw_text': text,
            'method': 'tesseract' if TESSERACT_AVAILABLE else 'fallback',
            'found_numbers': found_numbers,
            'total_digits': len(all_digits),
            'suggestion': 'Try a clearer image or ensure the patient number is clearly visible'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'tesseract_available': TESSERACT_AVAILABLE
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

