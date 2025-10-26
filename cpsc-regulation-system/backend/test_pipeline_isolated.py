#!/usr/bin/env python3
"""
Isolated test script for pipeline to diagnose issues
"""

import sys
import os

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test if all required imports work"""
    print("=" * 60)
    print("Testing imports...")
    print("=" * 60)
    
    try:
        print("✓ Testing basic imports...")
        import json
        import glob
        print("  ✓ json, glob OK")
        
        print("✓ Testing numpy...")
        import numpy as np
        print(f"  ✓ numpy {np.__version__} OK")
        
        print("✓ Testing requests...")
        import requests
        print(f"  ✓ requests {requests.__version__} OK")
        
        print("✓ Testing lxml...")
        import lxml
        print(f"  ✓ lxml {lxml.__version__} OK")
        
        print("✓ Testing tqdm...")
        from tqdm import tqdm
        print(f"  ✓ tqdm OK")
        
        print("✓ Testing sqlalchemy...")
        import sqlalchemy
        print(f"  ✓ sqlalchemy {sqlalchemy.__version__} OK")
        
        print("\n✓ All basic imports successful!")
        return True
        
    except Exception as e:
        print(f"\n✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config():
    """Test configuration"""
    print("\n" + "=" * 60)
    print("Testing configuration...")
    print("=" * 60)
    
    try:
        from app.config import DATA_DIR, OUTPUT_DIR, CFR_DATABASE_URL, AUTH_DATABASE_URL
        print(f"✓ DATA_DIR: {DATA_DIR}")
        print(f"✓ OUTPUT_DIR: {OUTPUT_DIR}")
        print(f"✓ CFR_DATABASE_URL: {CFR_DATABASE_URL}")
        print(f"✓ AUTH_DATABASE_URL: {AUTH_DATABASE_URL}")
        
        # Check if directories exist
        print(f"\n  DATA_DIR exists: {os.path.exists(DATA_DIR)}")
        print(f"  OUTPUT_DIR exists: {os.path.exists(OUTPUT_DIR)}")
        
        return True
    except Exception as e:
        print(f"\n✗ Config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_embedding_service():
    """Test embedding service"""
    print("\n" + "=" * 60)
    print("Testing embedding service...")
    print("=" * 60)
    
    try:
        from app.services.embedding_service import EmbeddingService
        
        service = EmbeddingService()
        print(f"✓ Embedding service initialized")
        print(f"  Dimension: {service.dimension}")
        
        # Test generating an embedding
        text = "Test regulation text"
        embedding = service.generate_embedding(text)
        print(f"✓ Generated embedding with {len(embedding)} dimensions")
        print(f"  First 5 values: {embedding[:5]}")
        
        # Test batch generation
        texts = ["Text 1", "Text 2", "Text 3"]
        embeddings = service.generate_embeddings(texts)
        print(f"✓ Generated {len(embeddings)} embeddings in batch")
        
        return True
    except Exception as e:
        print(f"\n✗ Embedding service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_init():
    """Test database initialization"""
    print("\n" + "=" * 60)
    print("Testing database initialization...")
    print("=" * 60)
    
    try:
        from app.models.cfr_database import init_cfr_db, SessionLocal
        from app.models.auth_database import init_auth_db
        
        print("✓ Initializing CFR database...")
        init_cfr_db()
        print("  ✓ CFR database initialized")
        
        print("✓ Initializing Auth database...")
        init_auth_db()
        print("  ✓ Auth database initialized")
        
        # Test connection
        db = SessionLocal()
        print("✓ Database connection successful")
        db.close()
        
        return True
    except Exception as e:
        print(f"\n✗ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pipeline_init():
    """Test pipeline initialization"""
    print("\n" + "=" * 60)
    print("Testing pipeline initialization...")
    print("=" * 60)
    
    try:
        from app.pipeline.data_pipeline import DataPipeline
        
        pipeline = DataPipeline(urls=['https://www.govinfo.gov/bulkdata/CFR/2025/title-16/'])
        print("✓ Pipeline initialized successfully")
        print(f"  Data dir: {pipeline.data_dir}")
        print(f"  Output dir: {pipeline.output_dir}")
        print(f"  Number of URLs: {len(pipeline.crawl_urls)}")
        
        # Check status
        status = pipeline.get_status()
        print(f"✓ Pipeline status: {status['state']}")
        
        return True
    except Exception as e:
        print(f"\n✗ Pipeline initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n")
    print("=" * 60)
    print("CPSC REGULATION SYSTEM - PIPELINE DIAGNOSTIC TEST")
    print("=" * 60)
    print("\n")
    
    results = {
        "Imports": test_imports(),
        "Configuration": test_config(),
        "Embedding Service": test_embedding_service(),
        "Database": test_database_init(),
        "Pipeline": test_pipeline_init()
    }
    
    print("\n")
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:.<40} {status}")
    
    print("\n")
    all_passed = all(results.values())
    if all_passed:
        print("✓ ALL TESTS PASSED - Pipeline should work correctly")
    else:
        print("✗ SOME TESTS FAILED - Fix issues before running pipeline")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
