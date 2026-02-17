#!/usr/bin/env python3

"""
Hazard Code Extractor
Lädt PDFs von URLs aus einem CSV-Datenfeed und extrahiert alle H-Codes (Hazard Statements).
"""

import re
import io
import sys
import csv
import requests
from pypdf import PdfReader


class ExtractionStats:
    """Hält Statistiken für den Extraktionsprozess."""
    total_rows: int = 0
    processed: int = 0
    skipped_no_url: int = 0
    skipped_not_in_list: int = 0

    def __init__(self):
        self.total_rows = 0
        self.processed = 0
        self.skipped_no_url = 0
        self.skipped_not_in_list = 0

def load_product_ids(product_ids_file: str) -> set:
    """Lädt die Artikelnummern aus der CSV-Datei."""
    product_ids = set()
    with open(product_ids_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, skipinitialspace=True, delimiter=',')
        if reader.fieldnames is None:
            raise ValueError(f"CSV file {product_ids_file} has no headers.")
        
        for row in reader:
            if '# Artikelnummer' in row:
                product_ids.add(row['# Artikelnummer'].strip())
    print(f"DEBUG: {len(product_ids)} Artikelnummern geladen", file=sys.stderr)
    sample_ids: list[str] = list(product_ids)
    sample_subset: list[str] = []
    for i, pid in enumerate(sample_ids):
        if i >= 5: break
        sample_subset.append(pid)
    print(f"DEBUG: Erste 5 product_ids: {sample_subset}", file=sys.stderr)
    return product_ids


def extract_hcodes_from_url(url: str) -> str:
    """Lädt ein PDF von der gegebenen URL und extrahiert alle H-Codes."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        pdf_file = io.BytesIO(response.content)
        reader = PdfReader(pdf_file)
        full_text_list: list[str] = []
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text_list.append(text)
                full_text_list.append("\n")
        
        full_text: str = "".join(full_text_list)
        
        pattern = r'\bH\d{3}[A-Za-z]?\b'
        matches = re.findall(pattern, full_text)
        unique_codes = sorted(set(matches))
        
        return ",".join(unique_codes) if unique_codes else "none"
    except Exception as e:
        return f"error: {str(e)}"


def process_data_feed(data_feed_file: str, product_ids_file: str, output_file: str) -> None:
    """Verarbeitet den Datenfeed und extrahiert H-Codes für zulässige Artikel."""
    product_ids = load_product_ids(product_ids_file)
    stats = ExtractionStats()
    
    with open(data_feed_file, 'r', encoding='utf-8') as f_in, \
         open(output_file, 'w', encoding='utf-8', newline='') as f_out:
        
        reader = csv.DictReader(f_in, skipinitialspace=True, delimiter=';')
        if reader.fieldnames is None:
            raise ValueError(f"CSV file {data_feed_file} has no headers.")
            
        writer = csv.writer(f_out, delimiter=';')
        writer.writerow(['Artikelnummer', 'H-Codes'])
        
        for row in reader:
            stats.total_rows = stats.total_rows + 1
            article_num = row.get('# Artikelnummer', '').strip()
            url = row.get('energy-label-data-sheet-url1', '').strip()
            
            if not article_num or not url:
                stats.skipped_no_url = stats.skipped_no_url + 1
                continue
            
            if article_num not in product_ids:
                stats.skipped_not_in_list = stats.skipped_not_in_list + 1
                continue
            
            stats.processed = stats.processed + 1
            print(f"DEBUG: [{stats.processed}/{len(product_ids)}] Verarbeite {article_num}", file=sys.stderr)
            hcodes = extract_hcodes_from_url(url)
            writer.writerow([article_num, hcodes])
    
    print(f"DEBUG: {stats.total_rows} Zeilen gelesen", file=sys.stderr)
    print(f"DEBUG: {stats.skipped_no_url} übersprungen (keine URL)", file=sys.stderr)
    print(f"DEBUG: {stats.skipped_not_in_list} übersprungen (nicht in Liste)", file=sys.stderr)
    print(f"DEBUG: {stats.processed} Artikel verarbeitet", file=sys.stderr)
    print(f"DEBUG: Output geschrieben nach {output_file}", file=sys.stderr)


def main():
    """Verarbeitet Kommandozeilenargumente und startet die Extraktion."""
    if len(sys.argv) < 4:
        print("Verwendung: python hazard_code_extractor.py <data_feed_csv> <product_ids_csv> <output_csv>")
        sys.exit(1)
    
    data_feed_file = sys.argv[1]
    product_ids_file = sys.argv[2]
    output_file = sys.argv[3]
    
    try:
        process_data_feed(data_feed_file, product_ids_file, output_file)
    except FileNotFoundError as e:
        print(f"Fehler: Datei nicht gefunden: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Fehler: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()