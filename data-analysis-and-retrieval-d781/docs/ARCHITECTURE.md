# 🏗️ System Architecture

## Overview

The CFR Agentic AI Application is built with a modular, layered architecture that separates concerns and enables easy maintenance and extension.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER INTERFACE                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │          Modern Web UI (HTML/CSS/JavaScript)                  │  │
│  │  - Data Pipeline Tab    - RAG Query Tab                       │  │
│  │  - Analysis Tab         - Similarity Search Tab               │  │
│  │  - Clustering Tab       - Visualizations Tab                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP/REST API
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         FASTAPI BACKEND                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    API Endpoints Layer                        │  │
│  │  - Pipeline Endpoints    - Clustering Endpoints               │  │
│  │  - Analysis Endpoints    - RAG Endpoints                      │  │
│  │  - Visualization Endpoints                                    │  │
│  │  - MCP Endpoints (Model Context Protocol)                     │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
┌──────────────────────┐ ┌──────────────────┐ ┌─────────────────────┐
│   SERVICE LAYER      │ │  SERVICE LAYER   │ │   SERVICE LAYER     │
│                      │ │                  │ │                     │
│  Data Pipeline       │ │  Analysis        │ │  Clustering         │
│  - Crawler           │ │  - Similarity    │ │  - HDBSCAN         │
│  - Parser            │ │  - Overlap       │ │  - K-Means         │
│  - Embeddings        │ │  - Redundancy    │ │  - DBSCAN          │
│  - Storage           │ │  - Parity        │ │  - Visualization   │
└──────────────────────┘ └──────────────────┘ └─────────────────────┘
                    │               │               │
                    └───────────────┼───────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      CORE SERVICES LAYER                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Embedding Service (sentence-transformers)                    │  │
│  │  - Generate embeddings for text                               │  │
│  │  - Compute similarity scores                                  │  │
│  │  - Find similar items                                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  RAG Service                                                  │  │
│  │  - Query-based retrieval                                      │  │
│  │  - Context generation                                         │  │
│  │  - Similarity search by name                                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Visualization Service                                        │  │
│  │  - 2D/3D cluster plots                                        │  │
│  │  - Similarity matrices                                        │  │
│  │  - HTML reports                                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA ACCESS LAYER                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                SQLAlchemy ORM                                 │  │
│  │  - Chapter, Subchapter, Part, Section Models                 │  │
│  │  - Embedding Models                                           │  │
│  │  - Cluster, Similarity, ParityCheck Models                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         DATABASE LAYER                               │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    SQLite Database                            │  │
│  │  - Structured CFR data                                        │  │
│  │  - Semantic embeddings                                        │  │
│  │  - Analysis results                                           │  │
│  │  - Clustering results                                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
         ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
         │  XML Files   │  │  JSON Files  │  │  CSV Files   │
         │  (Input)     │  │  (Output)    │  │  (Output)    │
         └──────────────┘  └──────────────┘  └──────────────┘
```

## Data Flow

### 1. Data Ingestion Pipeline

```
govinfo.gov → Crawler → ZIP Download → XML Extraction
                                            │
                                            ▼
                    XML Parser → Structured Data (JSON/CSV)
                                            │
                                            ▼
                    Database Storage → SQLite (chapters, sections, etc.)
                                            │
                                            ▼
                    Embedding Generation → Vector Embeddings (384-dim)
                                            │
                                            ▼
                    Store Embeddings → SQLite (embedding tables)
```

### 2. Analysis Pipeline

```
User Input → Select Level (chapter/subchapter/section)
                            │
                            ▼
            Retrieve Data & Embeddings from Database
                            │
                ┌───────────┼───────────┐
                │           │           │
                ▼           ▼           ▼
        Similarity   Overlap    Redundancy    Parity
        Analysis     Detection  Check         Check
                │           │           │
                └───────────┼───────────┘
                            ▼
            Store Results in Database
                            │
                            ▼
            Return Results to User
```

### 3. Clustering Pipeline

```
User Input → Select Level & Algorithm
                            │
                            ▼
            Retrieve Embeddings from Database
                            │
                            ▼
            Apply Clustering Algorithm
            (HDBSCAN/K-Means/DBSCAN)
                            │
                            ▼
            Generate Cluster Labels & Centroids
                            │
                            ▼
            Store Clusters in Database
                            │
                            ▼
            Generate Visualizations
                            │
                            ▼
            Return Results & Visualizations
```

### 4. RAG Query Pipeline

```
User Query (Natural Language)
            │
            ▼
Generate Query Embedding
            │
            ▼
Compute Similarity with All Items
            │
            ▼
Rank by Similarity Score
            │
            ▼
Return Top-K Results with Context
            │
            ▼
Display to User
```

### 5. Similarity Search Pipeline

```
User Input (Item Name)
            │
            ▼
Find Item in Database
            │
            ▼
Retrieve Item Embedding
            │
            ▼
Compare with All Other Items
            │
            ▼
Rank by Similarity
            │
            ▼
