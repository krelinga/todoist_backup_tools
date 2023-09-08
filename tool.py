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


@dataclasses.dataclass
class TodoistNote:
    content: str
    author: str
    date: str


@dataclasses.dataclass
class TodoistTask:
    content: str
    description: str
    priority: str
    indent: str
    author: str
    responsible: str
    date: str
    date_lang: str
    timezone: str
    notes: list[TodoistNote] = dataclasses.field(default_factory=list)


def ConvertCsvLinesToTasks(csv_lines: list[CSVLine]) -> list[TodoistTask]:
    def copy_relevant_fields(csv_line: CSVLine, out_type):
        csv_line_as_dict = dataclasses.asdict(csv_line)
        copied_values = {}
        for field_name in map(lambda x: x.name, dataclasses.fields(out_type)):
            if field_name in csv_line_as_dict:
                copied_values[field_name] = csv_line_as_dict[field_name]
        return out_type(**copied_values)

    todoist_tasks = []
    for csv_line in csv_lines:
        if csv_line.type == '':
            continue
        elif csv_line.type == 'task':
            todoist_tasks.append(copy_relevant_fields(csv_line, TodoistTask))
        elif csv_line.type == 'note':
            assert len(todoist_tasks) > 0
            todoist_tasks[-1].notes.append(copy_relevant_fields(csv_line, TodoistNote))
        else:
            assert False, f'unrecognized type {csv_line.type}'
    return todoist_tasks


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
    csv_lines = ReadFile(csv_path)
    tasks = ConvertCsvLinesToTasks(csv_lines)
    for task in tasks:
        print(task)


if __name__ == '__main__':
    main()
