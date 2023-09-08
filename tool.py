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


@dataclasses.dataclass(frozen=True)
class TodoistNote:
    content: str
    author: str
    date: str


@dataclasses.dataclass(frozen=True)
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
    notes: tuple[TodoistNote] = dataclasses.field(default_factory=tuple)

    # TODO: this hash is not stable across binary invocations ... no good.
    @property
    def id(self):
        return format(abs(hash(self.content)), '016X')


def ConvertCsvLinesToTasks(csv_lines: list[CSVLine]) -> list[TodoistTask]:
    def copy_relevant_fields(in_record, out_type, extra_fields:dict|None=None):
        in_record_as_dict = dataclasses.asdict(in_record)
        copied_values = {}
        for field_name in map(lambda x: x.name, dataclasses.fields(out_type)):
            if field_name in in_record_as_dict:
                copied_values[field_name] = in_record_as_dict[field_name]
        if extra_fields is not None:
            # TODO: this can probably be replaced by a one-liner.
            for field_name, field_value in extra_fields.items():
                copied_values[field_name] = field_value
        return out_type(**copied_values)

    # This could probably be made cleaner ... i'm not sure I need to convert these types before clustering them?
    last_task = None
    task_to_comments = {}
    for csv_line in csv_lines:
        if csv_line.type == '':
            continue
        elif csv_line.type == 'task':
            task = copy_relevant_fields(csv_line, TodoistTask)
            last_task = task
            task_to_comments[task] = []
        elif csv_line.type == 'note':
            assert last_task is not None
            assert last_task in task_to_comments
            task_to_comments[last_task].append(copy_relevant_fields(csv_line, TodoistNote))
        else:
            assert False, f'unrecognized type {csv_line.type}'
    return [copy_relevant_fields(task, TodoistTask, extra_fields={'notes':notes})
            for task, notes in task_to_comments.items()]


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
