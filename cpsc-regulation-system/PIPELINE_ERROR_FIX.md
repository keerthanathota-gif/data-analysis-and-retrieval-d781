# Pipeline Database Error Fix - [Errno 22] Invalid Argument

## Problem Analysis

**Error:** `[Errno 22] Invalid argument` during "Storing in database" step

### Root Causes

This error typically occurs on **Windows systems** when:

1. **File Path Issues:**
   - Invalid characters in the path
   - Incorrect path separators (mixing `/` and `\`)
   - Path contains special characters or colons in wrong places
   - Database file is locked by another process

2. **SQLite Specific Issues:**
   - Database URL format incorrect for Windows
   - File permissions problem
   - Disk space issues
   - Database file corruption

3. **Python/SQLAlchemy Issues:**
   - SQLite URI not properly escaped
   - Connection pool exhaustion
   - Transaction deadlock

---

## Current Configuration

```python
# From config.py (line 23)
CFR_DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'cfr_data.db')}"
```

### Potential Issues:

1. **Triple Slash on Windows:**
   - On Windows, `sqlite:///C:/path/file.db` can cause issues
   - Should be `sqlite:///path/to/file.db` or use proper escaping

2. **Path Separators:**
   - Windows uses backslashes `\`
   - SQLite URLs need forward slashes `/`

---

## Solutions

### Solution 1: Fix Database URL Path (Recommended)

Update `config.py` to handle Windows paths properly:

```python
import os
from pathlib import Path

# Base directory (project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Fix database paths for cross-platform compatibility
def get_sqlite_url(db_name):
    """Generate proper SQLite URL for any platform"""
    db_path = os.path.join(BASE_DIR, db_name)
    # Convert to absolute path and use forward slashes
    db_path = os.path.abspath(db_path).replace('\\', '/')
    # On Windows, don't include drive letter in URL
    if os.name == 'nt':  # Windows
        return f"sqlite:///{db_path}"
    else:  # Unix/Linux/Mac
        return f"sqlite:///{db_path}"

# Database configuration - Dual databases for clean separation
AUTH_DATABASE_URL = get_sqlite_url('auth.db')
CFR_DATABASE_URL = get_sqlite_url('cfr_data.db')
```

---

### Solution 2: Use Absolute Paths with Proper Escaping

```python
import os
from urllib.parse import quote

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Encode special characters in path
def safe_db_url(db_name):
    db_path = os.path.join(BASE_DIR, db_name)
    db_path = os.path.abspath(db_path)
    # Use pathlib for platform-agnostic paths
    from pathlib import Path
    db_path = Path(db_path).as_posix()  # Convert to forward slashes
    return f"sqlite:///{db_path}"

AUTH_DATABASE_URL = safe_db_url('auth.db')
CFR_DATABASE_URL = safe_db_url('cfr_data.db')
```

---

### Solution 3: Add Connection Parameters

Update `cfr_database.py` to add SQLite connection parameters:

```python
from sqlalchemy import create_engine
from app.config import CFR_DATABASE_URL
import os

# Add connection parameters for SQLite
connect_args = {}
if os.name == 'nt':  # Windows specific settings
    connect_args = {
        "check_same_thread": False,
        "timeout": 30  # Increase timeout
    }

engine = create_engine(
    CFR_DATABASE_URL, 
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600    # Recycle connections every hour
)
```

---

### Solution 4: Check File Permissions

```python
def ensure_db_directory():
    """Ensure database directory exists and is writable"""
    from app.config import BASE_DIR
    import os
    
    db_dir = BASE_DIR
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    # Test write permissions
    test_file = os.path.join(db_dir, '.write_test')
    try:
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print(f"✓ Database directory is writable: {db_dir}")
    except Exception as e:
        print(f"✗ Cannot write to database directory: {e}")
        raise

# Call before initializing database
ensure_db_directory()
```

---

## Implementation Steps

### Step 1: Update `config.py`

```python
"""
Configuration file for CFR Agentic AI Application
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory (project root) - using Path for better cross-platform support
BASE_DIR = str(Path(__file__).parent.parent.absolute())

# Database configuration helper
def get_sqlite_url(db_name):
    """Generate proper SQLite URL for cross-platform compatibility"""
    db_path = Path(BASE_DIR) / db_name
    db_path_str = str(db_path.absolute())
    
    # Convert backslashes to forward slashes for SQLite
    db_path_str = db_path_str.replace('\\', '/')
    
    return f"sqlite:///{db_path_str}"

# Database configuration - Dual databases for clean separation
AUTH_DATABASE_URL = get_sqlite_url('auth.db')
CFR_DATABASE_URL = get_sqlite_url('cfr_data.db')

# Legacy support
DATABASE_URL = CFR_DATABASE_URL

# ... rest of config remains the same ...
```

---

### Step 2: Update `cfr_database.py`

```python
"""
CFR Database models for CPSC Regulation System
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json
import os
from app.config import CFR_DATABASE_URL

Base = declarative_base()

# ... (all model classes remain the same) ...

# Database initialization with proper connection handling
connect_args = {"check_same_thread": False}
if os.name == 'nt':  # Additional Windows-specific settings
    connect_args['timeout'] = 30

