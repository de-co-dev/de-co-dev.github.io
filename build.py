#!/usr/bin/env python3
"""Builds the public legal pages of every project from its Markdown texts.

    python3 build.py

Each project is a folder with a `textos/` subfolder holding
terms-es.md, terms-en.md, privacy-es.md and privacy-en.md. To add a project,
create its folder + textos/ and add it to PROJECTS below. The .md files are
the source; the .html files are generated next to them — commit both.

Only the small Markdown subset the texts use is supported:
# / ## headings, paragraphs, "- " lists and a "> " note.
"""

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# folder name -> name shown on the pages
PROJECTS = {
    "pillreminder": "Pill Reminder",
}

PAGES = {
    # (doc, lang): output path relative to the project folder
    ("terms", "es"): "es/terminos.html",
    ("privacy", "es"): "es/privacidad.html",
    ("terms", "en"): "en/terms.html",
    ("privacy", "en"): "en/privacy.html",
}

LABELS = {
    "es": {"terms": "Términos y condiciones", "privacy": "Política de privacidad", "other_lang": "English"},
    "en": {"terms": "Terms and Conditions", "privacy": "Privacy Policy", "other_lang": "Español"},
}

STYLE = """
  :root { --bg:#f5faff; --ink:#1e3a5f; --sub:#6b829e; --body:#4a5f78; --blue:#2b78d0; --line:#e1ecf8; --red:#e2574c; --redbg:#fdecee; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--body); font:16px/1.55 "Source Sans 3", -apple-system, system-ui, sans-serif; }
  header { display:flex; align-items:center; justify-content:space-between; gap:12px; max-width:720px; margin:0 auto; padding:20px 20px 0; }
  .brand { display:flex; align-items:center; gap:10px; font-weight:900; color:var(--ink); text-decoration:none; }
  .badge { width:34px; height:34px; border-radius:10px; background:linear-gradient(135deg,#5aa6f2,#2b78d0); display:grid; place-items:center; }
  .badge span { width:18px; height:9px; border-radius:5px; background:#fff; transform:rotate(-40deg); }
  .lang { color:var(--blue); font-weight:700; text-decoration:none; font-size:15px; }
  main { max-width:720px; margin:0 auto; padding:8px 20px 48px; }
  h1 { color:var(--ink); font-weight:900; font-size:32px; line-height:1.15; margin:24px 0 6px; }
  .updated { color:var(--sub); font-weight:600; font-size:14px; margin:0 0 24px; }
  h2 { color:var(--ink); font-size:19px; font-weight:700; margin:28px 0 6px; }
  h3 { color:var(--sub); font-size:14px; text-transform:uppercase; letter-spacing:.04em; margin:28px 0 4px; }
  p, li { margin:0 0 10px; }
  ul { padding-left:20px; margin:0 0 10px; }
  a { color:var(--blue); }
  .links a { display:block; font-weight:700; text-decoration:none; padding:6px 0; }
  .note { margin:32px 0 0; padding:14px 16px; border-radius:14px; background:var(--redbg); color:var(--red); font-weight:700; font-size:15px; }
  nav.other { margin-top:32px; padding-top:20px; border-top:1px solid var(--line); font-weight:700; }
  nav.other a { text-decoration:none; }
"""

HEAD = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700;900&display=swap" rel="stylesheet">
<style>{style}</style>
</head>
<body>
"""

DOC_PAGE = HEAD + """<header>
  <a class="brand" href="{home}"><span class="badge"><span></span></span>{project}</a>
  <a class="lang" href="{other_lang_href}" hreflang="{other_lang_code}">{other_lang}</a>
</header>
<main>
<h1>{doc_title}</h1>
{body}
<nav class="other"><a href="{other_doc_href}">{other_doc} →</a></nav>
</main>
</body>
</html>
"""

LIST_PAGE = HEAD + """<main>
<h1>{heading}</h1>
{body}
</main>
</body>
</html>
"""


def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    return re.sub(r"([\w.+-]+@[\w-]+(?:\.[\w-]+)+)", r'<a href="mailto:\1">\1</a>', text)


def to_html(md: str) -> tuple[str, str]:
    """Returns (title, body html)."""
    title, parts, items = "", [], []

    def flush_list():
        if items:
            parts.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in items) + "</ul>")
            items.clear()

    for block in md.strip().split("\n\n"):
        lines = block.strip().split("\n")
        if all(l.startswith("- ") for l in lines):
            items.extend(l[2:] for l in lines)
            continue
        flush_list()
        line = block.strip()
        if line.startswith("# "):
            title = line[2:]
        elif line.startswith("## "):
            parts.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("> "):
            parts.append(f'<aside class="note">{inline(line[2:])}</aside>')
        elif not parts and title:
            # The first paragraph after the title is the "last updated" line.
            parts.append(f'<p class="updated">{inline(line)}</p>')
        else:
            parts.append(f"<p>{inline(line)}</p>")
    flush_list()
    return title, "\n".join(parts)


def up(path: str) -> str:
    """Relative prefix from a page at `path` back to its project folder."""
    return "../" * path.count("/")


def links_for(project_prefix: str) -> str:
    out = []
    for lang, name in (("es", "Español"), ("en", "English")):
        out.append(f"<h3>{name}</h3><div class=\"links\">")
        for doc in ("terms", "privacy"):
            out.append(f'<a href="{project_prefix}{PAGES[(doc, lang)]}">{LABELS[lang][doc]}</a>')
        out.append("</div>")
    return "\n".join(out)


def build_project(folder: str, name: str) -> None:
    project_dir = ROOT / folder
    for (doc, lang), path in PAGES.items():
        doc_title, body = to_html((project_dir / "textos" / f"{doc}-{lang}.md").read_text(encoding="utf-8"))
        other_lang = "en" if lang == "es" else "es"
        other_doc = "privacy" if doc == "terms" else "terms"
        page = DOC_PAGE.format(
            lang=lang,
            title=html.escape(f"{doc_title} · {name}"),
            style=STYLE,
            project=html.escape(name),
            doc_title=html.escape(doc_title),
            body=body,
            home=up(path) + "index.html",
            other_lang=LABELS[lang]["other_lang"],
            other_lang_code=other_lang,
            other_lang_href=up(path) + PAGES[(doc, other_lang)],
            other_doc=LABELS[lang][other_doc],
            other_doc_href=up(path) + PAGES[(other_doc, lang)],
        )
        target = project_dir / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page, encoding="utf-8")

    (project_dir / "index.html").write_text(
        LIST_PAGE.format(lang="es", title=html.escape(name), style=STYLE,
                         heading=html.escape(name), body=links_for("")),
        encoding="utf-8",
    )


def main() -> None:
    for folder, name in PROJECTS.items():
        build_project(folder, name)
    projects = "\n".join(
        f'<div class="links"><a href="{folder}/index.html">{html.escape(name)}</a></div>'
        for folder, name in PROJECTS.items()
    )
    (ROOT / "index.html").write_text(
        LIST_PAGE.format(lang="es", title="de-co-dev", style=STYLE, heading="Proyectos", body=projects),
        encoding="utf-8",
    )
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    print("Built", len(PROJECTS), "project(s)")


if __name__ == "__main__":
    main()
