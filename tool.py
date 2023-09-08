#! /usr/bin/python3


import argparse
import csv
import dataclasses
import sys
import textwrap


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

    # TODO: this hash is not stable across binary invocations ... no good.
    @property
    def id(self):
        return format(abs(hash(self.content)), '016X')


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


def PrettyPrintTasks(tasks: list[TodoistTask]) -> None:
    for task in tasks:
        print('========================')
        print(textwrap.dedent(f'''\
                [{task.id}] {task.content}
                -------------'''))
        if len(task.description) > 0:
            print(task.description)
        print(textwrap.dedent(f'''\
                - priority: {task.priority}
                - date: {task.date}
                - author: {task.author}
                - responsible: {task.responsible}
                - notes: {len(task.notes)}'''))
        for note in task.notes:
            print(f'  - note from {note.author} at {note.date}:')
            print(f'    {note.content}')
        print('========================')


# TODO: use a proper interface once I have internet access again (if such a thing exists in python?)
class Subcommand:
    def ConfigureArgs(self, parser: argparse.ArgumentParser) -> None:
        pass

    def Run(self, args: argparse.Namespace) -> int:
        pass


class List(Subcommand):
    def ConfigureArgs(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('csv_path')
        parser.add_argument('--long', action='store_true', default=False, dest='long')

    def Run(self, args: argparse.Namespace) -> int:
        csv_lines = ReadFile(args.csv_path)
        tasks = ConvertCsvLinesToTasks(csv_lines)
        if args.long:
            PrettyPrintTasks(tasks)
        else:
            for task in tasks:
                print(task.id)
        return 0

def main():
    commands = {
            'list': List(),
    }
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command', required=True)
    for name, command in commands.items():
        command_parser = subparsers.add_parser(name)
        command.ConfigureArgs(command_parser)
    args = parser.parse_args()
    sys.exit(commands[args.command].Run(args))


if __name__ == '__main__':
    main()
