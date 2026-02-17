
import csv
import sys

def inspect(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';', skipinitialspace=True)
        assert reader.fieldnames is not None
        print(f"Header fields: {reader.fieldnames}")
        if 'energy-label-data-sheet-url1' in (reader.fieldnames or []):
             print("Column 'energy-label-data-sheet-url1' FOUND in header.")
        else:
             print("Column 'energy-label-data-sheet-url1' NOT FOUND in header.")
        
        for i, row in enumerate(reader):
            if i >= 5: break
            val = row.get('energy-label-data-sheet-url1')
            print(f"Row {i+1} value: '{val}'")

if __name__ == "__main__":
    inspect(sys.argv[1])
