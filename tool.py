#! /usr/bin/python3


import csv
import sys


def main():
    assert len(sys.argv) == 2, sys.argv
    csv_path = sys.argv[1]
    with open(csv_path, newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            print(row)


if __name__ == '__main__':
    main()
