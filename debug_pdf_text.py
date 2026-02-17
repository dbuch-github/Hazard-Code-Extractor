
import requests
import io
from pypdf import PdfReader

url = "https://www.roller.de/medias/sys_master/datasheets/datasheets/hfa/h24/12280887017502/2309000200-P01.pdf"
print(f"Downloading {url}...")

try:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    pdf_file = io.BytesIO(response.content)
    reader = PdfReader(pdf_file)
    
    print(f"Number of pages: {len(reader.pages)}")
    
    full_text = ""
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        print(f"--- Page {i+1} ---")
        print(text)
        full_text += text + "\n"
        
    print("\n--- End of Text ---")
    
except Exception as e:
    print(f"Error: {e}")
