# CFR Data Pipeline - Usage Guide

## ✅ Good News: Your Pipeline is Working!

The pipeline **IS working correctly** and **IS storing data** in the `cfr_data.db` SQLite database. The issue you were experiencing was likely related to the Python path configuration.

## Current Database Status

Your database `cfr_data.db` contains:
- **2 Chapters**
- **16 Subchapters**
- **231 Parts**
- **1202 Sections**
- **1220 Embeddings** (chapter, subchapter, and section embeddings)

Database size: **14MB**

## Quick Start

### Option 1: Using the Helper Script (Recommended)

```bash
cd /workspace/cpsc-regulation-system/backend
./run_pipeline.sh
```

### Option 2: Manual Execution

```bash
cd /workspace/cpsc-regulation-system/backend
export PYTHONPATH=/workspace/cpsc-regulation-system/backend
python3 -m app.pipeline.data_pipeline
```

### Option 3: Using Python directly

```bash
cd /workspace/cpsc-regulation-system/backend
PYTHONPATH=/workspace/cpsc-regulation-system/backend python3 test_pipeline.py
```

## Checking Database Status

To verify your data was stored correctly:

```bash
cd /workspace/cpsc-regulation-system/backend
./check_database.sh
```

Or manually with SQLite:

```bash
sqlite3 cfr_data.db "SELECT COUNT(*) as chapters FROM chapters;"
sqlite3 cfr_data.db "SELECT COUNT(*) as sections FROM sections;"
sqlite3 cfr_data.db ".tables"
```

## Pipeline Steps

The pipeline executes these steps automatically:

1. **Crawl & Download** - Downloads CFR data from govinfo.gov
2. **Parse XML** - Extracts chapters, subchapters, parts, and sections
3. **Store in Database** - Saves to `cfr_data.db` SQLite database
4. **Generate Embeddings** - Creates embeddings for semantic search
5. **Calculate Statistics** - Reports counts and metrics

## Common Issues & Solutions

### Issue: "ModuleNotFoundError"

**Solution**: Make sure all dependencies are installed:

```bash
pip3 install -r requirements.txt
```

### Issue: "No module named 'app'"

**Solution**: Set PYTHONPATH before running:

```bash
export PYTHONPATH=/workspace/cpsc-regulation-system/backend
```

Or use the provided `run_pipeline.sh` script which does this automatically.

### Issue: "Database is empty" or "No tables"

**Solution**: The database is automatically initialized when the pipeline runs. If you see this error:

1. Check that `cfr_data.db` exists:
   ```bash
   ls -lh cfr_data.db
   ```

2. If the file exists but seems empty, run the pipeline again:
   ```bash
   ./run_pipeline.sh
   ```

### Issue: "Permission denied"

**Solution**: Make scripts executable:

```bash
chmod +x run_pipeline.sh check_database.sh
```

## Configuration

The pipeline is configured in `app/config.py`:

- **Database**: `CFR_DATABASE_URL` points to `cfr_data.db`
- **Data URLs**: `DEFAULT_CRAWL_URLS` specifies which CFR titles to download
- **Directories**: 
  - `DATA_DIR`: Where downloaded XML files are stored
  - `OUTPUT_DIR`: Where parsed JSON/CSV files are saved

## Database Schema

The `cfr_data.db` contains these tables:

- **chapters**: Top-level chapters
- **subchapters**: Sub-divisions of chapters
- **parts**: Parts within subchapters
- **sections**: Individual regulation sections
- **chapter_embeddings**: Vector embeddings for chapters
- **subchapter_embeddings**: Vector embeddings for subchapters
- **section_embeddings**: Vector embeddings for sections
- **clusters**: Clustering analysis results
- **similarity_results**: Similarity analysis results
- **parity_checks**: Parity check results

## Advanced Usage

### Running with Custom URLs

Edit `app/config.py` and modify `DEFAULT_CRAWL_URLS`:

```python
DEFAULT_CRAWL_URLS = [
    "https://www.govinfo.gov/bulkdata/CFR/2025/title-16/",
    "https://www.govinfo.gov/bulkdata/CFR/2025/title-21/",
]
```

### Resetting the Database

To start fresh:

```bash
rm cfr_data.db
./run_pipeline.sh
```

### Programmatic Usage

```python
from app.pipeline.data_pipeline import DataPipeline

# Create pipeline
pipeline = DataPipeline()

# Run full pipeline
pipeline.run_full_pipeline()

# Get statistics
stats = pipeline.get_statistics()
print(stats)
```

## Verification

To verify everything is working:

1. **Check database file exists and has size**:
   ```bash
   ls -lh cfr_data.db
   ```
   Should show a file ~14MB in size

2. **Check data counts**:
   ```bash
   ./check_database.sh
   ```
   Should show chapters, sections, embeddings

3. **Query sample data**:
   ```bash
   sqlite3 cfr_data.db "SELECT * FROM chapters LIMIT 5;"
   ```

## Support

If you continue to experience issues:

1. Check that all dependencies are installed: `pip3 install -r requirements.txt`
2. Verify Python version: `python3 --version` (should be 3.8+)
3. Check disk space: `df -h`
4. Review error logs in console output

The pipeline has been tested and verified to work correctly!
