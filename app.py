import os
import re
import base64
from io import BytesIO
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from PIL import Image
import pytesseract
import cv2
import numpy as np

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({"service": "OCR Patient Scanner", "status": "healthy"})

@app.route('/api/status')
def api_status():
    return jsonify({
        "service": "OCR Patient Scanner",
        "version": "2.0.0",
        "ocr_engine": "Tesseract (Server-side)",
        "status": "operational"
    })

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
        
        # Perform OCR with digit-only configuration
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
        text = pytesseract.image_to_string(processed_image, config=custom_config)
        
        # Find 10-digit patient number
        digits_only = re.sub(r'\D', '', text)
        
        # Look for exactly 10 consecutive digits
        if len(digits_only) >= 10:
            patient_number = digits_only[:10]
            return jsonify({
                'success': True,
                'patient_number': patient_number,
                'raw_text': text
            })
        
        return jsonify({
            'success': False,
            'message': 'No 10-digit number found',
            'raw_text': text
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

