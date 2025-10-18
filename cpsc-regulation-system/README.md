# 🚀 CPSC Regulation System

A comprehensive, production-ready system for analyzing and retrieving CPSC (Consumer Product Safety Commission) regulations with intelligent search, clustering, and role-based authentication.

## ✨ Features

### 🔐 Authentication & Authorization
- **JWT-based authentication** with secure password hashing (bcrypt)
- **Role-based access control** (Admin and User roles)
- **User management** with admin controls
- **Activity logging** for audit trails

### 🔍 Intelligent Search & Retrieval
- **Semantic search** using sentence transformers
- **Similarity matching** with configurable thresholds
- **Multi-level search** (Chapter, Subchapter, Section)
- **Top-K results** with relevance scoring

### 🤖 AI-Powered Analysis
- **FLAN-T5-base LLM** (250M parameters) for intelligent summaries
- **Content-based clustering** with K-Means algorithm
- **Semantic similarity analysis** with overlap detection
- **Redundancy detection** with LLM justifications

### 📊 Admin Dashboard
- **User management** (activate/deactivate, role changes)
- **System statistics** and monitoring
- **Pipeline control** (crawl, parse, embed, analyze)
- **Activity logs** with detailed tracking

### 🎨 Modern UI
- **React frontend** with Material-UI components
- **Responsive design** for all devices
- **Role-based navigation** and protected routes
- **Real-time updates** and progress tracking

## 🏗️ Architecture

```
cpsc-regulation-system/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── auth/              # Authentication modules
│   │   ├── admin/             # Admin routes
│   │   ├── search/            # Search routes
│   │   ├── models/            # Database models & schemas
│   │   ├── services/          # Business logic
│   │   ├── pipeline/          # Data processing
│   │   └── utils/             # Utilities
│   ├── requirements.txt       # Python dependencies
│   └── run.py                 # Main entry point
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── pages/            # Page components
│   │   ├── contexts/         # React contexts
│   │   └── services/         # API services
│   ├── package.json          # Node dependencies
│   └── public/               # Static assets
└── docs/                     # Documentation
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **npm** or **yarn**

### 1. Backend Setup

```bash
# Navigate to backend directory
cd cpsc-regulation-system/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the backend server
python run.py
```

The backend will be available at:
- **API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Interactive Docs**: http://localhost:8000/api/redoc

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd cpsc-regulation-system/frontend

# Install dependencies
npm install

# Start development server
npm start
```

The frontend will be available at:
- **React App**: http://localhost:3000

### 3. Default Credentials

The system creates a default admin user on first startup:
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: Admin

**⚠️ Important**: Change the default password in production!

## 📖 Usage Guide

### For Users

1. **Login** with your credentials
2. **Search** regulations using natural language queries
3. **View** detailed section information
4. **Find** similar sections based on content

### For Admins

1. **Login** with admin credentials
2. **Manage users** (activate/deactivate, change roles)
3. **Monitor system** statistics and activity logs
4. **Run pipeline** to crawl and process new regulations
5. **Trigger analysis** and clustering operations

## 🔧 Configuration

### Backend Configuration

Edit `backend/app/config.py`:

```python
# Database
DATABASE_URL = "sqlite:///cpsc_data.db"

# Authentication
SECRET_KEY = "your-secret-key-change-in-production"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# CORS
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000"
]
```

### Frontend Configuration

Create `frontend/.env`:

```env
REACT_APP_API_URL=http://localhost:8000
```

## 🗄️ Database Schema

### Core Tables
- **users** - User accounts and authentication
- **activity_logs** - User activity tracking
- **chapters** - CFR chapters
- **subchapters** - CFR subchapters
- **parts** - CFR parts
- **sections** - CFR sections (main content)

### Analysis Tables
- **similarity_results** - Semantic similarity analysis
- **clusters** - Clustering results
- **parity_checks** - Data integrity checks

### Embedding Tables
- **chapter_embeddings** - Vector embeddings for chapters
- **subchapter_embeddings** - Vector embeddings for subchapters
- **section_embeddings** - Vector embeddings for sections

## 🔌 API Endpoints

### Authentication (`/auth`)
- `POST /auth/signup` - Register new user
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user info
- `PUT /auth/me` - Update user profile
- `POST /auth/logout` - User logout

### Search (`/search`)
- `POST /search/query` - Semantic search
- `GET /search/similar/{name}` - Find similar sections
- `GET /search/section/{id}` - Get section details
- `GET /search/sections` - List sections

### Admin (`/admin`)
- `GET /admin/stats` - System statistics
- `GET /admin/users` - List all users
- `PUT /admin/users/{id}/role` - Update user role
- `PUT /admin/users/{id}/activate` - Activate user
- `PUT /admin/users/{id}/deactivate` - Deactivate user
- `GET /admin/activity-logs` - View activity logs
- `POST /admin/pipeline/run` - Run data pipeline
- `GET /admin/pipeline/status` - Get pipeline status
- `POST /admin/pipeline/reset` - Reset pipeline
- `POST /admin/analysis/run` - Run analysis
- `POST /admin/clustering/run` - Run clustering

## 🧪 Testing

### Backend Tests

```bash
cd backend
python -m pytest tests/
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 🚀 Deployment

### Production Backend

```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Production Frontend

```bash
# Build for production
npm run build

# Serve with a web server (nginx, Apache, etc.)
# The build files will be in the 'build' directory
```

### Docker Deployment

```dockerfile
# Backend Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "run.py"]

# Frontend Dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

## 🔒 Security Features

- **JWT tokens** with configurable expiration
- **Password hashing** using bcrypt
- **CORS protection** with configurable origins
- **Role-based access control**
- **Input validation** and sanitization
- **SQL injection protection** via SQLAlchemy ORM
- **XSS protection** via React's built-in escaping

## 📊 Performance

- **Vector similarity search** using sentence transformers
- **Database indexing** on frequently queried fields
- **Pagination** for large result sets
- **Background processing** for heavy operations
- **Caching** for frequently accessed data

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Change port in config.py
   API_PORT = 8001
   ```

2. **Database errors**
   ```bash
   # Reset database
   python scripts/reset_database.py
   ```

3. **Module not found**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt --upgrade
   ```

4. **Frontend build errors**
   ```bash
   # Clear cache and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

### Logs

- **Backend logs**: Check console output or configure logging
- **Frontend logs**: Check browser console
- **Database logs**: Enable SQLAlchemy echo in config

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation in the `docs/` folder
- Review the API documentation at `/api/docs`

---

**Built with ❤️ for CPSC regulation analysis and retrieval**