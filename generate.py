#!/usr/bin/env python3
"""CV Generator: Markdown + YAML front matter -> PDF via WeasyPrint."""

import argparse
import os
import platform
import re
import subprocess
from pathlib import Path

# Ensure Homebrew libs are discoverable on macOS (WeasyPrint needs pango/gobject)
if platform.system() == "Darwin":
    brew_prefix = subprocess.run(
        ["brew", "--prefix"], capture_output=True, text=True
    ).stdout.strip() or "/opt/homebrew"
    lib_path = f"{brew_prefix}/lib"
    existing = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
    if lib_path not in existing:
        os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = (
            f"{lib_path}:{existing}" if existing else lib_path
        )

import yaml
import markdown
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split YAML front matter from markdown body."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", text, re.DOTALL)
    if not match:
        return {}, text
    meta = yaml.safe_load(match.group(1))
    body = match.group(2)
    return meta, body


def build_html(meta: dict, md_body: str, template_dir: Path) -> str:
    """Convert markdown to HTML body, then render into Jinja2 template."""
    html_body = markdown.markdown(
        md_body,
        extensions=["smarty", "tables", "attr_list", "nl2br"],
    )
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("base.html")
    return template.render(meta=meta, content=html_body)


def generate_pdf(html_string: str, output_path: Path, base_url: str):
    """Render HTML+CSS to PDF using WeasyPrint."""
    font_config = FontConfiguration()
    html = HTML(string=html_string, base_url=base_url)
    html.write_pdf(str(output_path), font_config=font_config)


def main():
    parser = argparse.ArgumentParser(description="Generate CV PDF from Markdown")
    parser.add_argument("input", type=Path, help="Path to markdown CV file")
    parser.add_argument("-o", "--output", type=Path, default=None)
    parser.add_argument(
        "--html", action="store_true", help="Also save intermediate HTML"
    )
    args = parser.parse_args()

    # Paths
    project_root = Path(__file__).parent
    template_dir = project_root / "templates"
    output_dir = project_root / "output"
    output_dir.mkdir(exist_ok=True)

    # Parse
    text = args.input.read_text(encoding="utf-8")
    meta, md_body = parse_frontmatter(text)

    # Build HTML
    full_html = build_html(meta, md_body, template_dir)

    # Output path
    if args.output:
        pdf_path = args.output
    else:
        safe_name = meta.get("name", "CV").replace(" ", "_")
        safe_title = meta.get("title", "").replace(" ", "_")
        pdf_path = output_dir / f"{safe_name}_{safe_title}.pdf"

    # Optionally save HTML
    if args.html:
        html_path = pdf_path.with_suffix(".html")
        html_path.write_text(full_html, encoding="utf-8")
        print(f"HTML saved: {html_path}")

    # Generate PDF (base_url points to templates/ so CSS relative paths work)
    generate_pdf(full_html, pdf_path, base_url=str(template_dir) + "/")
    print(f"PDF saved: {pdf_path}")


if __name__ == "__main__":
    main()
