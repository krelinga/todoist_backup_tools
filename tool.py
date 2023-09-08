#! /usr/bin/python3


import csv
import dataclasses
import sys


@dataclasses.dataclass
class CSVLine:
    type: str
    content: str
    description: str
    priority: str
    indent: str
    author: str
    responsible: str
    date: str
    date_lang: str
    timezone: str


def ReadFile(csv_path: str) -> list[CSVLine]:
    csv_lines = []
    with open(csv_path, newline='', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for record in csv_reader:
            lower_case_keys = {k.lower(): v for (k, v) in record.items()}
            csv_lines.append(CSVLine(**lower_case_keys))
    return csv_lines


def main():
    assert len(sys.argv) == 2, sys.argv
    csv_path = sys.argv[1]
    entries = ReadFile(csv_path)
    print(entries)


if __name__ == '__main__':
    main()
