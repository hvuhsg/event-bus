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
    exit_code = subprocess.run(
        ["black", "multi_event_bus", "tests", "scripts"], cwd=root_path
    ).returncode
    return exit_code


@seperator
def run_flake8():
    exit_code = subprocess.run(
        ["flake8", "multi_event_bus", "--max-line-length", "120"], cwd=root_path
    ).returncode
    return exit_code


@seperator
def run_mypy():
    exit_code = subprocess.run(["mypy", "multi_event_bus"], cwd=root_path).returncode
    return exit_code


@seperator
def run_pytest():
    exit_code = subprocess.run(["pytest", "."], cwd=root_path).returncode
    return exit_code


def run_all_tests():
    exit_code = run_pytest()
    exit_code |= run_mypy()
    exit_code |= run_flake8()
    return exit_code


def run_all():
    exit_code = run_all_tests()
    exit_code |= run_black()
    return exit_code
