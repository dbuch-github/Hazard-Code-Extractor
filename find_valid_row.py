
import csv
import sys

def find_valid_row(filename, output_filename):
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';', skipinitialspace=True)
        header = reader.fieldnames
        
        if header is None:
            print("Error: CSV file has no headers or is empty.", file=sys.stderr)
            sys.exit(1)
        
        # Ensure the type checker knows header is not None
        assert header is not None
        
        found_row = None
        for i, row in enumerate(reader):
            if row.get('energy-label-data-sheet-url1'):
                print(f"Found valid URL at row {i+2}: {row['energy-label-data-sheet-url1']}")
                found_row = row
                break
            if i % 10000 == 0:
                print(f"Scanned {i} rows...", file=sys.stderr)
        
        if found_row:
            assert found_row is not None
            with open(output_filename, 'w', encoding='utf-8', newline='') as f_out:
                writer = csv.DictWriter(f_out, fieldnames=header, delimiter=';')
                writer.writeheader()
                writer.writerow(found_row)
            print(f"Created {output_filename} with valid row.")
        else:
            print("No valid URL found in scanned rows.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python find_valid_row.py <input_csv> <output_csv>")
        sys.exit(1)
    find_valid_row(sys.argv[1], sys.argv[2])
