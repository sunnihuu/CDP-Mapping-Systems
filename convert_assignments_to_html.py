#!/usr/bin/env python3
"""convert_assignments_to_html.py

Find all Jupyter notebooks under `Assignments/` and convert them to HTML
into a `docs/Assignments/...` folder, preserving relative paths.

Usage:
  python3 convert_assignments_to_html.py

This script tries to use `nbformat` and `nbconvert`. If they are not
installed it will print instructions to install them.
"""
from __future__ import annotations
import os
from pathlib import Path

SRC_DIR = Path("Assignments")
OUT_BASE = Path("docs")


def find_notebooks(src: Path):
    for root, dirs, files in os.walk(src):
        for f in files:
            if f.endswith(".ipynb"):
                yield Path(root) / f


def ensure_out_path(p: Path):
    p.parent.mkdir(parents=True, exist_ok=True)


def convert_notebook(nb_path: Path, out_path: Path):
    try:
        import nbformat
        from nbconvert import HTMLExporter
    except ImportError:
        print("Missing required packages: nbformat and nbconvert")
        print("Install with: python3 -m pip install --user nbformat nbconvert")
        raise

    nb = nbformat.read(nb_path, as_version=4)
    exporter = HTMLExporter()
    # Use default template; users can customize later.
    (body, resources) = exporter.from_notebook_node(nb)
    ensure_out_path(out_path)
    out_path.write_text(body, encoding="utf-8")


def main():
    if not SRC_DIR.exists():
        print(f"Source directory {SRC_DIR} does not exist. Nothing to convert.")
        return

    notebooks = list(find_notebooks(SRC_DIR))
    if not notebooks:
        print("No notebooks found under Assignments/. Nothing to convert.")
        return

    converted = []
    failed = []
    for nb in notebooks:
        rel = nb.relative_to(SRC_DIR)
        out_path = OUT_BASE / SRC_DIR.name / rel.with_suffix(".html")
        try:
            convert_notebook(nb, out_path)
            converted.append(out_path)
            print(f"Converted: {nb} -> {out_path}")
        except Exception as e:
            failed.append((nb, e))
            print(f"Failed to convert {nb}: {e}")

    print("\nSummary:")
    print(f"  Converted: {len(converted)} notebooks")
    print(f"  Failed: {len(failed)} notebooks")
    if failed:
        print("See errors above. Consider installing required packages:")
        print("  python3 -m pip install --user nbformat nbconvert")


if __name__ == "__main__":
    main()
