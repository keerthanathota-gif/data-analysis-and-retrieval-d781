#!/usr/bin/env python3
"""
Test script to run pipeline and capture errors
"""
import sys
import traceback
sys.path.insert(0, '.')

try:
    print("="*70)
    print("PIPELINE TEST")
    print("="*70)

    print("\n[1] Importing DataPipeline...")
    from app.pipeline.data_pipeline import DataPipeline
    print("[OK] DataPipeline imported")

    print("\n[2] Creating pipeline instance...")
    pipeline = DataPipeline(urls=["https://www.govinfo.gov/bulkdata/CFR/2025/title-16/"])
    print("[OK] Pipeline instance created")

    print("\n[3] Running full pipeline...")
    pipeline.run_full_pipeline()
    print("[OK] Pipeline completed")

    print("\n[4] Getting statistics...")
    stats = pipeline.get_statistics()
    print(f"[OK] Stats: {stats}")

except Exception as e:
    print(f"\n[ERROR] Pipeline test failed!")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    print(f"\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
