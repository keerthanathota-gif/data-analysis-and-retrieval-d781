
import requests
import zipfile
import os
import io
from app.config import CRAWL_URLS

def download_and_extract_zip(url, extract_to='./data'):
    """
    Downloads a zip file from the given URL and extracts its contents.
    Handles cross-platform path issues.
    """
    # Ensure the extract path exists and is properly formatted
    extract_to = os.path.abspath(extract_to)
    print(f"Extract path (absolute): {extract_to}")
    
    if not os.path.exists(extract_to):
        try:
            os.makedirs(extract_to, exist_ok=True)
            print(f"Created directory: {extract_to}")
        except Exception as e:
            print(f"ERROR creating directory {extract_to}: {e}")
            raise
    
    # Verify the directory is writable
    if not os.access(extract_to, os.W_OK):
        raise PermissionError(f"Directory {extract_to} is not writable")

    print(f"Downloading from {url}")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes
    except requests.RequestException as e:
        print(f"Error downloading from {url}: {e}")
        raise

    try:
        zip_file = zipfile.ZipFile(io.BytesIO(response.content))
        
        # Extract files one by one to handle cross-platform path issues
        for member in zip_file.namelist():
            try:
                # Sanitize filename for cross-platform compatibility
                filename = member.replace('\\', '/').strip()
                if not filename:
                    continue
                    
                # Skip directory entries
                if filename.endswith('/'):
                    continue
                    
                # Get just the base filename (no path components)
                base_filename = os.path.basename(filename)
                
                # Sanitize the filename to remove any invalid characters
                # Remove or replace characters that might be problematic
                base_filename = base_filename.replace(':', '_').replace('*', '_').replace('?', '_')
                base_filename = base_filename.replace('"', '_').replace('<', '_').replace('>', '_')
                base_filename = base_filename.replace('|', '_')
                
                # Create target path using absolute path with forward slashes for cross-platform compatibility
                target_path = os.path.abspath(os.path.join(extract_to, base_filename)).replace('\\', '/')
                
                # Additional validation for problematic characters
                if ':' in os.path.basename(target_path):
                    print(f"  SKIPPING: Invalid filename (contains colon): {base_filename}")
                    continue
                
                print(f"  Extracting: {base_filename} -> {target_path}")
                
                # Extract the file
                try:
                    with zip_file.open(member) as source:
                        file_content = source.read()
                        with open(target_path, 'wb') as target:
                            target.write(file_content)
                except OSError as e:
                    print(f"  ERROR extracting {member} [Errno {e.errno}]: {str(e)}")
                    print(f"  Hint: Check for invalid characters in filename or path issues")
                    raise
            except Exception as e:
                print(f"  ERROR extracting {member}: {type(e).__name__}: {str(e)}")
                # Continue with other files instead of failing completely
                continue
        
        print(f"Extracted to {extract_to}")
        return extract_to
    except (zipfile.BadZipFile, OSError, IOError) as e:
        print(f"Error extracting zip file: {e}")
        raise

if __name__ == "__main__":
    download_path = "./cfr_data"
    for target_url_base in CRAWL_URLS:
        
        # Example: https://www.govinfo.gov/bulkdata/CFR/2025/title-16/ -> ['', 'https:', '', 'www.govinfo.gov', 'bulkdata', 'CFR', '2025', 'title-16', '']
        url_parts = [part for part in target_url_base.split('/') if part] # Filter out empty strings
        
        year = url_parts[-2] # e.g., '2025'
        title_part = url_parts[-1] # e.g., 'title-16'
        
        # Construct the zip filename: CFR-YEAR-title-TITLE_NUMBER.zip
        zip_filename = f"CFR-{year}-{title_part}.zip"
        full_zip_url = f"https://www.govinfo.gov/bulkdata/CFR/{year}/{title_part}/{zip_filename}"

        download_and_extract_zip(full_zip_url, download_path)

