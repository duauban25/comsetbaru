#!/bin/bash

# Activate virtual environment
source .venv/bin/activate

# Set Flask environment variables
export FLASK_APP=app.py
export FLASK_DEBUG=0  # Disable debug mode for better performance

# Kill any existing process on port 8000
echo "Stopping any existing process on port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Start Flask on port 8000
echo "Starting Flask server on port 8000..."

# Open browser after a short delay
(sleep 2 && open http://localhost:8000) &

# Run Flask
flask run --port=8000 --no-debugger --no-reload

echo "\nPress Ctrl+C to stop the server"
