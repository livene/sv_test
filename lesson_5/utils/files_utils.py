import csv
from data.config import IMPORT_PATH
from data.models import InitialCsvData


def write_row_to_csv_file(path: str, row: list):
    with open(path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(row)


def write_rows_to_csv_file(path: str, rows: list[list]):
    with open(path, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def get_initial_data_from_csv_file(path: str = IMPORT_PATH, skip_header: bool = True) -> list[InitialCsvData]:
    res = []
    with open(path) as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 1:
                res.append(InitialCsvData(private_key=row[0]))
    if skip_header and len(res):
        return res[1:]
    return res
