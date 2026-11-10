import csv
import zipfile
from pathlib import Path


def open_csv(path):
    """Return a text stream and resources to close (supports .csv or .zip)."""
    path = Path(path)
    if path.suffix.lower() == '.zip':
        archive = zipfile.ZipFile(path)
        members = [name for name in archive.namelist() if name.lower().endswith('.csv') and not name.endswith('/')]
        if len(members) != 1:
            archive.close()
            raise ValueError(f'Expected exactly one CSV inside ZIP, found {len(members)}')
        import io
        binary = archive.open(members[0])
        stream = io.TextIOWrapper(binary, encoding='utf-8-sig', newline='')
        return stream, [stream, archive]
    if path.suffix.lower() == '.csv':
        stream = path.open('r', encoding='utf-8-sig', newline='')
        return stream, [stream]
    raise ValueError('Input must be a .csv or .zip file')


def close_all(resources):
    for resource in resources:
        resource.close()
