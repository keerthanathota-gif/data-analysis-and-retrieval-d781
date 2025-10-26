#!/bin/bash

# System Status Check Script for CPSC Regulation System

echo "================================================================"
echo "CPSC REGULATION SYSTEM - STATUS CHECK"
echo "================================================================"
echo ""

# Check if backend is running
echo "1. Backend Service Status:"
echo "   -----------------------"
if pgrep -f "uvicorn.*app.main:app" > /dev/null; then
    echo "   ✅ Backend is RUNNING"
    ps aux | grep "uvicorn.*app.main:app" | grep -v grep | awk '{print "   PID: "$2}'
else
    echo "   ❌ Backend is NOT running"
    echo "   To start: cd backend && python3 run.py"
fi
echo ""

# Check if port 8000 is in use
echo "2. Port 8000 Status:"
echo "   -----------------"
if netstat -tuln 2>/dev/null | grep ":8000 " > /dev/null || ss -tuln 2>/dev/null | grep ":8000 " > /dev/null; then
    echo "   ✅ Port 8000 is IN USE (backend listening)"
else
    echo "   ⚠️  Port 8000 is FREE (backend not listening)"
fi
echo ""

# Check databases
echo "3. Database Files:"
echo "   ---------------"
cd /workspace/cpsc-regulation-system/backend
if [ -f "auth.db" ]; then
    SIZE=$(ls -lh auth.db | awk '{print $5}')
    echo "   ✅ auth.db exists ($SIZE)"
else
    echo "   ❌ auth.db NOT FOUND"
fi

if [ -f "cfr_data.db" ]; then
    SIZE=$(ls -lh cfr_data.db | awk '{print $5}')
    echo "   ✅ cfr_data.db exists ($SIZE)"
    
    # Check data in database
    echo ""
    echo "4. Database Contents:"
    echo "   -----------------"
    CHAPTERS=$(sqlite3 cfr_data.db "SELECT COUNT(*) FROM chapters;" 2>/dev/null || echo "0")
    SECTIONS=$(sqlite3 cfr_data.db "SELECT COUNT(*) FROM sections;" 2>/dev/null || echo "0")
    CHAPTER_EMBS=$(sqlite3 cfr_data.db "SELECT COUNT(*) FROM chapter_embeddings;" 2>/dev/null || echo "0")
    SECTION_EMBS=$(sqlite3 cfr_data.db "SELECT COUNT(*) FROM section_embeddings;" 2>/dev/null || echo "0")
    
    echo "   Chapters: $CHAPTERS"
    echo "   Sections: $SECTIONS"
    echo "   Chapter Embeddings: $CHAPTER_EMBS"
    echo "   Section Embeddings: $SECTION_EMBS"
    
    if [ "$CHAPTERS" -gt 0 ] && [ "$SECTION_EMBS" -gt 0 ]; then
        echo ""
        echo "   ✅ Database has data and embeddings!"
    elif [ "$CHAPTERS" -gt 0 ]; then
        echo ""
        echo "   ⚠️  Database has data but NO embeddings"
    else
        echo ""
        echo "   ⚠️  Database is EMPTY - need to run pipeline"
    fi
else
    echo "   ❌ cfr_data.db NOT FOUND"
    echo ""
    echo "4. Database Contents:"
    echo "   -----------------"
    echo "   ⚠️  No database - need to run pipeline first"
fi
echo ""

# Check data directory
echo "5. Data Directory:"
echo "   ---------------"
if [ -d "cfr_data" ]; then
    FILE_COUNT=$(find cfr_data -type f 2>/dev/null | wc -l)
    if [ "$FILE_COUNT" -gt 0 ]; then
        echo "   ✅ cfr_data/ exists with $FILE_COUNT file(s)"
        XML_COUNT=$(find cfr_data -name "*.xml" 2>/dev/null | wc -l)
        ZIP_COUNT=$(find cfr_data -name "*.zip" 2>/dev/null | wc -l)
        echo "   XML files: $XML_COUNT"
        echo "   ZIP files: $ZIP_COUNT"
    else
        echo "   ⚠️  cfr_data/ exists but is EMPTY"
    fi
else
    echo "   ❌ cfr_data/ does NOT exist"
fi
echo ""

# Check Python dependencies
echo "6. Python Dependencies:"
echo "   --------------------"
python3 -c "import numpy; print('   ✅ numpy installed')" 2>/dev/null || echo "   ❌ numpy NOT installed"
python3 -c "import sqlalchemy; print('   ✅ sqlalchemy installed')" 2>/dev/null || echo "   ❌ sqlalchemy NOT installed"
python3 -c "import requests; print('   ✅ requests installed')" 2>/dev/null || echo "   ❌ requests NOT installed"
python3 -c "import lxml; print('   ✅ lxml installed')" 2>/dev/null || echo "   ❌ lxml NOT installed"
python3 -c "import fastapi; print('   ✅ fastapi installed')" 2>/dev/null || echo "   ❌ fastapi NOT installed"
echo ""

# Summary
echo "================================================================"
echo "SUMMARY"
echo "================================================================"

ISSUES=0

if ! pgrep -f "uvicorn.*app.main:app" > /dev/null; then
    echo "❌ Backend is not running - start it with: cd backend && python3 run.py"
    ISSUES=$((ISSUES+1))
fi

if [ ! -f "cfr_data.db" ]; then
    echo "❌ No database found - run pipeline to create data"
    ISSUES=$((ISSUES+1))
elif [ "$CHAPTERS" -eq 0 ]; then
    echo "❌ Database is empty - run pipeline to populate data"
    ISSUES=$((ISSUES+1))
elif [ "$SECTION_EMBS" -eq 0 ]; then
    echo "⚠️  No embeddings found - pipeline may not have completed"
    ISSUES=$((ISSUES+1))
fi

if ! python3 -c "import numpy, sqlalchemy, requests, lxml, fastapi" 2>/dev/null; then
    echo "❌ Missing Python dependencies - run: pip install -r requirements.txt"
    ISSUES=$((ISSUES+1))
fi

if [ $ISSUES -eq 0 ]; then
    echo ""
    echo "✅ ✅ ✅ SYSTEM READY ✅ ✅ ✅"
    echo ""
    echo "Everything looks good! You can:"
    echo "  1. Access the UI at: http://localhost:8000/ui"
    echo "  2. Access the API at: http://localhost:8000/api/docs"
    echo "  3. Run queries in the RAG Query tab"
else
    echo ""
    echo "⚠️  Found $ISSUES issue(s) - see above for details"
    echo ""
    echo "Quick fix:"
    echo "  1. Install dependencies: cd backend && pip install -r requirements.txt"
    echo "  2. Start backend: cd backend && python3 run.py"
    echo "  3. Run pipeline from UI or run diagnostic: python3 test_pipeline_isolated.py"
fi

echo ""
echo "================================================================"
