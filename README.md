# Patient Number OCR Scanner

A lightweight OCR web application for recognizing 10-digit patient numbers from photos. This solution uses Tesseract.js (a JavaScript OCR library that runs entirely in the browser) combined with the HTML5 camera API for capturing photos directly from mobile devices.

## Key Features

- **Tesseract.js OCR** - A lightweight JavaScript OCR library that runs entirely in the browser (no server-side processing needed)
- **Mobile-optimized UI** - Designed specifically for iPhone Safari with proper touch targets and responsive design
- **Camera Integration** - Uses HTML5 file input with `capture="environment"` for direct camera access
- **Smart Pattern Matching** - Specifically searches for 10-digit sequences (patient numbers)
- **User-friendly Interface** - Clear feedback, progress indicators, and copy-to-clipboard functionality

## How It Works

1. User taps "Get Patient Number from Camera" button
2. Safari opens the camera interface
3. User takes a photo of the document
4. Tesseract.js processes the image locally in the browser
5. The app extracts and displays the 10-digit patient number
6. User can copy the number to clipboard with one tap

## Deployment

This is a static HTML file with client-side JavaScript that can be deployed as a static site on platforms like:

- Render.com
- Netlify
- Vercel
- GitHub Pages

### Deploying on Render.com

1. Fork or clone this repository
2. In Render, create a new "Static Site"
3. Connect your repository
4. Deploy - no build command needed

## Optimizations for Accuracy

- The OCR engine is configured to only recognize digits (0-9) for better accuracy
- It looks for exactly 10 consecutive digits
- Works best with clear, well-lit photos

## Privacy & Security

- All processing happens locally in the browser
- No images or data are sent to any server
- Perfect for sensitive medical information

## Technical Details

- Uses Tesseract.js v5 for OCR processing
- Responsive design with CSS Grid and Flexbox
- Progressive Web App ready
- Works offline after initial load

## Browser Compatibility

- Modern browsers with ES6+ support
- Mobile Safari (iOS)
- Chrome Mobile (Android)
- Desktop browsers for testing

The solution is lightweight, requires no backend infrastructure, and will work reliably on mobile devices. The OCR processing typically takes 2-5 seconds depending on image quality and device performance.

