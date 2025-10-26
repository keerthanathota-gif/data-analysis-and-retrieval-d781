#!/bin/bash
# Script to run the CFR data pipeline

echo "=========================================="
echo "CFR Data Pipeline Runner"
echo "=========================================="
echo ""

# Set the working directory
cd "$(dirname "$0")"

# Set PYTHONPATH to include the backend directory
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Run the pipeline
python3 -m app.pipeline.data_pipeline

echo ""
echo "=========================================="
echo "Pipeline execution completed!"
echo "=========================================="
echo ""
echo "To check the database, run:"
echo "  sqlite3 cfr_data.db 'SELECT COUNT(*) FROM chapters; SELECT COUNT(*) FROM sections;'"
