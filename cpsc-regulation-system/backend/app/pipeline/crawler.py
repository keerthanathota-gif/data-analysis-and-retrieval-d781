
import requests
import zipfile
import os
import io
from app.config import CRAWL_URLS

def download_and_extract_zip(url, extract_to='./data'):
    """
    Downloads a zip file from the given URL and extracts its contents.
    """
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)

    print(f"Downloading from {url}")
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad status codes

    zip_file = zipfile.ZipFile(io.BytesIO(response.content))
    zip_file.extractall(extract_to)
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

