#!/usr/bin/env python3
"""
Verification script for the new configuration features.
"""

import sys
import os

# Add the current directory to the path so we can import epg_collector modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from epg_collector.config import load_config

def main():
    print("Verifying configuration...")
    
    # Load configuration
    config = load_config()
    
    print(f"API Host: {config.api_host}")
    print(f"API Port: {config.api_port}")
    print(f"Skip Enrichment If Exists: {config.skip_enrichment_if_exists}")
    
    # Verify the values are what we expect
    assert config.api_host == "0.0.0.0", f"Expected API host 0.0.0.0, got {config.api_host}"
    assert config.api_port == 8000, f"Expected API port 8000, got {config.api_port}"
    assert config.skip_enrichment_if_exists == True, f"Expected skip_enrichment_if_exists True, got {config.skip_enrichment_if_exists}"
    
    print("✅ Configuration verification passed!")

if __name__ == "__main__":
    main()