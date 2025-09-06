#!/bin/bash
# Build and run locally
docker build -t ocr-test .
docker run -p 10000:10000 ocr-test

# Visit http://localhost:10000

