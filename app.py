from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    """Serve the main OCR scanner page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    return jsonify({'status': 'healthy', 'service': 'OCR Patient Scanner'})

@app.route('/api/status')
def api_status():
    """API status endpoint for future API features"""
    return jsonify({
        'status': 'active',
        'version': '1.0.0',
        'features': ['ocr_scanning', 'patient_number_recognition']
    })

if __name__ == '__main__':
    # For local development
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

