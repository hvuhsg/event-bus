import os
import subprocess
from pathlib import Path

root_path = str(Path(__file__).parent.parent.absolute())
terminal_length = os.get_terminal_size().columns


def seperator(func):
    def wrapper(*args, **kwargs):
        func_name = func.__name__.replace("run_", "")
        line = "#" * (terminal_length // 2 - (len(func_name) // 2) - 1)
        print(line, func_name, line)
        try:
            return func(*args, **kwargs)
        finally:
            print(line, func_name, line, "\n\n\n")

    return wrapper


@seperator
def run_black():
    subprocess.run(["black", "event_bus", "tests", "scripts"], cwd=root_path)


@seperator
def run_mypy():
    subprocess.run(["mypy", "event_bus"], cwd=root_path)


@seperator
def run_pytest():
    subprocess.run(["pytest", "."], cwd=root_path)


def run_all_tests():
    run_pytest()
    run_mypy()


def run_all():
    run_all_tests()
    run_black()
