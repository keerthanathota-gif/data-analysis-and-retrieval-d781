#!/usr/bin/env python3
"""
End-to-End Test Script for CFR Agentic AI Application
Tests all components without actually running the server
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all module imports"""
    print("\n" + "="*60)
    print("TEST 1: Module Imports")
    print("="*60)
    
    tests = [
        ("Config", "from app.config import DATA_DIR, DATABASE_URL, API_PORT"),
        ("Database Models", "from app.database import Chapter, Section, init_db"),
        ("Embedding Service", "from app.services.embedding_service import EmbeddingService"),
        ("Analysis Service", "from app.services.analysis_service import AnalysisService"),
        ("Clustering Service", "from app.services.clustering_service import ClusteringService"),
        ("RAG Service", "from app.services.rag_service import RAGService"),
        ("LLM Service", "from app.services.llm_service import LLMService"),
        ("Visualization Service", "from app.services.visualization_service import VisualizationService"),
        ("Crawler", "from app.pipeline.crawler import download_and_extract_zip"),
        ("Parser", "from app.pipeline.cfr_parser import parse_chapter_subchapter_part_sections"),
        ("Data Pipeline", "from app.pipeline.data_pipeline import DataPipeline"),
        ("FastAPI App", "from app.main import app"),
    ]
    
    passed = 0
    failed = 0
    errors = []
    
    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"✅ {name}")
            passed += 1
        except Exception as e:
            print(f"❌ {name}: {str(e)[:50]}")
            failed += 1
            errors.append((name, str(e)))
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0, errors

def test_file_structure():
    """Test that all required files exist"""
    print("\n" + "="*60)
    print("TEST 2: File Structure")
    print("="*60)
    
    required_files = [
        "run.py",
        "requirements.txt",
        "README.md",
        "app/__init__.py",
        "app/config.py",
        "app/database.py",
        "app/main.py",
        "app/services/__init__.py",
        "app/services/embedding_service.py",
        "app/services/analysis_service.py",
        "app/services/clustering_service.py",
        "app/services/rag_service.py",
        "app/services/llm_service.py",
        "app/services/visualization_service.py",
        "app/pipeline/__init__.py",
        "app/pipeline/crawler.py",
        "app/pipeline/cfr_parser.py",
        "app/pipeline/data_pipeline.py",
        "app/static/index.html",
        "scripts/reset_database.py",
        "scripts/migrate_database.py",
    ]
    
    passed = 0
    failed = 0
    missing = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
            passed += 1
        else:
            print(f"❌ {file_path} - MISSING")
            failed += 1
            missing.append(file_path)
    
    print(f"\nResults: {passed} files found, {failed} missing")
    return failed == 0, missing

def test_config_paths():
    """Test that config paths are correct"""
    print("\n" + "="*60)
    print("TEST 3: Configuration Paths")
    print("="*60)
    
    try:
        from app.config import DATA_DIR, OUTPUT_DIR, VISUALIZATIONS_DIR, DATABASE_URL
        
        print(f"DATA_DIR: {DATA_DIR}")
        print(f"OUTPUT_DIR: {OUTPUT_DIR}")
        print(f"VISUALIZATIONS_DIR: {VISUALIZATIONS_DIR}")
        print(f"DATABASE_URL: {DATABASE_URL}")
        
        # Check if paths are absolute
        import os
        if os.path.isabs(DATA_DIR):
            print("✅ DATA_DIR is absolute path")
        else:
            print("⚠️  DATA_DIR is relative path")
            
        if os.path.isabs(OUTPUT_DIR):
            print("✅ OUTPUT_DIR is absolute path")
        else:
            print("⚠️  OUTPUT_DIR is relative path")
        
        return True, None
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False, str(e)

def test_static_files():
    """Test that static files exist and are accessible"""
    print("\n" + "="*60)
    print("TEST 4: Static Files")
    print("="*60)
    
    static_file = "app/static/index.html"
    
    if os.path.exists(static_file):
        size = os.path.getsize(static_file)
        print(f"✅ {static_file} exists ({size:,} bytes)")
        
        # Check if file has content
        if size > 1000:
            print("✅ File has substantial content")
            return True, None
        else:
            print("⚠️  File seems too small")
            return False, "index.html is too small"
    else:
        print(f"❌ {static_file} not found")
        return False, "index.html missing"

def test_syntax():
    """Test Python syntax of all files"""
    print("\n" + "="*60)
    print("TEST 5: Python Syntax")
    print("="*60)
    
    import py_compile
    
    python_files = []
    for root, dirs, files in os.walk("app"):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    
    passed = 0
    failed = 0
    errors = []
    
    for file_path in python_files:
        try:
            py_compile.compile(file_path, doraise=True)
            print(f"✅ {file_path}")
            passed += 1
        except Exception as e:
            print(f"❌ {file_path}: {str(e)[:50]}")
            failed += 1
            errors.append((file_path, str(e)))
    
    print(f"\nResults: {passed} files valid, {failed} with errors")
    return failed == 0, errors

def main():
    """Run all tests"""
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + " "*10 + "CFR Agentic AI - End-to-End Tests" + " "*15 + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    results = []
    
    # Run all tests
    results.append(("File Structure", *test_file_structure()))
    results.append(("Python Syntax", *test_syntax()))
    results.append(("Configuration", *test_config_paths()))
    results.append(("Static Files", *test_static_files()))
    results.append(("Module Imports", *test_imports()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    all_passed = True
    for test_name, passed, error_info in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not passed and error_info:
            all_passed = False
            print(f"  Error: {error_info}")
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Application is ready to run.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run application: python run.py")
        print("3. Open browser: http://localhost:8000/ui")
    else:
        print("⚠️  SOME TESTS FAILED - Review errors above")
        print("\nCommon fixes:")
        print("1. Install missing packages: pip install -r requirements.txt")
        print("2. Check file paths in error messages")
        print("3. Ensure all files are in correct locations")
    print("="*60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
