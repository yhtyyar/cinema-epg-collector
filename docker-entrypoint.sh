#!/bin/bash
set -e

echo "🚀 Starting Cinema EPG Collector..."

# Wait for dependencies if needed
sleep 2

# Check if .env exists, if not copy from example
if [ ! -f "/app/.env" ]; then
    echo "📋 Creating .env from .env.example..."
    cp /app/.env.example /app/.env
fi

# Run the pipeline if AUTO_RUN_PIPELINE is enabled
if [ "${AUTO_RUN_PIPELINE:-false}" = "true" ]; then
    echo "🔄 Running data collection pipeline..."
    
    # Check if TMDB_API_KEY is set
    if [ -z "${TMDB_API_KEY}" ]; then
        echo "⚠️  Warning: TMDB_API_KEY not set. Movie enrichment will be limited."
    fi
    
    # Run the full pipeline
    echo "📡 Fetching EPG data..."
    python -m epg_collector.cli fetch-epg-cmd || echo "❌ EPG fetch failed, continuing..."
    
    echo "🎬 Filtering movies..."
    python -m epg_collector.cli filter-movies-cmd || echo "❌ Movie filtering failed, continuing..."
    
    echo "🔍 Enriching with TMDB data..."
    python -m epg_collector.cli enrich || echo "❌ Enrichment failed, continuing..."
    
    echo "✅ Pipeline completed!"
else
    echo "⏭️  Skipping pipeline (AUTO_RUN_PIPELINE=false)"
fi

# Start the API server
echo "🌐 Starting API server on port 8000..."
exec uvicorn epg_collector.api.app:app --host 0.0.0.0 --port 8000 --log-level info
