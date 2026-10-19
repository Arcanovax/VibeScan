import json
from pathlib import Path
import webbrowser


def _finalize(node):
    if "children" in node:
        return {
            "name": node["name"],
            "children": [_finalize(c) for c in node["children"].values()],
        }
    return node


def export_html(data: dict, output="scan.html") -> Path:

    with (open("srcs/template.html", "r") as f):
        HTML_TEMPLATE = f.read()

    payload = json.dumps(_finalize(data),
                         ensure_ascii=False).replace("</", "<\\/")
    html = HTML_TEMPLATE.replace("__DATA__", payload)
    out = Path(output).resolve()
    out.write_text(html, encoding="utf-8")

    webbrowser.open(out.as_uri())
    return out
