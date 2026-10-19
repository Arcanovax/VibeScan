import json
from pathlib import Path
import webbrowser


def _ai_score(answers):
    r = answers.get("is_made_by_ai")
    if r is None:
        return None
    ans = getattr(r, "answer", None)
    is_ai = ans if isinstance(ans, bool) else str(ans).strip().lower() in ("true", "yes", "oui", "1")
    conf = getattr(r, "confidence", None)
    if conf is None:
        return 1.0 if is_ai else 0.0
    conf = max(0.0, min(1.0, float(conf)))
    return conf if is_ai else 1.0 - conf


def _count_loc(path: Path):
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0, 0
    lines = text.splitlines()
    loc = sum(1 for line in lines if line.strip())
    return loc, len(lines)


def build_data(directory: Path, results: dict) -> dict:
    root = {"name": directory.name or str(directory), "children": {}}

    for path, answers in results.items():
        try:
            rel = path.relative_to(directory)
        except ValueError:
            continue

        node = root
        for part in rel.parts[:-1]:
            node = node["children"].setdefault(part, {"name": part, "children": {}})

        loc, total = _count_loc(path)
        node["children"][rel.parts[-1]] = {
            "name": rel.parts[-1],
            "path": rel.as_posix(),
            "loc": loc,
            "lines": total,
            "score": _ai_score(answers),
            "answers": {
                name: {
                    "answer": str(getattr(content, "answer", "?")),
                    "confidence": getattr(content, "confidence", None),
                }
                for name, content in answers.items()
            },
        }

    def finalize(n):
        if "children" in n:
            kids = [finalize(c) for c in n["children"].values()]
            return {"name": n["name"], "children": kids}
        return n

    return finalize(root)


def export_html(directory: Path, results: dict, output="scan.html") -> Path:

    with (open("srcs/template.html", "r") as f):
        HTML_TEMPLATE = f.read()

    data = build_data(Path(directory), results)
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = HTML_TEMPLATE.replace("__DATA__", payload)
    out = Path(output).resolve()
    out.write_text(html, encoding="utf-8")

    webbrowser.open(out.as_uri())
    return out
