import os
import argparse
from pathlib import Path

from dotenv import load_dotenv
from .jev import Jev
from .visu import export_html
from .question import Question


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

    print(
        f"Scanning {directory}"
    )

    results = scan_directory(
        directory,
        jev,
    )

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


def get_score(answers):
    report = "Does this is made by ia or human, here the report of several" \
             "questions to see if the code is made by ia:"
    for name, res in answers.items():
        report += f"{name}, {res.intruction} Answer: {res.answer} (confidence:\
{res.confidence})\n"

    jev = Jev(get_api_key())
    name = "final_answer"
    response = jev.get_response({name: Question(
            name="narrating_comments",
            type="score",
            intruction=(
                report
            ),
            criteria=[
                "it's made by a human",
                "it's made with ia or helped by ia",
            ],
        )}, report)

    response.raise_for_status()
    answer = response.json().get("answers", {}).get(name).get('score')
    return answer


def get_lines(path: Path):
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0, 0
    lines = text.splitlines()
    return len(lines)


if __name__ == "__main__":
    main()
