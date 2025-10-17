# 🎯 Complete Setup & Test Guide

## ✅ Project Successfully Organized!

All files have been reorganized into a professional, clean directory structure.

---

## 📁 New Directory Structure

```
cfr-agentic-app/                    # ← You are here
│
├── run.py                          # ⭐ MAIN ENTRY POINT - Run this!
├── requirements.txt                # Dependencies
├── README.md                       # Main documentation
├── mcp_server.json                # MCP configuration
│
├── app/                            # 📦 Main application package
│   ├── __init__.py
│   ├── config.py                   # ⚙️ Configuration
│   ├── database.py                 # 🗄️ SQLAlchemy models
│   ├── main.py                     # 🌐 FastAPI application
│   │
│   ├── services/                   # 🔧 Business logic services
│   │   ├── __init__.py
│   │   ├── analysis_service.py     # Similarity, overlap, redundancy
│   │   ├── clustering_service.py   # K-Means clustering
│   │   ├── embedding_service.py    # Sentence embeddings
│   │   ├── llm_service.py          # FLAN-T5-base LLM
│   │   ├── rag_service.py          # RAG queries
│   │   └── visualization_service.py # Chart generation
│   │
│   ├── pipeline/                   # 📊 Data processing pipeline
│   │   ├── __init__.py
│   │   ├── crawler.py              # Download CFR data
│   │   ├── cfr_parser.py           # Parse XML files
│   │   └── data_pipeline.py        # Orchestrate pipeline
│   │
│   └── static/                     # 🎨 Frontend files
│       └── index.html              # Web UI
│
├── scripts/                        # 🛠️ Utility scripts
│   ├── __init__.py
│   ├── reset_database.py           # Reset DB and data
│   └── migrate_database.py         # Migrate DB schema
│
├── docs/                           # 📚 Documentation
│   ├── PROJECT_STRUCTURE.md
│   ├── LLM_UPGRADE.md
│   ├── CLUSTER_SUMMARY_COMPARISON.md
│   └── ... (other docs)
│
└── [Runtime directories - created automatically]
    ├── cfr_data/                   # Downloaded CFR files
    ├── output/                     # Parsed JSON/CSV
    ├── visualizations/             # Generated charts
    └── cfr_data.db                 # SQLite database
```

---

## 🚀 How to Run

### Step 1: Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Note:** First run will download FLAN-T5-base (~900MB). This takes 30-60 seconds and only happens once.

---

### Step 2: Start the Application

```bash
python run.py
```

**Expected Output:**
```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║         CFR Agentic AI Application Starting...               ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

🚀 Server will start on http://0.0.0.0:8000
📊 UI available at http://localhost:8000/ui

Press CTRL+C to stop the server
═════════════════════════════════════════════════════════════════

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Loading LLM model: google/flan-t5-base
INFO:     LLM model (FLAN-T5-base) loaded on cpu
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

### Step 3: Open the Web UI

```
http://localhost:8000/ui
```

You should see a beautiful, modern interface with 5 tabs:
- **Pipeline** - Download and process CFR data
- **Analysis** - Semantic similarity checks
- **Clustering** - Group related regulations
- **RAG Query** - Search and retrieve
- **Visualizations** - View charts

---

## 🧪 Testing the Application

### Test 1: Pipeline with Real-Time Progress

```
1. Go to "Pipeline" tab
2. Keep default URL:
   https://www.govinfo.gov/bulkdata/CFR/2025/title-16/
3. Click "Run Complete Pipeline"
4. Watch the progress bar update in real-time!

Expected:
✅ Progress bar: 0% → 17% → 33% → 50% → 67% → 83% → 100%
✅ Stats automatically display when complete
✅ Shows number of chapters, parts, subchapters, sections
```

**What's Happening:**
1. Downloading ZIP files from govinfo.gov
2. Extracting and parsing XML
3. Storing in SQLite database
4. Generating embeddings with Sentence-Transformers
5. Calculating statistics

---

### Test 2: Content-Based Clustering

```
1. Wait for pipeline to complete
2. Go to "Clustering" tab
3. Select "Section Level"
4. Keep default clusters: 5
5. Click "Perform Clustering"
6. Wait for LLM to generate summaries (20-30 seconds)

Expected Results:
✅ Cluster names like:
   "Privacy Protection and Data Security"
   "Financial Reporting and Disclosure"
   "Product Safety Standards"

✅ Detailed summaries like:
   "This cluster encompasses consumer privacy protection
    requirements including explicit consent for data
    collection, mandatory disclosure of information handling
    practices, encryption standards for personal data
    storage, user access and deletion rights, breach
    notification procedures, and enforcement provisions
    with penalties for violations."
```

**Why This Is Amazing:**
- ❌ **Before:** "Privacy sections grouped together."
- ✅ **Now:** Specific, detailed, actionable summaries!

---

### Test 3: Analysis with LLM Justifications

```
1. Go to "Analysis" tab
2. Select "Section Level"
3. Click "Run Analysis"
4. Wait for results (30-60 seconds)
5. Click on any result row

Expected:
✅ Modal opens with:
   - Similarity score
   - Overlap data
   - Redundancy check
   - Parity check
   - LLM-generated justification explaining why
```

---

### Test 4: RAG Query

```
1. Go to "RAG Query" tab
2. Enter query: "privacy protection requirements"
3. Click "Search"

