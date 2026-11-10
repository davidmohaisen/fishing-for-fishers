import argparse
import csv
from common import open_csv, close_all


def main():
    parser = argparse.ArgumentParser(description='Preview a transaction CSV or ZIP')
    parser.add_argument('path')
    parser.add_argument('--rows', type=int, default=5)
    args = parser.parse_args()
    stream, resources = open_csv(args.path)
    try:
        reader = csv.DictReader(stream)
        print('Columns:', ', '.join(reader.fieldnames or []))
        for i, row in enumerate(reader):
            if i >= args.rows:
                break
            print(row)
    finally:
        close_all(resources)


if __name__ == '__main__':
    main()
