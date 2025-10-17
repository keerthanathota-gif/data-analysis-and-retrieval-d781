# 🚀 Quick Start Guide

Get up and running with CFR Agentic AI Application in 5 minutes!

## Step 1: Installation

### Option A: Using the Run Scripts (Recommended)

**Linux/Mac:**
```bash
./run.sh
```

**Windows:**
```bash
# For installation (first time):
install_windows.bat

# To run the app:
run.bat
```

The scripts will:
- Create a virtual environment
- Install all dependencies
- Create necessary directories
- Optionally run the data pipeline
- Start the server

**Note for Windows:** HDBSCAN is optional and requires C++ compiler. The app works perfectly with K-Means (default). See `WINDOWS_SETUP.md` for details.

### Option B: Manual Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p cfr_data output visualizations
```

## Step 2: Run Data Pipeline

**First time setup** - Download and process CFR data:

```bash
python data_pipeline.py
```

This will:
1. Download CFR data from govinfo.gov
2. Parse XML files
3. Store data in SQLite database
4. Generate embeddings (this may take a few minutes)

**Expected output:**
```
================================================================================
Starting CFR Data Pipeline
================================================================================

[1/4] Crawling and downloading CFR data...
  Downloading: https://www.govinfo.gov/bulkdata/CFR/...
  Extracted to ./cfr_data

[2/4] Parsing XML files...
  Parsing: CFR-2025-title16-vol1.xml
    ✓ Saved to output/CFR-2025-title16-vol1.json and .csv

[3/4] Storing data in database...
  ✓ Data stored successfully

[4/4] Generating embeddings...
  ✓ Embeddings generated successfully

================================================================================
Pipeline completed successfully!
================================================================================
```

## Step 3: Start the Server

```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload
```

## Step 4: Access the Application

Open your browser and go to:
- **Web UI**: http://localhost:8000/ui
- **API Docs**: http://localhost:8000/docs

## 🎯 Try These Examples

### Example 1: Semantic Search

1. Go to the **RAG Query** tab
2. Enter: "What are the consumer protection regulations?"
3. Select level: "All Levels"
4. Click "Search"
5. View top 10 relevant results with similarity scores

### Example 2: Clustering Analysis

1. Go to the **Clustering** tab
2. Select level: "Section"
3. Select algorithm: "HDBSCAN"
4. Click "Perform Clustering"
5. Click "Generate Visualizations"
6. Go to **Visualizations** tab to see results

### Example 3: Find Similar Content

1. Go to the **Similarity Search** tab
2. Enter a chapter/subchapter name
3. Select search type
4. Click "Find Similar"
5. View top 10 most similar items

### Example 4: Semantic Analysis

1. Go to the **Analysis** tab
2. Select level: "Chapter"
3. Check all analysis options
4. Click "Run Analysis"
5. View similarity, overlap, and redundancy results

## 📊 Understanding the Results

### Similarity Scores
- **> 85%**: Highly redundant content
- **80-85%**: Overlapping content
- **75-80%**: Similar content
- **< 75%**: Different content

### Cluster Labels
- **Label 0, 1, 2...**: Valid clusters
- **Label -1**: Noise points (don't fit any cluster)

### Visualizations
- **t-SNE 2D**: Shows natural groupings in 2D space
- **PCA 2D**: Shows principal components
- **Interactive 3D**: Explore clusters in 3D
- **Cluster Sizes**: Bar chart of cluster distributions

## 🔌 Using the API

### cURL Examples

**Get Statistics:**
```bash
curl http://localhost:8000/api/pipeline/stats
```

**Query Database:**
```bash
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "consumer protection",
    "level": "all",
    "top_k": 10
  }'
```

**Perform Clustering:**
```bash
curl -X POST http://localhost:8000/api/clustering/cluster \
  -H "Content-Type: application/json" \
  -d '{
    "level": "section",
    "algorithm": "hdbscan"
  }'
```

### Python Examples

```python
import requests

# Query the database
response = requests.post('http://localhost:8000/api/rag/query', json={
    'query': 'What are the consumer protection regulations?',
    'level': 'all',
    'top_k': 10
})
results = response.json()
print(f"Found {len(results['results'])} results")

# Perform clustering
response = requests.post('http://localhost:8000/api/clustering/cluster', json={
    'level': 'section',
    'algorithm': 'hdbscan'
})
clusters = response.json()
print(f"Created {clusters['num_clusters']} clusters")

# Find similar items
response = requests.post('http://localhost:8000/api/rag/similar', json={
    'name': 'Consumer Protection',
    'search_type': 'chapter',
    'top_k': 10
})
similar = response.json()
print(f"Found {len(similar['results'])} similar items")
```

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Add more CFR titles to crawl
CRAWL_URLS = [
    "https://www.govinfo.gov/bulkdata/CFR/2025/title-16/",
    "https://www.govinfo.gov/bulkdata/CFR/2025/title-17/",
]

# Adjust similarity thresholds
SIMILARITY_THRESHOLD = 0.75  # Lower = more results
OVERLAP_THRESHOLD = 0.80
REDUNDANCY_THRESHOLD = 0.85

# Change clustering algorithm
CLUSTERING_ALGORITHM = "hdbscan"  # or "kmeans", "dbscan"
```

## 🐛 Troubleshooting

### Issue: "Module not found"
**Solution:** Make sure you activated the virtual environment and installed dependencies:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: "No data in database"
**Solution:** Run the data pipeline first:
```bash
python data_pipeline.py
```

### Issue: "Port 8000 already in use"
**Solution:** Change the port in `config.py`:
```python
API_PORT = 8001
```

### Issue: "Out of memory during embedding generation"
**Solution:** Process in smaller batches by reducing `batch_size` in `data_pipeline.py`

### Issue: "Download fails"
**Solution:** Check your internet connection and verify the URLs in `config.py` are accessible

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the [API documentation](http://localhost:8000/docs)
- Check out the MCP integration guide
- Customize the configuration for your use case

## 💡 Tips

1. **Start Small**: Begin with one CFR title before scaling up
2. **Use HDBSCAN**: It's the best algorithm for most cases
3. **Adjust Thresholds**: Fine-tune similarity thresholds for your needs
4. **Batch Processing**: Process large datasets in batches
5. **Save Visualizations**: Download visualizations for presentations

## 🆘 Need Help?

- Check the [README.md](README.md) for detailed information
- Review API docs at `/docs`
- Open an issue on GitHub
- Check the logs in the console

---

**Happy analyzing! 🎉**
