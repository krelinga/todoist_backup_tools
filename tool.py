#! /usr/bin/python3


import csv
import sys


def main():
    print('hello world!')
    assert len(sys.argv) == 2, sys.argv
    csv_path = sys.argv[1]
    print(csv_path)


if __name__ == '__main__':
    main()
