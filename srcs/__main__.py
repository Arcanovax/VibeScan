import argparse
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from dulwich import porcelain

from .jev import Jev
from .visu import export_html


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

        if not path._str.endswith((".py", ".c", ".rs")):
            continue

        if not path.is_file():
            continue

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        answers = jev.scan(content)
        results[path] = answers

    return results


def get_score(answers):
    report = "Does this is made by ia or human, here the report of several" \
             "questions to see if the code is made by ia:"
    for name, res in answers.items():
        report += f"{name}, {res.intruction} Answer: {res.answer} (confidence:\
{res.confidence})\n"
    jev = Jev(get_api_key())
    score = jev.get_final_score(report)
    return score


def get_lines(path: Path):
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0, 0
    lines = text.splitlines()
    return len(lines)

class Parser:
    _parser: argparse.ArgumentParser
    _args: Any

    def __init__(self) -> None:
        self._parser = argparse.ArgumentParser()
        self._parser.add_argument("--code", default=".")
        self._parser.add_argument("--git", default=None)
        self._parser.add_argument("--branch", default="main")
        self._parser.add_argument("--dist", default="dist")

        self._args = self._parser.parse_args()

    def get_args(self) -> Any:
        return self._args

    def get_directory_path(self) -> Path:
        if self.get_args().git:
            porcelain.clone(
                self._args.git,
                self._args.dist,
                checkout=self._args.branch
            )
            return Path(self._args.dist).resolve()
        return Path(self._args.code).resolve()


def main():
    parser = Parser()
    try:
        directory = parser.get_directory_path()
    except PermissionError as e:
        print(e)
        return

    jev = Jev(get_api_key())

    print(f"Scanning {directory}")

    results = scan_directory(directory, jev)
    root = {"name": directory.name or str(directory), "children": {}}

    for path, answer in results.items():
        try:
            rel = path.relative_to(directory)
        except ValueError:
            continue

        node = root
        for part in rel.parts[:-1]:
            node = node["children"].setdefault(part,
                                               {"name": part, "children": {}})

        lines = get_lines(path)
        node["children"][rel.parts[-1]] = {
            "name": rel.parts[-1],
            "path": rel.as_posix(),
            "lines": lines,
            "score": get_score(answer),
            "answers": {
                name: {
                    "answer": str(getattr(content, "answer", "?")),
                    "confidence": getattr(content, "confidence", None),
                }
                for name, content in answer.items()
            },
        }
    export_html(root)


if __name__ == "__main__":
    main()
