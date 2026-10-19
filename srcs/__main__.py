import os
import argparse
from pathlib import Path

from dotenv import load_dotenv
from .jev import Jev

from rich.console import Console


from .visu import export_html


console = Console()


def get_api_key():
    load_dotenv()

    key = os.getenv("KEY")

    if key is None:
        raise ValueError("No key")

    return key


def scan_directory(directory: Path, jev: Jev):

    results = {}

    paths = sorted(directory.rglob("*"), key=lambda path: str(path).lower())

    for path in paths:
        if any(part.startswith(".") for part in path.parts):
            continue

        if "__pycache__" in path.parts:
            continue

        if ".py" not in path._str:
            continue

        if not path.is_file():
            continue

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        answers = jev.scan(content)
        results[path] = answers

    return results


def get_files(results):
    return sorted(
        results.keys(),
        key=lambda path: str(path).lower(),
    )


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--code",
        default=".",
    )

    args = parser.parse_args()

    directory = Path(args.code).resolve()

    jev = Jev(get_api_key())

    console.print(
        f"Scanning {directory}"
    )

    results = scan_directory(
        directory,
        jev,
    )

    export_html(directory, results)


if __name__ == "__main__":
    main()
