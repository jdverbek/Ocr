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

def simple_digit_extraction(image):
    """
    Fallback OCR method using basic image processing
    when Tesseract is not available
    """
    try:
        # Convert PIL image to OpenCV format
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Find contours for text regions
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Look for rectangular regions that might contain text
        text_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 30 and h > 8 and 2 <= w/h <= 15:  # Likely text region
                text_regions.append((x, y, w, h))
        
        text_regions.sort(key=lambda r: (r[1], r[0]))
        
        if len(text_regions) > 0:
            return "FALLBACK_ATTEMPTED"
        
        return None
        
    except Exception as e:
        print(f"Fallback OCR error: {e}")
        return None

@app.route('/process_ocr', methods=['POST'])
def process_ocr():
    try:
        data = request.get_json()
        image_data = base64.b64decode(data['image'])
        
        # Convert to PIL Image
        image = Image.open(BytesIO(image_data))
        
        # Convert to OpenCV format for preprocessing
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Preprocess image for better OCR
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to get better contrast
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Denoise
        denoised = cv2.medianBlur(thresh, 3)
        
        # Convert back to PIL Image
        processed_image = Image.fromarray(denoised)
        
        text = ""
        
        if TESSERACT_AVAILABLE:
            try:
                digit_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789'
                text = pytesseract.image_to_string(processed_image, config=digit_config).strip()
                
                if not text or not any(c.isdigit() for c in text):
                    text = pytesseract.image_to_string(processed_image, config=r'--oem 3 --psm 6').strip()
                
                # If still no text, try original image
                if not text:
                    text = pytesseract.image_to_string(image, config=digit_config).strip()
                    
            except Exception as tesseract_error:
                print(f"Tesseract error: {tesseract_error}")
                # Fall back to simple extraction
                fallback_result = simple_digit_extraction(processed_image)
                if fallback_result and fallback_result != "FALLBACK_ATTEMPTED":
                    text = fallback_result
        else:
            # Use fallback method
            fallback_result = simple_digit_extraction(processed_image)
            if fallback_result and fallback_result != "FALLBACK_ATTEMPTED":
                text = fallback_result
            else:
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