engine = create_engine(
    CFR_DATABASE_URL, 
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_cfr_db():
    """Initialize CFR database and create all tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print(f"✓ CFR database initialized at: {CFR_DATABASE_URL}")
    except Exception as e:
        print(f"✗ Error initializing CFR database: {e}")
        raise

# ... rest remains the same ...
```

---

### Step 3: Add Error Handling in Pipeline

Update `data_pipeline.py` line 184-233:

```python
def store_in_database(self, parsed_data_list: List[Dict[str, Any]]):
    """Store parsed data in SQLite database"""
    db = SessionLocal()
    
    try:
        # Test database connection first
        db.execute("SELECT 1")
        print("  ✓ Database connection verified")
        
        for parsed_data in parsed_data_list:
            for chapter_data in tqdm(parsed_data.get("chapters", []), desc="  Processing chapters"):
                try:
                    # Create chapter
                    chapter = Chapter(name=chapter_data["chapter_name"])
                    db.add(chapter)
                    db.flush()  # Get chapter ID
                    
                    # Process subchapters
                    for subchapter_data in chapter_data.get("subchapters", []):
                        subchapter = Subchapter(
                            chapter_id=chapter.id,
                            name=subchapter_data["subchapter_name"]
                        )
                        db.add(subchapter)
                        db.flush()
                        
                        # Process parts
                        for part_data in subchapter_data.get("parts", []):
                            part = Part(
                                subchapter_id=subchapter.id,
                                heading=part_data["heading"]
                            )
                            db.add(part)
                            db.flush()
                            
                            # Process sections
                            for section_data in part_data.get("sections", []):
                                section = Section(
                                    part_id=part.id,
                                    section_number=section_data.get("section_number", ""),
                                    subject=section_data.get("subject", ""),
                                    text=section_data.get("text", ""),
                                    citation=section_data.get("citation", ""),
                                    section_label=section_data.get("section_label", "")
                                )
                                db.add(section)
                    
                    # Commit after each chapter for better error isolation
                    db.commit()
                    
                except Exception as e:
                    print(f"    ✗ Error processing chapter '{chapter_data.get('chapter_name', 'Unknown')}': {e}")
                    db.rollback()
                    # Continue with next chapter
                    continue
        
        print("  ✓ Data stored successfully")
        
    except Exception as e:
        db.rollback()
        print(f"  ✗ Error storing data: {e}")
        print(f"  Database URL: {CFR_DATABASE_URL}")
        raise
    finally:
        db.close()
```

---

## Quick Fix Script

Create `fix_database_path.py` in the backend directory:

```python
#!/usr/bin/env python3
"""
Quick fix for database path issues
Run this to test and fix database configuration
"""
import os
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database_path():
    """Test database path configuration"""
    print("=" * 60)
    print("Database Path Configuration Test")
    print("=" * 60)
    
    try:
        from app.config import CFR_DATABASE_URL, AUTH_DATABASE_URL, BASE_DIR
        
        print(f"\n📁 Base Directory:")
        print(f"   {BASE_DIR}")
        print(f"   Exists: {os.path.exists(BASE_DIR)}")
        print(f"   Writable: {os.access(BASE_DIR, os.W_OK)}")
        
        print(f"\n🗄️  CFR Database URL:")
        print(f"   {CFR_DATABASE_URL}")
        
        # Extract path from URL
        db_path = CFR_DATABASE_URL.replace('sqlite:///', '')
        print(f"\n📄 Database File Path:")
        print(f"   {db_path}")
        print(f"   Exists: {os.path.exists(db_path)}")
        if os.path.exists(db_path):
            print(f"   Size: {os.path.getsize(db_path)} bytes")
            print(f"   Writable: {os.access(db_path, os.W_OK)}")
        
        # Test SQLAlchemy connection
        print(f"\n🔌 Testing Database Connection...")
        from sqlalchemy import create_engine
        engine = create_engine(CFR_DATABASE_URL, echo=False)
        with engine.connect() as conn:
            result = conn.execute("SELECT 1").scalar()
            print(f"   ✓ Connection successful! Result: {result}")
        
        print(f"\n✅ All checks passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database_path()
    sys.exit(0 if success else 1)
```

Run with:
```bash
cd /workspace/cpsc-regulation-system/backend
python3 fix_database_path.py
```

---

## Platform-Specific Notes

### Windows
- Use forward slashes in SQLite URLs
- Be careful with drive letters (C:, D:, etc.)
- Check antivirus isn't blocking database file

### Linux/Mac
- Forward slashes work natively
- Check file permissions (chmod 666 for database file)
- Ensure directory exists

---

## Testing the Fix

After applying the fixes:

```bash
# 1. Test database configuration
cd /workspace/cpsc-regulation-system/backend
python3 fix_database_path.py

# 2. Test pipeline
python3 -m app.pipeline.data_pipeline

# 3. Check if error is resolved
# Look for "✓ Data stored successfully" message
```

---

## If Error Persists

### Check 1: Database File Permissions
```bash
ls -la /workspace/cpsc-regulation-system/backend/*.db
chmod 666 /workspace/cpsc-regulation-system/backend/cfr_data.db
```

### Check 2: Disk Space
```bash
df -h /workspace/cpsc-regulation-system/backend/
```

### Check 3: Process Locks
```bash
lsof /workspace/cpsc-regulation-system/backend/cfr_data.db
```

### Check 4: Database Integrity
```bash
sqlite3 /workspace/cpsc-regulation-system/backend/cfr_data.db "PRAGMA integrity_check;"
```

---

## Summary

**Primary Fix:** Update `config.py` to use `pathlib.Path` and convert backslashes to forward slashes for SQLite URLs.

**Secondary Fixes:**
- Add connection parameters for better error handling
- Improve error messages with more context
- Add database connection verification
- Commit more frequently to isolate errors

This should resolve the `[Errno 22] Invalid argument` error completely!
