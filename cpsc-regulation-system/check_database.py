#!/usr/bin/env python3
"""
Check database contents - Works on both Windows and Linux
"""

import sqlite3
import sys
import os

def check_database(db_path):
    """Check contents of the CFR database"""
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        print("\nPlease provide the correct path to cfr_data.db")
        return False
    
    print("=" * 70)
    print("DATABASE CONTENTS CHECK")
    print("=" * 70)
    print(f"\n📁 Database: {db_path}")
    
    # Get file size
    size_bytes = os.path.getsize(db_path)
    size_mb = size_bytes / (1024 * 1024)
    print(f"📊 File size: {size_mb:.2f} MB ({size_bytes:,} bytes)")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n" + "=" * 70)
        print("TABLE COUNTS")
        print("=" * 70)
        
        # Check each table
        tables = [
            ('chapters', 'Chapters'),
            ('subchapters', 'Subchapters'),
            ('parts', 'Parts'),
            ('sections', 'Sections/Regulations'),
            ('chapter_embeddings', 'Chapter Embeddings'),
            ('subchapter_embeddings', 'Subchapter Embeddings'),
            ('section_embeddings', 'Section Embeddings')
        ]
        
        results = {}
        for table_name, display_name in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                results[table_name] = count
                
                status = "✅" if count > 0 else "⚠️ "
                print(f"{status} {display_name:.<40} {count:>10,}")
            except sqlite3.OperationalError as e:
                print(f"❌ {display_name:.<40} Table not found")
                results[table_name] = 0
        
        # Check for sample data
        print("\n" + "=" * 70)
        print("SAMPLE DATA")
        print("=" * 70)
        
        # Sample chapter
        if results.get('chapters', 0) > 0:
            cursor.execute("SELECT id, name FROM chapters LIMIT 3")
            chapters = cursor.fetchall()
            print(f"\n📚 Sample Chapters:")
            for chapter_id, name in chapters:
                print(f"   {chapter_id}. {name[:80]}")
        
        # Sample section
        if results.get('sections', 0) > 0:
            cursor.execute("SELECT id, section_number, subject FROM sections LIMIT 3")
            sections = cursor.fetchall()
            print(f"\n📄 Sample Sections:")
            for section_id, number, subject in sections:
                subject_text = subject[:60] if subject else "No subject"
                print(f"   {number}: {subject_text}")
        
        # Check embedding samples
        if results.get('section_embeddings', 0) > 0:
            cursor.execute("SELECT id, section_id, embedding FROM section_embeddings LIMIT 1")
            emb = cursor.fetchone()
            if emb:
                import json
                emb_id, section_id, emb_data = emb
                try:
                    emb_array = json.loads(emb_data)
                    print(f"\n🔢 Sample Embedding:")
                    print(f"   ID: {emb_id}, Section: {section_id}")
                    print(f"   Dimension: {len(emb_array)}")
                    print(f"   First 5 values: {emb_array[:5]}")
                except:
                    print(f"\n⚠️  Embedding data exists but couldn't parse")
        
        # Analysis
        print("\n" + "=" * 70)
        print("ANALYSIS")
        print("=" * 70)
        
        total_data = results.get('chapters', 0) + results.get('sections', 0)
        total_embeddings = (results.get('chapter_embeddings', 0) + 
                           results.get('subchapter_embeddings', 0) + 
                           results.get('section_embeddings', 0))
        
        if total_data == 0:
            print("\n❌ DATABASE IS EMPTY")
            print("   The database exists but has no data.")
            print("   You need to run the pipeline to populate it.")
            print("\n   Steps:")
            print("   1. Start backend: python run.py")
            print("   2. Open UI: http://localhost:8000/ui")
            print("   3. Click 'Pipeline' tab")
            print("   4. Enter URL and click 'Run Pipeline'")
            
        elif total_embeddings == 0:
            print("\n⚠️  DATA EXISTS BUT NO EMBEDDINGS")
            print(f"   Found {results.get('sections', 0)} regulations but 0 embeddings")
            print("\n   This means:")
            print("   - Pipeline partially completed (data was stored)")
            print("   - Embedding generation step failed or didn't run")
            print("\n   Solutions:")
            print("   1. Check backend logs for errors during embedding generation")
            print("   2. Run pipeline again (it will regenerate embeddings)")
            print("   3. Check if numpy is installed: pip install numpy")
            
        elif total_embeddings < results.get('sections', 0):
            print("\n⚠️  INCOMPLETE EMBEDDINGS")
            print(f"   Sections: {results.get('sections', 0)}")
            print(f"   Embeddings: {total_embeddings}")
            print(f"   Missing: {results.get('sections', 0) - total_embeddings}")
            print("\n   The pipeline may have been interrupted.")
            print("   Run the pipeline again to complete embedding generation.")
            
        else:
            print("\n✅ DATABASE IS HEALTHY!")
            print(f"   📊 Total Data Items: {total_data:,}")
            print(f"   🔢 Total Embeddings: {total_embeddings:,}")
            print("\n   Your system is ready to use!")
            print("   - Try RAG queries in the UI")
            print("   - Run analysis on the data")
            print("   - Search for similar regulations")
        
        # Coverage statistics
        if results.get('sections', 0) > 0:
            coverage = (results.get('section_embeddings', 0) / results.get('sections', 0)) * 100
            print(f"\n   📈 Embedding Coverage: {coverage:.1f}%")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Error reading database: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    
    # Default path (Linux/Mac)
    default_path = "/workspace/cpsc-regulation-system/backend/cfr_data.db"
    
    # Check if path provided as argument
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        # Try to find database
        possible_paths = [
            default_path,
            "./cfr_data.db",
            "./backend/cfr_data.db",
            "../cfr_data.db",
        ]
        
        db_path = None
        for path in possible_paths:
            if os.path.exists(path):
                db_path = path
                break
        
        if not db_path:
            print("Database not found in default locations.")
            print("\nUsage:")
            print("  python check_database.py [path/to/cfr_data.db]")
            print("\nExample (Windows):")
            print('  python check_database.py "C:\\My_projects\\...\\cfr_data.db"')
            print("\nExample (Linux/Mac):")
            print("  python check_database.py ./backend/cfr_data.db")
            return 1
    
    success = check_database(db_path)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
