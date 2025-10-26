"""
Data Processing Pipeline for CFR Agentic AI Application
Integrates crawler, parser, and database storage with embeddings
"""

import os
import glob
import json
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.pipeline.crawler import download_and_extract_zip
from app.pipeline.cfr_parser import parse_chapter_subchapter_part_sections, save_json, save_csv
from app.models.cfr_database import (
    Chapter, Subchapter, Part, Section,
    ChapterEmbedding, SubchapterEmbedding, SectionEmbedding,
    init_cfr_db, SessionLocal
)
from app.services.embedding_service import EmbeddingService
from app.config import DEFAULT_CRAWL_URLS, DATA_DIR, OUTPUT_DIR

# Create embedding service instance
embedding_service = EmbeddingService()


class DataPipeline:
    def __init__(self, urls: List[str] = None):
        """
        Initialize data pipeline
        
        Args:
            urls: List of URLs to crawl. If None, uses DEFAULT_CRAWL_URLS
        """
        # Use absolute paths to avoid any path resolution issues
        self.data_dir = os.path.abspath(DATA_DIR)
        self.output_dir = os.path.abspath(OUTPUT_DIR)
        self.crawl_urls = urls if urls else DEFAULT_CRAWL_URLS
        
        print(f"Initializing DataPipeline:")
        print(f"  data_dir: {self.data_dir}")
        print(f"  output_dir: {self.output_dir}")
        
        # Create directories if they don't exist
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            print(f"  Created/verified data_dir: {self.data_dir}")
        except Exception as e:
            print(f"  ERROR creating data_dir: {e}")
            raise
            
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            print(f"  Created/verified output_dir: {self.output_dir}")
        except Exception as e:
            print(f"  ERROR creating output_dir: {e}")
            raise
        
        # Initialize database
        init_cfr_db()
        
        # Pipeline status tracking
        self.status = {
            'state': 'idle',  # idle, running, completed, error
            'current_step': None,
            'progress': 0,
            'total_steps': 6,
            'steps_completed': [],
            'error_message': None,
            'start_time': None,
            'end_time': None,
            'stats': {}
        }
    
    def update_status(self, state: str = None, current_step: str = None, 
                     progress: int = None, error_message: str = None):
        """Update pipeline status"""
        from datetime import datetime
        
        if state:
            self.status['state'] = state
            if state == 'running' and not self.status['start_time']:
                self.status['start_time'] = datetime.now()
            elif state in ['completed', 'error']:
                self.status['end_time'] = datetime.now()
        
        if current_step:
            self.status['current_step'] = current_step
            if current_step not in self.status['steps_completed']:
                self.status['steps_completed'].append(current_step)
        
        if progress is not None:
            self.status['progress'] = progress
        
        if error_message:
            self.status['error_message'] = error_message
    
    def get_status(self):
        """Get current pipeline status"""
        return self.status.copy()
    
    def run_full_pipeline(self):
        """Run the complete data pipeline: crawl -> parse -> store -> embed"""
        try:
            self.update_status(state='running', current_step='Starting', progress=0)
            
            print("=" * 80)
            print("Starting CFR Data Pipeline")
            print("=" * 80)
            
            # Step 1: Crawl and download data
            print("\n[1/6] Crawling and downloading CFR data...")
            self.update_status(current_step='Crawling data', progress=17)
            self.crawl_data()
            
            # Step 2: Parse XML files
            print("\n[2/6] Parsing XML files...")
            self.update_status(current_step='Parsing XML', progress=33)
            parsed_data_list = self.parse_xml_files()
            
            # Step 3: Store in database
            print("\n[3/6] Storing data in database...")
            self.update_status(current_step='Storing in database', progress=50)
            self.store_in_database(parsed_data_list)
            
            # Step 4: Generate embeddings
            print("\n[4/6] Generating embeddings...")
            self.update_status(current_step='Generating embeddings', progress=67)
            self.generate_embeddings()
            
            # Step 5: Get statistics
            print("\n[5/6] Calculating statistics...")
            self.update_status(current_step='Calculating statistics', progress=83)
            stats = self.get_statistics()
            self.status['stats'] = stats
            
            # Step 6: Complete
            self.update_status(state='completed', current_step='Completed', progress=100)
            
            print("\n" + "=" * 80)
            print("Pipeline completed successfully!")
            print("=" * 80)
            
            # Display statistics
            print("\nDatabase Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
                
        except Exception as e:
            import traceback
            error_details = f"{type(e).__name__}: {str(e)}"
            self.update_status(state='error', error_message=error_details)
            print(f"\n[ERROR] Pipeline failed: {error_details}")
            print(f"[ERROR] Full traceback:")
            traceback.print_exc()
            raise
    
    def crawl_data(self):
        """Crawl and download CFR data from configured URLs"""
        print(f"  Processing {len(self.crawl_urls)} URL(s)...")
        
        for target_url_base in self.crawl_urls:
            try:
                # Parse URL to construct zip filename
                url_parts = [part for part in target_url_base.split('/') if part]
                
                if len(url_parts) < 2:
                    print(f"  [WARNING] Invalid URL format: {target_url_base}")
                    continue
                    
                year = url_parts[-2]
                title_part = url_parts[-1]
                
                zip_filename = f"CFR-{year}-{title_part}.zip"
                full_zip_url = f"https://www.govinfo.gov/bulkdata/CFR/{year}/{title_part}/{zip_filename}"
                
                print(f"  Downloading: {full_zip_url}")
                download_and_extract_zip(full_zip_url, self.data_dir)
                print(f"  [OK] Downloaded and extracted successfully")
            except Exception as e:
                import traceback
                print(f"  [ERROR] Error downloading from {target_url_base}: {e}")
                print(f"  [ERROR] Traceback: {traceback.format_exc()}")
                raise
    
    def parse_xml_files(self) -> List[Dict[str, Any]]:
        """Parse all XML files in the data directory"""
        print(f"  Looking for XML files in: {self.data_dir}")
        xml_files = glob.glob(os.path.join(self.data_dir, "*.xml"))
        
        if not xml_files:
            print(f"  [WARNING] No XML files found in data directory: {self.data_dir}")
            print(f"  [WARNING] Directory contents: {os.listdir(self.data_dir) if os.path.exists(self.data_dir) else 'Directory does not exist'}")
            return []
        
        parsed_data_list = []
        for xml_file in xml_files:
            try:
                print(f"  Parsing: {os.path.basename(xml_file)}")
                parsed_data = parse_chapter_subchapter_part_sections(xml_file)
                
                # Save JSON and CSV outputs
                base_name = os.path.splitext(os.path.basename(xml_file))[0]
                # Sanitize base_name to avoid any path issues
                base_name = base_name.replace(':', '_').replace('*', '_').replace('?', '_')
                base_name = base_name.replace('"', '_').replace('<', '_').replace('>', '_')
                base_name = base_name.replace('|', '_').replace('/', '_').replace('\\', '_')
                
                json_output = os.path.abspath(os.path.join(self.output_dir, f"{base_name}.json"))
                csv_output = os.path.abspath(os.path.join(self.output_dir, f"{base_name}.csv"))
                
                print(f"    Saving to:")
                print(f"      JSON: {json_output}")
                print(f"      CSV: {csv_output}")
                
                save_json(parsed_data, json_output)
                save_csv(parsed_data, csv_output)
                
                parsed_data_list.append(parsed_data)
                print(f"    [OK] Saved successfully")
            except Exception as e:
                import traceback
                print(f"    [ERROR] Error parsing {xml_file}: {type(e).__name__}: {e}")
                print(f"    [ERROR] Traceback: {traceback.format_exc()}")
                # Continue with next file instead of crashing
        
        return parsed_data_list
    
    def store_in_database(self, parsed_data_list: List[Dict[str, Any]]):
        """Store parsed data in SQLite database"""
        print(f"  Processing {len(parsed_data_list)} parsed file(s)...")
        
        if not parsed_data_list:
            print("  [WARNING] No parsed data to store!")
            return
            
        db = SessionLocal()

        try:
            for parsed_data in parsed_data_list:
                chapters = parsed_data.get("chapters", [])
                print(f"  Processing {len(chapters)} chapters...")
                for idx, chapter_data in enumerate(chapters, 1):
                    print(f"    Chapter {idx}/{len(chapters)}: {chapter_data.get('chapter_name', 'Unknown')}")
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
                        db.flush()  # Get subchapter ID
                        
                        # Process parts
                        for part_data in subchapter_data.get("parts", []):
                            part = Part(
                                subchapter_id=subchapter.id,
                                heading=part_data["heading"]
                            )
                            db.add(part)
                            db.flush()  # Get part ID
                            
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
            
            db.commit()
            print("  [OK] Data stored successfully")
        except Exception as e:
            db.rollback()
            print(f"  [ERROR] Error storing data: {e}")
            print(f"  [ERROR] Error type: {type(e).__name__}")
            import traceback
            print(f"  [ERROR] Traceback:")
            traceback.print_exc()
            raise
        finally:
            db.close()
    
    def generate_embeddings(self):
        """Generate embeddings for all chapters, subchapters, and sections"""
        db = SessionLocal()
        
        try:
            # Generate chapter embeddings
            print("  Generating chapter embeddings...")
            chapters = db.query(Chapter).all()
            print(f"    Found {len(chapters)} chapters")
            
            if len(chapters) == 0:
                print("    [WARNING] No chapters found in database!")
                return
            
            for idx, chapter in enumerate(chapters, 1):
                print(f"      Chapter {idx}/{len(chapters)}")
                # Create text representation
                text = chapter.name
                
                # Generate embedding
                embedding = embedding_service.generate_embedding(text)
                
                # Store embedding
                chapter_embedding = ChapterEmbedding(
                    chapter_id=chapter.id,
                    embedding=json.dumps(embedding)
                )
                db.add(chapter_embedding)
            
            db.commit()
            
            # Generate subchapter embeddings
            print("  Generating subchapter embeddings...")
            subchapters = db.query(Subchapter).all()
            print(f"    Found {len(subchapters)} subchapters")
            
            for idx, subchapter in enumerate(subchapters, 1):
                if idx % 5 == 0 or idx == len(subchapters):
                    print(f"      Subchapter {idx}/{len(subchapters)}")
                # Create text representation
                text = f"{subchapter.chapter.name} - {subchapter.name}"
                
                # Generate embedding
                embedding = embedding_service.generate_embedding(text)
                
                # Store embedding
                subchapter_embedding = SubchapterEmbedding(
                    subchapter_id=subchapter.id,
                    embedding=json.dumps(embedding)
                )
                db.add(subchapter_embedding)
            
            db.commit()
            
            # Generate section embeddings
            print("  Generating section embeddings...")
            sections = db.query(Section).all()
            print(f"    Found {len(sections)} sections")
            print(f"    Processing sections in batches of 32...")
            
            # Batch process sections for efficiency
            batch_size = 32
            total_batches = (len(sections) + batch_size - 1) // batch_size
            for batch_num, i in enumerate(range(0, len(sections), batch_size), 1):
                print(f"      Batch {batch_num}/{total_batches}")
                batch = sections[i:i+batch_size]
                
                # Prepare texts
                texts = []
                for section in batch:
                    text = f"{section.subject} {section.text}"
                    texts.append(text)
                
                # Generate embeddings in batch
                embeddings = embedding_service.generate_embeddings(texts)
                
                # Store embeddings
                for section, embedding in zip(batch, embeddings):
                    section_embedding = SectionEmbedding(
                        section_id=section.id,
                        embedding=json.dumps(embedding)
                    )
                    db.add(section_embedding)
                
                db.commit()

            print("  [OK] Embeddings generated successfully")
        except Exception as e:
            import traceback
            db.rollback()
            print(f"  [ERROR] Error generating embeddings: {e}")
            print(f"  [ERROR] Traceback: {traceback.format_exc()}")
            raise
        finally:
            db.close()
    
    def get_statistics(self):
        """Get statistics about the stored data"""
        db = SessionLocal()
        
        try:
            stats = {
                "chapters": db.query(Chapter).count(),
                "subchapters": db.query(Subchapter).count(),
                "parts": db.query(Part).count(),
                "sections": db.query(Section).count(),
                "chapter_embeddings": db.query(ChapterEmbedding).count(),
                "subchapter_embeddings": db.query(SubchapterEmbedding).count(),
                "section_embeddings": db.query(SectionEmbedding).count()
            }
            return stats
        finally:
            db.close()


if __name__ == "__main__":
    pipeline = DataPipeline()
    pipeline.run_full_pipeline()
    
    # Print statistics
    print("\nData Statistics:")
    stats = pipeline.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
