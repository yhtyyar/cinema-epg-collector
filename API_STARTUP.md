# API Startup Without Data Collection

This document explains how to start the Cinema EPG Collector API without automatically collecting data, which allows for faster startup and manual control over when data collection occurs.

## Changes Made

1. **Default Configuration**: The `AUTO_RUN_PIPELINE` setting in `.env.example` is now set to `false` by default.
2. **API Endpoint**: A new endpoint `POST /api/collect-data` has been added to manually trigger data collection.
3. **Graceful Handling**: The API now gracefully handles missing data files and returns empty results instead of errors.

## How It Works

### Default Behavior (Recommended)
When `AUTO_RUN_PIPELINE=false` (default):
- The API starts immediately without collecting data
- Existing data files (if any) are served
- Missing data files result in empty responses rather than errors
- Data collection can be triggered manually when needed

### Manual Data Collection
To collect data after API startup:
```bash
curl -X POST http://localhost:8000/api/collect-data
```

This endpoint starts the data collection process in the background and returns immediately.

### Automatic Data Collection (Legacy)
To restore the previous behavior, set `AUTO_RUN_PIPELINE=true` in your `.env` file.

## Benefits

1. **Faster Startup**: The API is available immediately without waiting for data collection
2. **Better Control**: You can control exactly when data collection occurs
3. **Resource Management**: Data collection can be scheduled during off-peak hours
4. **Error Isolation**: API availability is not dependent on data collection success

## Testing

A test script `test_api_startup.py` is included to verify that the API works correctly without data files.

## Usage Examples

### Development
```bash
# Start API without data collection
uvicorn epg_collector.api.app:app --host 0.0.0.0 --port 8000

# Later, trigger data collection manually
curl -X POST http://localhost:8000/api/collect-data
```

### Production
In production environments, you might want to:
1. Start the API service
2. Trigger data collection via a scheduled task or deployment script
3. Monitor the data collection progress through logs