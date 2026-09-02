"""Pre-flight check for hand-authored lab diagrams.

SVG has no layout engine and browsers fail silently or partially, so a
malformed attribute renders as a blank figure rather than an error. Run this
after editing any diagram, before committing.

    python check_svgs.py

Checks:
  1. XML well-formedness (a missing space between attributes stops rendering
     at that point — the rest of the figure simply disappears).
  2. Missing space between attributes, which is the specific mistake that
     produces "attributes construct error" in Chrome.
  3. A viewBox is present, so the figure scales in the page.
  4. title and desc elements are present for accessibility.

It cannot catch overlapping text. For that, rasterise and look:

    chrome --headless=new --screenshot=out.png --window-size=W,H file:///...
"""

from __future__ import annotations

import re
import sys
import xml.dom.minidom
from pathlib import Path

ASSETS = Path(__file__).resolve().parent / "docs" / "assets" / "labs"

BAD_ATTR = re.compile(r'"[a-zA-Z0-9_.\-]+"[a-zA-Z-]+=')
VIEWBOX = re.compile(r"viewBox=")


def check(path: Path) -> list[str]:
    problems: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")

    for m in BAD_ATTR.finditer(text):
        line = text.count("\n", 0, m.start()) + 1
        problems.append(f"line {line}: missing space between attributes — {m.group(0)}")

    try:
        xml.dom.minidom.parseString(text)
    except Exception as exc:  # noqa: BLE001 - the message is the useful part
        problems.append(f"not well-formed XML: {exc}")

    if not VIEWBOX.search(text):
        problems.append("no viewBox — the figure will not scale in the page")
    if "<title" not in text:
        problems.append("no <title> element")
    if "<desc" not in text:
        problems.append("no <desc> element")

    return problems


def main() -> int:
    files = sorted(ASSETS.glob("lab*/*.svg"))
    if not files:
        print(f"No diagrams found under {ASSETS}")
        return 1

    failed = 0
    for f in files:
        problems = check(f)
        rel = f.relative_to(ASSETS)
        if problems:
            failed += 1
            print(f"FAIL {rel}")
            for p in problems:
                print(f"       {p}")
        else:
            print(f"ok   {rel}")

    print(f"\n{len(files) - failed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
