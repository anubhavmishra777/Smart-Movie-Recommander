from __future__ import annotations

import html
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "project_report.md"
BUILD_DIR = ROOT / "docs"
HTML_PATH = BUILD_DIR / "project_report_print.html"
PDF_PATH = BUILD_DIR / "Smart_Movie_Recommender_Project_Report.pdf"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")


def inline_markdown(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    return escaped


def render_table(lines: list[str]) -> str:
    rows = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)

    if not rows:
        return ""

    output = ["<table>"]
    for index, cells in enumerate(rows):
        tag = "th" if index == 0 else "td"
        output.append("<tr>")
        for cell in cells:
            output.append(f"<{tag}>{inline_markdown(cell)}</{tag}>")
        output.append("</tr>")
    output.append("</table>")
    return "\n".join(output)


def markdown_to_html(markdown: str) -> str:
    lines = markdown.splitlines()
    output: list[str] = []
    paragraph: list[str] = []
    list_open = False
    code_open = False
    table_lines: list[str] = []

    def close_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            output.append(f"<p>{inline_markdown(' '.join(paragraph))}</p>")
            paragraph = []

    def close_list() -> None:
        nonlocal list_open
        if list_open:
            output.append("</ul>")
            list_open = False

    def close_table() -> None:
        nonlocal table_lines
        if table_lines:
            output.append(render_table(table_lines))
            table_lines = []

    for raw_line in lines:
        line = raw_line.rstrip()

        if line.startswith("```"):
            close_paragraph()
            close_list()
            close_table()
            if code_open:
                output.append("</code></pre>")
            else:
                output.append("<pre><code>")
            code_open = not code_open
            continue

        if code_open:
            output.append(html.escape(line))
            continue

        if line.startswith("|") and line.endswith("|"):
            close_paragraph()
            close_list()
            table_lines.append(line)
            continue
        close_table()

        if not line.strip():
            close_paragraph()
            close_list()
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading_match:
            close_paragraph()
            close_list()
            level = min(len(heading_match.group(1)), 3)
            text = heading_match.group(2)
            output.append(f"<h{level}>{inline_markdown(text)}</h{level}>")
            continue

        if line.strip() == "---":
            close_paragraph()
            close_list()
            output.append("<hr>")
            continue

        ordered_match = re.match(r"^\d+\.\s+(.+)$", line)
        bullet_match = re.match(r"^[-*]\s+(.+)$", line)
        item = ordered_match.group(1) if ordered_match else bullet_match.group(1) if bullet_match else None
        if item is not None:
            close_paragraph()
            if not list_open:
                output.append("<ul>")
                list_open = True
            output.append(f"<li>{inline_markdown(item)}</li>")
            continue

        paragraph.append(line.strip())

    close_paragraph()
    close_list()
    close_table()
    return "\n".join(output)


def build_html(body: str) -> str:
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Smart Movie Recommender Project Report</title>
<style>
@page {{
    size: A4;
    margin: 20mm 17mm 19mm;
}}
body {{
    font-family: "Times New Roman", Times, serif;
    color: #111;
    background: white;
    font-size: 11.8pt;
    line-height: 1.42;
}}
h1 {{
    text-align: center;
    font-size: 16pt;
    margin: 0 0 18pt;
    padding-bottom: 8pt;
    border-bottom: 1px solid #111;
    page-break-after: avoid;
}}
h2 {{
    font-size: 15pt;
    margin: 18pt 0 8pt;
    page-break-after: avoid;
}}
h3 {{
    font-size: 13pt;
    margin: 14pt 0 6pt;
    page-break-after: avoid;
}}
p {{
    margin: 0 0 8pt;
    text-align: justify;
}}
ul {{
    margin: 0 0 9pt 20pt;
    padding: 0;
}}
li {{
    margin: 0 0 4pt;
}}
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 8pt 0 14pt;
}}
th, td {{
    border: 1px solid #333;
    padding: 5pt 6pt;
    vertical-align: top;
    font-size: 10pt;
}}
tr {{
    page-break-inside: avoid;
}}
th {{
    background: #efefef;
    font-weight: bold;
    text-align: left;
}}
pre {{
    border: 1px solid #333;
    background: #f7f7f7;
    padding: 8pt;
    white-space: pre-wrap;
    font-family: Consolas, monospace;
    font-size: 9.5pt;
}}
code {{
    font-family: Consolas, monospace;
    font-size: 10pt;
}}
hr {{
    border: 0;
    border-top: 1px solid #111;
    margin: 12pt 0;
}}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def main() -> None:
    BUILD_DIR.mkdir(exist_ok=True)
    body = markdown_to_html(SOURCE.read_text(encoding="utf-8"))
    HTML_PATH.write_text(build_html(body), encoding="utf-8")

    if not EDGE.exists():
        raise SystemExit(f"Microsoft Edge was not found at {EDGE}")

    subprocess.run(
        [
            str(EDGE),
            "--headless",
            "--disable-gpu",
            f"--print-to-pdf={PDF_PATH}",
            str(HTML_PATH),
        ],
        check=True,
    )
    print(PDF_PATH)


if __name__ == "__main__":
    main()
