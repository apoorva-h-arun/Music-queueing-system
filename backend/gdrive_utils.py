import re

def get_direct_link(gdrive_url_or_id):
    """
    Converts a Google Drive view link or ID into a direct download/stream link.
    """
    file_id = gdrive_url_or_id
    
    # Handle full URL
    if 'drive.google.com' in gdrive_url_or_id:
        match = re.search(r'[-\w]{25,}', gdrive_url_or_id)
        if match:
            file_id = match.group()
            
    return f"https://docs.google.com/uc?export=download&id={file_id}"

def extract_id(gdrive_url):
    """Extracts file ID from a GDrive URL"""
    match = re.search(r'[-\w]{25,}', gdrive_url)
    return match.group() if match else gdrive_url
