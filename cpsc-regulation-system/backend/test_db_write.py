#!/usr/bin/env python3
"""
Test database write operation to find the actual error
"""
import sys
import traceback
sys.path.insert(0, '.')

print("="*70)
print("TESTING DATABASE WRITE OPERATION")
print("="*70)

try:
    print("\n[1] Importing database models...")
    from app.models.cfr_database import SessionLocal, Chapter, Subchapter, Part, Section
    print("    [OK] Models imported")

    print("\n[2] Creating database session...")
    db = SessionLocal()
    print("    [OK] Session created")

    print("\n[3] Testing simple write...")
    test_chapter = Chapter(name="Test Chapter for Error Detection")
    db.add(test_chapter)
    db.flush()
    print(f"    [OK] Chapter added with ID: {test_chapter.id}")

    print("\n[4] Adding subchapter...")
    test_subchapter = Subchapter(
        chapter_id=test_chapter.id,
        name="Test Subchapter"
    )
    db.add(test_subchapter)
    db.flush()
    print(f"    [OK] Subchapter added with ID: {test_subchapter.id}")

    print("\n[5] Adding part...")
    test_part = Part(
        subchapter_id=test_subchapter.id,
        heading="Test Part Heading"
    )
    db.add(test_part)
    db.flush()
    print(f"    [OK] Part added with ID: {test_part.id}")

    print("\n[6] Adding section...")
    test_section = Section(
        part_id=test_part.id,
        section_number="§ 1234.56",
        subject="Test Section Subject",
        text="This is test section text to verify database writes work correctly.",
        citation="16 CFR 1234.56",
        section_label="1234.56"
    )
    db.add(test_section)
    db.flush()
    print(f"    [OK] Section added with ID: {test_section.id}")

    print("\n[7] Committing transaction...")
    db.commit()
    print("    [OK] Transaction committed successfully!")

    print("\n[8] Cleaning up test data...")
    db.delete(test_section)
    db.delete(test_part)
    db.delete(test_subchapter)
    db.delete(test_chapter)
    db.commit()
    print("    [OK] Test data cleaned up")

    db.close()

    print("\n" + "="*70)
    print("✅ DATABASE WRITE TEST PASSED!")
    print("="*70)
    print("\nThe database configuration is working correctly.")
    print("The error must be coming from somewhere else in the pipeline.")

except Exception as e:
    print(f"\n❌ DATABASE WRITE TEST FAILED!")
    print(f"\nError Type: {type(e).__name__}")
    print(f"Error Message: {str(e)}")
    print(f"\nFull Traceback:")
    traceback.print_exc()
    print("\n" + "="*70)
