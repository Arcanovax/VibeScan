import os
import argparse
from pathlib import Path

from dotenv import load_dotenv
from jev import Jev

from rich.console import Console
from rich.live import Live
from rich.markup import escape
from rich.text import Text
from rich.tree import Tree

import readchar


console = Console()

def get_api_key():
    load_dotenv()

    key = os.getenv("KEY")

    if key is None:
        raise ValueError("No key")

    return key

def scan_directory(directory: Path, jev: Jev):

    results = {}

    paths = sorted(directory.rglob("*"),
        key=lambda path: str(path).lower(),
    )

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


def add_file_to_tree(parent, path: Path, answers, selected: Path | None, expanded: set[Path]):
    ai_result = answers.get("is_made_by_ai")

    if ai_result is not None:
        answer = ai_result.answer
        confidence = ai_result.confidence

        status = str(answer).lower()

        filename = Text()

        filename.append(
            path.name,
            "bold green" if path == selected else "green",
        )

        filename.append(
            f" ({status} {confidence:.2f})",
            "blue",
        )

    else:
        filename = Text(path.name, "green")


    if path == selected:
        filename.stylize("reverse")

    branch = parent.add(filename)

    if path in expanded:

        for name, content in answers.items():

            answer = getattr(content, "answer", "?")
            confidence = getattr(content,"confidence",None)

            line = Text()

            line.append(name, "cyan")
            line.append(": ", "dim")
            line.append(str(answer), "white")

            if confidence is not None:
                line.append(
                    f" ({confidence * 100:.1f}%)",
                    "blue",
                )

            branch.add(line)


def build_tree(
    directory: Path,
    results,
    selected: Path | None,
    expanded: set[Path],
):
    tree = Tree("Project")
    def build_directory(current_dir: Path, parent):

        children = set(
            path for path in results
            if path.parent == current_dir
        )

        directories = set()

        for path in results:
            try:
                relative = path.relative_to(current_dir)
            except ValueError:
                continue

            if len(relative.parts) > 1:
                directories.add(
                    current_dir / relative.parts[0]
                )

        entries = sorted(
            children | directories,
            key=lambda path: (
                path.is_file(),
                path.name.lower(),
            ),
        )

        for path in entries:

            if path.is_dir():

                if any(part.startswith(".") for part in path.parts) or "__pycache__" in path.parts:
                    continue
                branch = parent.add(
                    f"{escape(path.name)}"
                )
                build_directory(path, branch)

            else:

                answers = results[path]
                add_file_to_tree(
                    parent,
                    path,
                    answers,
                    selected,
                    expanded,
                )

    build_directory(directory, tree)
    return tree

def run_interface(directory: Path, results):
    
    files = get_files(results)
    if not files:
        return

    index = 0
    expanded: set[Path] = set()
    selected = files[index]

    tree = build_tree(
        directory,
        results,
        selected,
        expanded,
    )

    with Live(tree, console=console, refresh_per_second=20,screen=True) as live:
        while True:

            key = readchar.readkey()

            if key in ("q", "Q"):
                break
            elif key == readchar.key.DOWN:
                index = min(index + 1, len(files) - 1)
            elif key == readchar.key.UP:
                index = max(index - 1, 0)

            elif key in (readchar.key.ENTER, " "):
                selected = files[index]
                if selected in expanded:
                    expanded.remove(selected)
                else:
                    expanded.add(selected)

            selected = files[index]

            tree = build_tree(
                directory,
                results,
                selected,
                expanded,
            )

            live.update(tree)


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

    run_interface(
        directory,
        results,
    )


if __name__ == "__main__":
    main()

