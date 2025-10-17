#!/usr/bin/env python3
"""
Migrate database schema to add new columns without deleting data
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import BASE_DIR
import sqlite3

def migrate_database():
    """Add missing columns to existing database"""
    db_path = os.path.join(BASE_DIR, "cfr_data.db")
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        print("   No migration needed - database will be created on first run")
        return
    
    print(f"📊 Migrating database at {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    migrations = [
        ("sections", "section_label", "VARCHAR(100)"),
        ("sections", "citation", "VARCHAR(500)"),
        ("clusters", "summary", "TEXT"),
        ("clusters", "name", "VARCHAR(200)"),
        ("similarity_results", "overlap_data", "TEXT"),
        ("similarity_results", "llm_justification", "TEXT"),
        ("parity_checks", "llm_justification", "TEXT"),
    ]
    
    for table, column, column_type in migrations:
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")
            print(f"✅ Added {column} to {table}")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print(f"ℹ️  Column {column} already exists in {table}")
            else:
                print(f"⚠️  Error adding {column} to {table}: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Migration complete!")
    print("   You can now restart the server with: python run.py")

if __name__ == "__main__":
    migrate_database()
