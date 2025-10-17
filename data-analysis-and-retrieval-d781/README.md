# 🚀 CFR Agentic AI Application

A comprehensive AI-powered application for analyzing Code of Federal Regulations (CFR) data with semantic similarity, clustering, and RAG capabilities.

## ✨ Key Features

- 🤖 **FLAN-T5-base LLM** (250M parameters) for intelligent summaries
- 📊 **Content-Based Clustering** - Analyzes actual regulatory text
- 🔍 **Semantic Analysis** - Similarity, overlap, redundancy checks
- 🔎 **RAG Search** - Natural language query interface
- 📈 **Real-Time Progress** - Live pipeline status tracking
- 🎨 **Beautiful Web UI** - Modern, responsive interface
- 📉 **Interactive Visualizations** - t-SNE, PCA, Plotly charts

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python run.py
```

### 3. Open Your Browser

```
http://localhost:8000/ui
```

**That's it!** 🎉

---

## 📁 Project Structure

```
cfr-agentic-app/
│
├── run.py ⭐                   # Main entry point - RUN THIS!
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── SETUP_GUIDE.md             # Detailed setup instructions
├── START_HERE.md              # Quick reference
├── mcp_server.json            # MCP configuration
│
├── app/                        # Main application package
│   ├── config.py              # Configuration settings
│   ├── database.py            # Database models
│   ├── main.py                # FastAPI application
│   │
│   ├── services/              # Business logic
│   │   ├── analysis_service.py
│   │   ├── clustering_service.py
│   │   ├── embedding_service.py
│   │   ├── llm_service.py
│   │   ├── rag_service.py
│   │   └── visualization_service.py
│   │
│   ├── pipeline/              # Data processing
│   │   ├── crawler.py
│   │   ├── cfr_parser.py
│   │   └── data_pipeline.py
│   │
│   └── static/                # Frontend
│       └── index.html
│
├── scripts/                    # Utility scripts
│   ├── reset_database.py      # Reset DB and data
│   └── migrate_database.py    # Migrate DB schema
│
└── docs/                       # Documentation
    └── [detailed documentation files]
```

---

## 🧪 Quick Test

After starting the server:

### 1. **Pipeline Tab**
- Keep default URL or enter custom
- Click "Run Complete Pipeline"
- Watch real-time progress bar!

### 2. **Clustering Tab**
- Select "Section Level"
- Click "Perform Clustering"
- See content-based summaries powered by FLAN-T5-base!

**Example Output:**
```
Cluster: "Privacy Protection and Data Security"

Summary: "This cluster encompasses consumer privacy protection
requirements including explicit consent for data collection,
mandatory disclosure of information handling practices,
encryption standards for personal data storage, user access
and deletion rights, breach notification procedures, and
enforcement provisions with penalties for violations."
```

### 3. **Analysis Tab**
- Run similarity analysis
- Click results to see LLM justifications

### 4. **RAG Query**
- Search: "privacy protection"
- See top-10 relevant results

---

## 🔧 Maintenance

### Reset Everything

```bash
python scripts/reset_database.py
```

This removes:
- Database file
- Downloaded data
- Generated outputs
- Visualizations

### Migrate Database (Keep Data)

```bash
python scripts/migrate_database.py
```

Adds new columns without deleting existing data.

---

## 📊 What Makes This Special

### Content-Based Summaries

**Before (Generic):**
```
"Privacy sections grouped together."
```

**After (AI-Powered):**
```
"Consumer privacy protection requirements including explicit
consent mechanisms, mandatory disclosure obligations, encryption
standards, breach notification, and enforcement penalties."
```

**5-10x more useful!** ✨

### Real-Time Progress

Live updates during data processing:
```
[████████████░░░░] 67%
Generating embeddings... (67%)
```

### LLM Justifications

Every analysis result includes AI-generated explanations of why items are similar, redundant, or different.

---

## 🎯 Technologies

- **FastAPI** - Modern web framework
- **SQLAlchemy** - Database ORM
- **Sentence-Transformers** - Text embeddings
- **FLAN-T5-base** - 250M parameter LLM
- **scikit-learn** - K-Means clustering
- **Plotly/Matplotlib** - Visualizations

---

## 📚 Documentation

- **START_HERE.md** - Quick reference guide
- **SETUP_GUIDE.md** - Detailed setup and testing
- **docs/** - Complete technical documentation

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Change port in app/config.py
API_PORT = 8001
```

### Module Not Found

```bash
# Make sure you're in project root
python run.py

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Database Errors

```bash
# Reset database
python scripts/reset_database.py
```

---

## 🎊 Features Summary

✅ FLAN-T5-base LLM (250M parameters)  
✅ Content-based cluster summaries  
✅ Real-time pipeline progress  
✅ Semantic similarity analysis  
✅ K-Means clustering  
✅ RAG queries  
✅ Interactive visualizations  
✅ Beautiful web UI  
✅ REST API with auto docs  

---

## 🚀 Get Started

```bash
pip install -r requirements.txt
python run.py
```

**Open:** http://localhost:8000/ui

**Enjoy!** ✨

---

## 📖 API Documentation

Interactive API docs available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🎯 Use Cases

- **Compliance Officers:** Find all regulations on specific topics
- **Legal Researchers:** Semantic search across CFR
- **Policy Analysts:** Cluster and analyze regulatory themes
- **Developers:** REST API for integration

---

**Professional, production-ready CFR analysis platform!** 🎉
