#!/bin/bash
# Script to check CFR database contents

echo "=========================================="
echo "CFR Database Status Check"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

if [ ! -f "cfr_data.db" ]; then
    echo "❌ ERROR: cfr_data.db not found!"
    echo ""
    echo "Please run the pipeline first:"
    echo "  ./run_pipeline.sh"
    echo ""
    exit 1
fi

echo "✅ Database file found: cfr_data.db"
echo "   Size: $(ls -lh cfr_data.db | awk '{print $5}')"
echo ""

echo "Database Statistics:"
echo "===================="
echo ""

sqlite3 cfr_data.db <<EOF
.mode column
.headers on
SELECT 'Chapters' as Item, COUNT(*) as Count FROM chapters
UNION ALL
SELECT 'Subchapters', COUNT(*) FROM subchapters
UNION ALL
SELECT 'Parts', COUNT(*) FROM parts
UNION ALL
SELECT 'Sections', COUNT(*) FROM sections
UNION ALL
SELECT 'Chapter Embeddings', COUNT(*) FROM chapter_embeddings
UNION ALL
SELECT 'Subchapter Embeddings', COUNT(*) FROM subchapter_embeddings
UNION ALL
SELECT 'Section Embeddings', COUNT(*) FROM section_embeddings;
EOF

echo ""
echo "Sample Data (First 3 Chapters):"
echo "================================"
sqlite3 cfr_data.db <<EOF
.mode column
.headers on
SELECT id, substr(name, 1, 60) as chapter_name FROM chapters LIMIT 3;
EOF

echo ""
echo "Sample Data (First 5 Sections):"
echo "================================"
sqlite3 cfr_data.db <<EOF
.mode column
.headers on
SELECT id, section_number, substr(subject, 1, 50) as subject FROM sections LIMIT 5;
EOF

echo ""
