#!/usr/bin/env python3
"""
Test script to verify the new host configuration.
"""

import sys
import os

# Add the current directory to the path so we can import epg_collector modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from epg_collector.config import load_config

def main():
    print("Verifying host configuration...")
    
    # Load configuration
    config = load_config()
    
    print(f"API Host: {config.api_host}")
    print(f"API Port: {config.api_port}")
    
    # Verify the values are what we expect
    assert config.api_host == "194.35.48.118", f"Expected API host 194.35.48.118, got {config.api_host}"
    assert config.api_port == 8000, f"Expected API port 8000, got {config.api_port}"
    
    print("✅ Host configuration verification passed!")
    print("The API will be accessible at http://194.35.48.118:8000")

if __name__ == "__main__":
    main()