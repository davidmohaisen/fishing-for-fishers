import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from common import open_csv, close_all

SCHEMA = Path(__file__).resolve().parents[1] / 'dataset' / 'schema.json'


def main():
    parser = argparse.ArgumentParser(description='Validate the dataset CSV header and optionally scan all rows')
    parser.add_argument('path', help='Path to CSV or ZIP containing one CSV')
    parser.add_argument('--full', action='store_true', help='Scan all rows and count labels')
    args = parser.parse_args()
    expected = [col['name'] for col in json.loads(SCHEMA.read_text())['columns']]
    stream, resources = open_csv(args.path)
    try:
        reader = csv.DictReader(stream)
        actual = reader.fieldnames or []
        if actual != expected:
            print('SCHEMA MISMATCH')
            print('Expected:', expected)
            print('Actual:  ', actual)
            raise SystemExit(1)
        print('Schema OK: 24 columns in expected order')
        if args.full:
            counts = Counter()
            total = 0
            malformed = 0
            for row in reader:
                total += 1
                if None in row or any(v is None for v in row.values()):
                    malformed += 1
                counts[row.get('label', '')] += 1
            print('Total records:', total)
            print('Label counts:', dict(counts))
            print('Rows with wrong field count:', malformed)
            if malformed or any(k not in ('0', '1') for k in counts):
                raise SystemExit(2)
            print('Full scan completed')
    finally:
        close_all(resources)


if __name__ == '__main__':
    main()
