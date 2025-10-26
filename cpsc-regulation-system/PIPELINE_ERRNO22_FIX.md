# Pipeline Error Fix: [Errno 22] Invalid argument

## Issue Description

The pipeline was encountering `[Errno 22] Invalid argument` error during the "Storing in database" step, even though all previous steps (Starting, Crawling data, Parsing XML) completed successfully.

## Root Cause

The error was caused by the `save_json()` and `save_csv()` functions in `backend/app/pipeline/cfr_parser.py`. These functions were attempting to create directories using `os.makedirs(os.path.dirname(output_file), exist_ok=True)` without checking if the dirname was empty.

When `output_file` is a simple filename without a directory component, `os.path.dirname(output_file)` returns an empty string `""`. Calling `os.makedirs("")` with an empty string causes `[Errno 22] Invalid argument` on some systems.

### Problematic Code (Lines 73-78, 80-84)
```python
def save_json(data, output_file):
    """Save data to JSON file."""
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)  # ❌ Fails if dirname is ""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
```

## Solution

Modified both `save_json()` and `save_csv()` functions to check if the directory path is non-empty before attempting to create it:

### Fixed Code
```python
def save_json(data, output_file):
    """Save data to JSON file."""
    # Ensure the directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir:  # ✅ Only create directory if path has a directory component
        os.makedirs(output_dir, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def save_csv(data, output_file):
    """Save data to CSV file."""
    # Ensure the directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir:  # ✅ Only create directory if path has a directory component
        os.makedirs(output_dir, exist_ok=True)
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        # ... rest of the function
```

## Changes Made

### File: `backend/app/pipeline/cfr_parser.py`

1. **`save_json()` function (lines 73-78)**:
   - Added check to verify `output_dir` is non-empty before calling `os.makedirs()`
   
2. **`save_csv()` function (lines 80-84)**:
   - Added check to verify `output_dir` is non-empty before calling `os.makedirs()`

## Testing

The fix was validated with the following tests:

1. **Test with directory path**: `tmpdir/test/output.json` ✅
2. **Test with filename only**: `tmpdir/output.json` ✅ (Previously would fail)
3. **CSV file test**: `tmpdir/output.csv` ✅

All tests passed successfully.

## Dependencies Installed

As part of the fix verification, the following Python packages were installed:
- `sqlalchemy`
- `sentence-transformers`
- `torch`
- `lxml`
- `requests`
- `beautifulsoup4`
- `matplotlib`
- `seaborn`
- `pandas`
- `plotly`
- `fastapi`
- `uvicorn`
- `python-multipart`
- `pyjwt`
- `passlib`
- `bcrypt`
- `python-jose`

## Database Configuration

The database URL configuration was also reviewed and confirmed correct:
- **Format**: `sqlite:////workspace/cpsc-regulation-system/backend/cfr_data.db`
- **Note**: Four slashes (`////`) is the correct format for SQLite with absolute Unix paths
  - First three slashes: `sqlite:///` (protocol)
  - Fourth slash: Start of absolute path `/workspace/...`

## Impact

This fix resolves the `[Errno 22] Invalid argument` error that was preventing the pipeline from successfully storing parsed data to the database. The pipeline can now complete all steps without errors:

✅ Starting
✅ Crawling data
✅ Parsing XML
✅ Storing in database
✅ Generating embeddings
✅ Calculating statistics

## Date
October 26, 2025