Return Top-K Similar Items
```

## Component Details

### 1. Data Layer
**Files:** `database.py`, `config.py`
- **Purpose**: Define database schema and models
- **Technologies**: SQLAlchemy ORM, SQLite
- **Features**:
  - 10 database tables
  - Automatic relationship management
  - Indexing for fast queries
  - JSON storage for embeddings

### 2. Data Processing Layer
**Files:** `crawler.py`, `cfr_parser.py`, `data_pipeline.py`
- **Purpose**: Ingest and process CFR data
- **Technologies**: requests, lxml, tqdm
- **Features**:
  - Automatic download and extraction
  - XML parsing with XPath
  - Batch processing
  - Progress tracking

### 3. AI/ML Layer
**Files:** `embedding_service.py`, `analysis_service.py`, `clustering_service.py`
- **Purpose**: AI-powered analysis and clustering
- **Technologies**: sentence-transformers, HDBSCAN, scikit-learn
- **Features**:
  - Semantic embedding generation
  - Similarity computation
  - Multiple clustering algorithms
  - Automatic parameter tuning

### 4. RAG Layer
**Files:** `rag_service.py`
- **Purpose**: Retrieval-augmented generation
- **Technologies**: sentence-transformers, NumPy
- **Features**:
  - Query-based semantic search
  - Context generation
  - Similarity-based retrieval
  - Multi-level search

### 5. Visualization Layer
**Files:** `visualization_service.py`
- **Purpose**: Generate visual representations
- **Technologies**: Matplotlib, Seaborn, Plotly
- **Features**:
  - 2D/3D scatter plots
  - Heatmaps
  - Interactive visualizations
  - HTML reports

### 6. API Layer
**Files:** `main.py`
- **Purpose**: RESTful API endpoints
- **Technologies**: FastAPI, Uvicorn
- **Features**:
  - 20+ endpoints
  - Automatic API documentation
  - CORS support
  - Background tasks
  - MCP compatibility

### 7. Presentation Layer
**Files:** `static/index.html`
- **Purpose**: User interface
- **Technologies**: HTML, CSS, JavaScript
- **Features**:
  - 6 functional tabs
  - Responsive design
  - Real-time updates
  - Beautiful animations

## Design Patterns

### 1. Service Pattern
Each major functionality is encapsulated in a service:
- `embedding_service`
- `analysis_service`
- `clustering_service`
- `rag_service`
- `visualization_service`

### 2. Repository Pattern
Database access is abstracted through SQLAlchemy ORM

### 3. Factory Pattern
Different clustering algorithms can be selected at runtime

### 4. Singleton Pattern
Services are instantiated once and reused

### 5. Dependency Injection
FastAPI's dependency injection for database sessions

## Scalability Considerations

### Current Limitations
- Single-process execution
- In-memory clustering
- Local file storage
- Single SQLite database

### Scaling Options
1. **Horizontal Scaling**: Add load balancer + multiple API instances
2. **Database**: Migrate to PostgreSQL for better concurrency
3. **Caching**: Add Redis for embedding cache
4. **Queue**: Add Celery for background tasks
5. **Storage**: Use S3/MinIO for visualizations
6. **Search**: Add Elasticsearch for full-text search

## Security Architecture

### Current Security
- Local-only deployment
- No authentication required
- CORS enabled for development
- Input validation via Pydantic

### Production Security Recommendations
1. Add JWT authentication
2. Implement rate limiting
3. Use HTTPS (TLS/SSL)
4. Add request logging
5. Implement RBAC (Role-Based Access Control)
6. Add API key management
7. Enable CORS selectively

## Performance Optimization

### Current Optimizations
- Batch embedding generation
- Database indexing
- Result caching
- Async API endpoints
- Lazy loading of relationships

### Future Optimizations
- Vector similarity search (FAISS/Annoy)
- Incremental clustering
- Parallel processing
- GPU acceleration for embeddings
- CDN for static assets

## Monitoring & Observability

### Recommended Additions
1. **Logging**: Structured logging with correlation IDs
2. **Metrics**: Prometheus metrics for API
3. **Tracing**: OpenTelemetry for distributed tracing
4. **Alerting**: Alert on failures and performance issues
5. **Dashboard**: Grafana dashboard for monitoring

## Testing Strategy

### Recommended Tests
1. **Unit Tests**: Individual service functions
2. **Integration Tests**: API endpoints
3. **Load Tests**: Performance under load
4. **E2E Tests**: Full user workflows
5. **Security Tests**: Penetration testing

## Deployment Options

### 1. Local Development
```bash
python main.py
```

### 2. Docker
```dockerfile
FROM python:3.9
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

### 3. Cloud (AWS/GCP/Azure)
- Deploy as containerized service
- Use managed database
- Add CDN for static assets
- Use object storage for files

### 4. Kubernetes
- Deploy as microservices
- Scale API layer independently
- Use persistent volumes for data

---

**Architecture designed for:**
- ✅ Modularity
- ✅ Maintainability  
- ✅ Scalability
- ✅ Extensibility
- ✅ Performance
