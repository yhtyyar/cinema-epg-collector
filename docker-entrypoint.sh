#!/bin/bash
# This entrypoint script is provided for Docker deployments only.
# For manual deployment on Ubuntu, please follow the instructions in README.md

set -e

echo "🚀 Starting Cinema EPG Collector..."

# Check if .env exists, if not copy from example
if [ ! -f "/app/.env" ]; then
    echo "📋 Creating .env from .env.example..."
    cp /app/.env.example /app/.env
fi

# Start the API server
echo "🌐 Starting API server on port 8000..."
exec uvicorn epg_collector.api.app:app --host 0.0.0.0 --port 8000 --log-level info --access-log
