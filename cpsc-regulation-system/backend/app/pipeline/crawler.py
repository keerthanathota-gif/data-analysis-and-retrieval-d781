
import requests
import zipfile
import os
import io
from app.config import CRAWL_URLS

def download_and_extract_zip(url, extract_to='./data'):
    """
    Downloads a zip file from the given URL and extracts its contents.
    """
    # Ensure extract_to is an absolute path and properly formatted
    extract_to = os.path.abspath(extract_to)
    
    if not os.path.exists(extract_to):
        os.makedirs(extract_to, exist_ok=True)

    print(f"Downloading from {url}")
    response = requests.get(url, timeout=300)  # 5 minute timeout
    response.raise_for_status()  # Raise an exception for bad status codes

    print(f"Extracting to {extract_to}")
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))
    
    # Extract with proper path handling
    for member in zip_file.namelist():
        # Sanitize filename to avoid path issues on Windows
        member_path = os.path.join(extract_to, member)
        member_path = os.path.normpath(member_path)
        
        # Extract the member
        zip_file.extract(member, extract_to)
    
    print(f"Extracted to {extract_to}")
    return extract_to

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