Expected:
✅ Top-10 most relevant sections
✅ Similarity scores
✅ Section subjects as titles (not "Section 0")
✅ Click section to see full text + hierarchy
```

---

### Test 5: Find Similar

```
1. RAG Query tab → "Find Similar" section
2. Enter a section name (e.g., "Subchapter A")
3. Click "Find Similar"

Expected:
✅ Top-10 similar items
✅ Similarity scores
✅ Full hierarchical context
```

---

## 🔧 Maintenance Commands

### Reset Everything

```bash
python scripts/reset_database.py
```

**Prompts for confirmation**, then:
- Deletes `cfr_data.db`
- Removes `cfr_data/` directory
- Removes `output/` directory
- Removes `visualizations/` directory

**Use this when:**
- Schema changed
- Want to start fresh
- Testing different data

---

### Migrate Database (Keep Data)

```bash
python scripts/migrate_database.py
```

**Adds new columns** without deleting data:
- `sections.section_label`
- `sections.citation`
- `clusters.summary`
- `clusters.name`
- `similarity_results.overlap_data`
- `similarity_results.llm_justification`
- `parity_checks.llm_justification`

**Use this when:**
- Schema updated
- Want to preserve existing data
- Adding new features

---

## 📊 What's Different After Reorganization

### Import Paths Changed

**Before (Flat Structure):**
```python
from config import DATA_DIR
from database import Chapter
from embedding_service import embedding_service
```

**After (Organized Structure):**
```python
from app.config import DATA_DIR
from app.database import Chapter
from app.services.embedding_service import EmbeddingService
```

### Entry Point Changed

**Before:**
```bash
python main.py  # ❌ Won't work anymore
```

**After:**
```bash
python run.py  # ✅ Correct way
```

### Scripts Moved

**Before:**
```bash
python reset_database.py  # In root
```

**After:**
```bash
python scripts/reset_database.py  # In scripts/
```

---

## ✅ Verification Checklist

After running the application, verify:

- [ ] Server starts without errors
- [ ] FLAN-T5-base loads successfully
- [ ] UI opens at http://localhost:8000/ui
- [ ] All 5 tabs are visible
- [ ] Pipeline can be run
- [ ] Progress bar updates in real-time
- [ ] Stats display automatically
- [ ] Clustering generates detailed summaries
- [ ] LLM justifications appear in analysis
- [ ] RAG query returns results
- [ ] Section details open in modals
- [ ] Visualizations are generated

---

## 🎯 Key Features Summary

### 1. **LLM: FLAN-T5-base** 🤖
- 250M parameters
- Instruction-tuned
- High-quality summaries
- Better than DialoGPT

### 2. **Content-Based Summaries** 📊
- Analyzes actual text (not just names)
- Fetches section content from DB
- Combines 5 sections per cluster
- LLM generates specific summaries

### 3. **Real-Time Progress** 📈
- Live progress bar
- Status updates every 2 seconds
- 6 pipeline steps tracked
- Auto-display stats on completion

### 4. **Enhanced UI** 🎨
- Click-to-expand results
- Modal dialogs for details
- Modern gradient design
- Responsive layout

### 5. **Professional Structure** 🏗️
- Clean package organization
- Logical file grouping
- Easy to navigate
- Scalable architecture

---

## 🐛 Common Issues & Solutions

### Issue: Port 8000 Already in Use

```bash
# Option 1: Change port
# Edit app/config.py:
API_PORT = 8001

# Option 2: Kill process
# Linux/Mac:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
# Note the PID, then:
taskkill /PID <pid> /F
```

---

### Issue: Module Not Found

```bash
# Ensure you're in project root
pwd  # Should show: /path/to/cfr-agentic-app

# Run from root
python run.py  # ✅ Correct
cd app && python main.py  # ❌ Wrong

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

---

### Issue: Database Schema Error

```bash
# Error: "no such column: sections.section_label"

# Solution: Reset database
python scripts/reset_database.py
# Type: yes
```

---

### Issue: Out of Memory

```bash
# Reduce batch size in app/config.py:
CHUNK_SIZE = 256  # Default: 512

# Or process fewer items
# (Edit the URL to get less data)
```

---

## 📚 Documentation Files

- **README.md** - Main documentation (you are here)
- **PROJECT_STRUCTURE.md** - Detailed architecture
- **SETUP_GUIDE.md** - This file
- **LLM_UPGRADE.md** - FLAN-T5-base details
- **CLUSTER_SUMMARY_COMPARISON.md** - Before/after examples
- **RESTART_GUIDE.md** - Server restart instructions

---

## 🎊 Summary

### What Was Done:

✅ **Organized all files** into logical directory structure  
✅ **Updated all imports** to use new paths  
✅ **Created `run.py`** as single entry point  
✅ **Moved scripts** to `scripts/` directory  
✅ **Moved docs** to `docs/` directory  
✅ **Created `__init__.py`** files for proper packages  
✅ **Fixed config paths** to use absolute paths  
✅ **Cleaned up duplicates** from root directory  
✅ **Wrote comprehensive docs** for all features  

### Result:

🚀 **Professional, production-ready application!**

---

## 🎯 Next Steps

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run application
python run.py

# 3. Open UI
http://localhost:8000/ui

# 4. Test pipeline → clustering → analysis → RAG

# 5. Enjoy amazing cluster summaries! ✨
```

---

**Everything is ready to go! 🚀**

Just run `python run.py` and start exploring CFR data with AI! 🎉
