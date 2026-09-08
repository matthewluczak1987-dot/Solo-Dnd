#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["pypdf>=4.2.0"]
# ///
"""
Candlekeep — local adventure-book query tool.

A self-contained replacement for the private CandleKeep CLI the dnd-dm skill
was originally written against. Indexes PDFs you own from ./books/ and lets
the DM pull exact page text on demand instead of relying on training data.

    ./tools/candlekeep.py list
    ./tools/candlekeep.py toc phandelver
    ./tools/candlekeep.py pages phandelver -p "21-23"
    ./tools/candlekeep.py search phandelver "Klarg"

Books are referenced by index number or by any unique substring of the
filename, so `pages 1`, `pages phandelver` and `pages "lost mine"` all work.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BOOKS_DIR = Path(os.environ.get("CANDLEKEEP_BOOKS", REPO_ROOT / "books"))
CACHE_DIR = REPO_ROOT / ".cache" / "candlekeep"


def die(msg, code=1):
    print(f"candlekeep: {msg}", file=sys.stderr)
    sys.exit(code)


def discover():
    """Return sorted list of PDF paths in the books directory."""
    if not BOOKS_DIR.is_dir():
        die(f"no books directory at {BOOKS_DIR}\n"
            f"  Create it and drop in PDFs of adventures you own:\n"
            f"    mkdir -p {BOOKS_DIR}")
    return sorted(BOOKS_DIR.glob("*.pdf"), key=lambda p: p.name.lower())


def resolve(ref):
    """Resolve a book reference (index or filename substring) to a path."""
    books = discover()
    if not books:
        die(f"no PDFs found in {BOOKS_DIR}")

    if ref.isdigit():
        idx = int(ref)
        if not 1 <= idx <= len(books):
            die(f"book {idx} out of range (have 1..{len(books)}) — try `list`")
        return books[idx - 1]

    needle = ref.lower()
    hits = [b for b in books if needle in b.stem.lower()]
    if not hits:
        die(f"no book matching {ref!r} — try `list`")
    if len(hits) > 1:
        names = ", ".join(h.stem for h in hits)
        die(f"{ref!r} is ambiguous, matches: {names}")
    return hits[0]


def load(path):
    """Extract per-page text, memoised to .cache keyed on path+mtime+size."""
    stat = path.stat()
    key = f"{path.stem}-{int(stat.st_mtime)}-{stat.st_size}"
    key = re.sub(r"[^A-Za-z0-9._-]", "_", key)
    cache_file = CACHE_DIR / f"{key}.json"

    if cache_file.is_file():
        try:
            return json.loads(cache_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass  # corrupt cache is not fatal; just re-extract

    try:
        from pypdf import PdfReader
    except ImportError:
        die("pypdf is not installed.\n"
            "  Run this script via `uv run` (handles deps automatically):\n"
            "    ./tools/candlekeep.py list\n"
            "  Or install manually: pip install pypdf")

    reader = PdfReader(str(path))
    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception:
            die(f"{path.name} is password-protected and cannot be read")

    print(f"candlekeep: indexing {path.name} "
          f"({len(reader.pages)} pages, first run only)...", file=sys.stderr)

    pages = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception:
            pages.append("")

    outline = []
    try:
        def walk(items, depth=0):
            for item in items:
                if isinstance(item, list):
                    walk(item, depth + 1)
                    continue
                try:
                    outline.append({
                        "title": str(item.title).strip(),
                        "page": reader.get_destination_page_number(item) + 1,
                        "depth": depth,
                    })
                except Exception:
                    continue
        walk(reader.outline)
    except Exception:
        pass

    data = {"pages": pages, "outline": outline, "name": path.stem}
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(data), encoding="utf-8")
    return data


def parse_ranges(spec, total):
    """Parse '21-23,45' into a sorted list of 1-based page numbers."""
    wanted = []
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            lo, _, hi = chunk.partition("-")
            try:
                lo, hi = int(lo), int(hi)
            except ValueError:
                die(f"bad page range {chunk!r}")
            if lo > hi:
                lo, hi = hi, lo
            wanted.extend(range(lo, hi + 1))
        else:
            try:
                wanted.append(int(chunk))
            except ValueError:
                die(f"bad page number {chunk!r}")

    in_range = sorted({p for p in wanted if 1 <= p <= total})
    if not in_range:
        die(f"no pages in {spec!r} fall within this book (1..{total})")
    return in_range


def cmd_list(_args):
    books = discover()
    if not books:
        print(f"No PDFs in {BOOKS_DIR}.\n"
              "Drop in adventure PDFs you own, then re-run.")
        return
    print(f"Books in {BOOKS_DIR}:\n")
    for i, book in enumerate(books, 1):
        size = book.stat().st_size / (1024 * 1024)
        print(f"  [{i}]  {book.stem}  ({size:.1f} MB)")
    print(f"\n{len(books)} book(s). Query with: "
          f"./tools/candlekeep.py pages <id> -p \"21-23\"")


def cmd_toc(args):
    book = resolve(args.book)
    data = load(book)
    print(f"# {data['name']} — {len(data['pages'])} pages\n")
    if not data["outline"]:
        print("(No embedded table of contents in this PDF.)")
        print("Use `search` to locate sections by keyword instead.")
        return
    for entry in data["outline"]:
        print(f"{'  ' * entry['depth']}{entry['title']}  ...  p.{entry['page']}")


def cmd_pages(args):
    book = resolve(args.book)
    data = load(book)
    pages = data["pages"]
    for num in parse_ranges(args.pages, len(pages)):
        text = pages[num - 1].strip()
        print(f"\n{'=' * 70}\n{data['name']} — page {num}\n{'=' * 70}\n")
        print(text if text else "(no extractable text — likely a full-page image or map)")


def cmd_search(args):
    book = resolve(args.book)
    data = load(book)
    needle = args.query.lower()
    hits = 0
    for i, text in enumerate(data["pages"], 1):
        if needle not in text.lower():
            continue
        hits += 1
        for line in text.splitlines():
            if needle in line.lower():
                print(f"p.{i:>4}: {line.strip()}")
        if hits >= args.limit:
            print(f"\n(stopped at {args.limit} matching pages; "
                  f"use --limit to see more)")
            return
    if not hits:
        print(f"No matches for {args.query!r} in {data['name']}.")
    else:
        print(f"\n{hits} matching page(s).")


def main():
    parser = argparse.ArgumentParser(
        prog="candlekeep",
        description="Query adventure PDFs you own, by page.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="list available books").set_defaults(fn=cmd_list)

    p_toc = sub.add_parser("toc", help="show a book's table of contents")
    p_toc.add_argument("book")
    p_toc.set_defaults(fn=cmd_toc)

    p_pages = sub.add_parser("pages", help="print text from page ranges")
    p_pages.add_argument("book")
    p_pages.add_argument("-p", "--pages", required=True,
                         help='e.g. "21-23" or "5,9,14-16"')
    p_pages.set_defaults(fn=cmd_pages)

    p_search = sub.add_parser("search", help="find a keyword across pages")
    p_search.add_argument("book")
    p_search.add_argument("query")
    p_search.add_argument("--limit", type=int, default=20,
                          help="max matching pages to show (default 20)")
    p_search.set_defaults(fn=cmd_search)

    args = parser.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
