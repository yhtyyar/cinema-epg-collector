#!/usr/bin/env python3
"""
Test script for the data validation and enrichment logic.
"""

import sys
import os
import json
from pathlib import Path

# Add the current directory to the path so we can import epg_collector modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from epg_collector.data_validator import should_run_pipeline, get_data_status
from epg_collector.config import load_config

def test_data_validation():
    print("Testing data validation logic...")
    
    # Clean up any existing test data
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    enriched_path = data_dir / "enriched_movies.json"
    if enriched_path.exists():
        enriched_path.unlink()
    
    # Test 1: No data exists
    print("Test 1: Checking when no data exists")
    should_run, reason = should_run_pipeline(skip_if_exists=True)
    print(f"  Should run: {should_run}, Reason: {reason}")
    assert should_run == True, "Should run when no data exists"
    
    # Test 2: Create some test data
    print("Test 2: Creating test data")
    test_data = [{"id": "1", "title": "Test Movie", "tmdb_data": {"name": "Test Movie", "year": 2023}}]
    enriched_path.write_text(json.dumps(test_data), encoding="utf-8")
    
    # Test 3: Data exists, should skip
    print("Test 3: Checking when data exists")
    should_run, reason = should_run_pipeline(skip_if_exists=True)
    print(f"  Should run: {should_run}, Reason: {reason}")
    assert should_run == False, "Should not run when data exists and skip_if_exists=True"
    
    # Test 4: Data exists, but force run
    print("Test 4: Checking force run when data exists")
    should_run, reason = should_run_pipeline(force_run=True, skip_if_exists=True)
    print(f"  Should run: {should_run}, Reason: {reason}")
    assert should_run == True, "Should run when force_run=True even if data exists"
    
    # Test 5: Data exists, but skip_if_exists=False
    print("Test 5: Checking when data exists but skip_if_exists=False")
    should_run, reason = should_run_pipeline(skip_if_exists=False)
    print(f"  Should run: {should_run}, Reason: {reason}")
    # This should depend on data freshness, but since we just created it, it should be fresh
    # So it should return False (no need to update)
    
    # Clean up test data
    if enriched_path.exists():
        enriched_path.unlink()
    
    print("✅ Data validation tests completed!")

def test_config():
    print("Testing configuration...")
    config = load_config()
    print(f"  Skip enrichment if exists: {config.skip_enrichment_if_exists}")
    print(f"  Auto run pipeline: {config.auto_run_pipeline}")
    print("✅ Configuration test completed!")

def main():
    print("Running comprehensive tests...")
    test_config()
    test_data_validation()
    print("✅ All tests completed successfully!")

if __name__ == "__main__":
    main()