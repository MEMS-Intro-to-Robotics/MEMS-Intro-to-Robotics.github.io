"""Process 2026 lab HTML files for the public website.

Strips:
- Instructor/professor headers
- Deliverables sections
- Submission checklists
- Grading rubrics
- TOC links to removed sections

Also applies public-site rewrites that keep shared cross-lab references in one
place instead of repeating the same material inside every generated lab page.
"""

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_LABS_SRC = REPO_ROOT.parent / "intro-to-robotics-labs" / "2026_fall_labs"
DEFAULT_LABS_DST = REPO_ROOT / "docs" / "labs"

LAB_TITLES = {
    1: "VM and Git Setup",
    2: "ROS 2 CLI Fundamentals",
    3: "Shell Scripting for Robot Control",
    4: "ROS 2 Python Nodes",
    5: "Motion Planning with MoveIt 2",
    6: "Pick-and-Place Manipulation",
    7: "Crazyflie PID Tuning",
    8: "Real Hardware Drone Control",
    9: "TurtleBot 4 Sensors",
    10: "SLAM and Frontier Exploration in the Garage Labs",
}

# Section IDs to remove entirely (opening <section id="..."> to </section>)
REMOVE_SECTION_IDS = {
    "deliverables", "deliverables-glance", "checklist",
}

def remove_header_block(html: str) -> str:
    """Remove <header>...</header> blocks."""
    return re.sub(r'<header>\s*.*?</header>\s*', '', html, flags=re.DOTALL)


def remove_sections_by_id(html: str) -> str:
    """Remove <section id="deliverables|checklist|...">...</section> blocks."""
    for section_id in REMOVE_SECTION_IDS:
        pattern = rf'<section id="{section_id}">\s*.*?</section>\s*'
        html = re.sub(pattern, '', html, flags=re.DOTALL)
    return html


def remove_h1_deliverables_sections(html: str) -> str:
    """Remove deliverables sections that use <h1> headings (labs 5, 6).

    Removes from <h1>Deliverables...</h1> to the next <h1> or end of content.
    """
    # Match <h1> containing "Deliverables" through to next <h1> or end
    # Handle both "Deliverables" standalone sections
    patterns = [
        # <h1>Deliverables...</h1> to next <h1> or end
        r'<h1>[^<]*Deliverables[^<]*</h1>.*?(?=<h1>|\Z)',
        # <h1 id="sec-4">4. Deliverables</h1> style
        r'<h1 id="sec-\d+">\d+\.\s*Deliverables[^<]*</h1>.*?(?=<h1|\Z)',
    ]
    for pattern in patterns:
        html = re.sub(pattern, '', html, flags=re.DOTALL)
    return html


def remove_h3_deliverables_checklist(html: str) -> str:
    """Remove <h3>Deliverables Checklist</h3> subsections (lab 5)."""
    pattern = r'<h3>Deliverables Checklist</h3>.*?(?=<h[123]>|<h1|</div>\s*$|\Z)'
    html = re.sub(pattern, '', html, flags=re.DOTALL)
    return html


def remove_toc_links(html: str) -> str:
    """Remove TOC entries linking to removed sections."""
    # Remove <li> entries containing links to deliverables, checklist, submission
    patterns = [
        r'\s*<li><a href="#deliverables[^"]*">[^<]*</a></li>',
        r'\s*<li><a href="#checklist">[^<]*</a></li>',
    ]
    for pattern in patterns:
        html = re.sub(pattern, '', html)
    return html


def remove_grading_rubric(html: str) -> str:
    """Remove grading rubric subsections."""
    # <h3>6.2 Grading Rubric...</h3> to next <h2>|<h1>|</section>|end
    pattern = r'<h3>[^<]*Grading Rubric[^<]*</h3>.*?(?=<h[12]>|</section>|\Z)'
    html = re.sub(pattern, '', html, flags=re.DOTALL)
    return html


def remove_submission_grading_section(html: str) -> str:
    """Remove 'Submission & Grading' sections (lab 10)."""
    pattern = r'<section id="checklist">\s*<h2>[^<]*Submission[^<]*Grading[^<]*</h2>.*?</section>'
    html = re.sub(pattern, '', html, flags=re.DOTALL)
    return html


def require_replace(html: str, old: str, new: str, label: str) -> str:
    """Replace an exact snippet once, or fail loudly if the source drifted."""
    if old not in html:
        raise ValueError(f"{label}: expected snippet not found")
    return html.replace(old, new, 1)



def apply_public_site_dedup(html: str, lab_num: int) -> str:
    """Apply shared-reference rewrites that should survive regeneration.

    None are needed now: Lab 10's block for the Humble maze manual was retired on 2026-11-09,
    when the lab was rebuilt to the conventions (no repeated setup prose to rewrite).
    """
    return html


def replace_canvas_images(html: str) -> str:
    """Replace Canvas-hosted images with grey placeholder divs."""
    def make_placeholder(match):
        full_tag = match.group(0)
        # Extract alt text
        alt_match = re.search(r'alt="([^"]*)"', full_tag)
        alt = alt_match.group(1) if alt_match else "Image"
        # Extract width/height if present
        w_match = re.search(r'width="(\d+)"', full_tag)
        h_match = re.search(r'height="(\d+)"', full_tag)
        width = w_match.group(1) if w_match else "400"
        height = h_match.group(1) if h_match else "200"
        # Also check for equation images - keep alt text as-is for context
        if 'equation_image' in full_tag:
            # For LaTeX equations rendered as images, use proper MathJax delimiters
            eq_match = re.search(r'data-equation-content="([^"]*)"', full_tag)
            eq = eq_match.group(1).strip() if eq_match else alt
            # Multi-line or long equations get display mode, short ones inline
            if '\n' in eq or len(eq) > 60:
                # Store LaTeX in data attribute to survive markdown processing
                import html as html_mod
                escaped_attr = html_mod.escape(eq, quote=True)
                return (
                    f'<span class="math-display" '
                    f'data-latex="{escaped_attr}">'
                    f'</span>'
                )
            import html as html_mod
            escaped_attr = html_mod.escape(eq, quote=True)
            return (
                f'<span class="math-inline" '
                f'data-latex="{escaped_attr}">'
                f'</span>'
            )
        # Skip empty alt text placeholders
        if not alt or alt.strip() == "":
            alt = "Image placeholder"
        return (
            f'<div class="image-placeholder" style="'
            f'background:#e0e0e0;border:2px dashed #999;border-radius:8px;'
            f'display:flex;align-items:center;justify-content:center;'
            f'color:#666;font-style:italic;text-align:center;padding:1em;'
            f'max-width:{width}px;min-height:{min(int(height), 150)}px;'
            f'margin:1em auto;">'
            f'{alt}</div>'
        )

    # Match img tags with canvas.duke.edu URLs
    html = re.sub(
        r'<img[^>]*src="https://canvas\.duke\.edu/[^"]*"[^>]*/?>',
        make_placeholder,
        html,
    )
    return html


def redact_secrets(html: str) -> str:
    """Redact license keys and similar credentials before public export."""
    html = re.sub(
        r'FASTX_ACTIVATION_KEY="[^"]*"',
        'FASTX_ACTIVATION_KEY="&lt;key-from-course-staff&gt;"',
        html,
    )
    html = re.sub(
        r'Enter the license key when prompted: <code>[^<]*</code>',
        'Enter the license key provided by course staff when prompted.',
        html,
    )
    # Backstop: never let a FastX-style key (4x4 digit groups) reach the site.
    html = re.sub(r'\b\d{4}-\d{4}-\d{4}-\d{4}\b', '&lt;redacted&gt;', html)
    return html


def clean_lab(html: str, lab_num: int) -> str:
    """Apply all cleaning transformations."""
    # 0. Redact credentials, then replace Canvas-hosted images with placeholders
    html = redact_secrets(html)
    html = replace_canvas_images(html)

    # 1. Remove instructor headers, and HTML comments (staff TODO notes)
    html = remove_header_block(html)
    html = re.sub(r'<!--.*?-->[ \t]*\n?', '', html, flags=re.DOTALL)

    # 2. Remove section-based deliverables/checklists
    html = remove_sections_by_id(html)

    # 3. Remove h1-based deliverables (labs 5, 6)
    if lab_num in (5, 6):
        html = remove_h1_deliverables_sections(html)
        html = remove_h3_deliverables_checklist(html)

    # 4. Remove grading rubrics
    html = remove_grading_rubric(html)

    # 5. Remove TOC links to removed sections
    html = remove_toc_links(html)

    # 6. Remove inline "Deliverables (at a glance)" subsections
    # These are <h4>Deliverables...</h4> followed by lists and notes
    # Consume through any nested lists and trailing blockquotes up to the next
    # heading/section boundary (a lazy <ul>.*?</ul> stops at the first nested
    # </ul> and strands the outer list's tail).
    html = re.sub(
        r'<h4>Deliverables[^<]*</h4>.*?(?=<h[1-6][ >]|<section\b|</section)',
        '', html, flags=re.DOTALL,
    )
    # Also remove "Deliverables At a Glance" as <h1> in labs 5/6 intro areas
    # (already handled by remove_h1_deliverables_sections)

    # 7. Clean up excess whitespace
    html = re.sub(r'\n{3,}', '\n\n', html)

    # 8. Apply public-site dedup so regeneration preserves shared references
    html = apply_public_site_dedup(html, lab_num)
    html = re.sub(r'\n{3,}', '\n\n', html)

    return html.strip()


def wrap_in_markdown(html: str, lab_num: int) -> str:
    """Wrap cleaned HTML in a markdown page."""
    title = LAB_TITLES[lab_num]
    return f"""---
title: "Lab {lab_num:02d}: {title}"
---

# Lab {lab_num:02d}: {title}

<div class="lab-content">

{html}

</div>
"""


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--src",
        type=Path,
        default=DEFAULT_LABS_SRC,
        help="Path to the source lab HTML directory",
    )
    parser.add_argument(
        "--dst",
        type=Path,
        default=DEFAULT_LABS_DST,
        help="Path to the destination markdown directory",
    )
    parser.add_argument(
        "--labs",
        type=int,
        nargs="+",
        default=list(range(1, 11)),
        help="Lab numbers to process (default: all)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None):
    args = parse_args(argv if argv is not None else sys.argv[1:])
    labs_src = args.src.resolve()
    labs_dst = args.dst.resolve()

    if not labs_src.exists():
        raise SystemExit(f"Source lab directory not found: {labs_src}")

    labs_dst.mkdir(parents=True, exist_ok=True)

    for lab_num in args.labs:
        src = labs_src / f"lab_{lab_num}.html"
        if not src.exists():
            print(f"WARNING: {src} not found, skipping")
            continue

        html = src.read_text(encoding="utf-8")
        cleaned = clean_lab(html, lab_num)
        md = wrap_in_markdown(cleaned, lab_num)

        dst = labs_dst / f"lab_{lab_num:02d}.md"
        dst.write_text(md, encoding="utf-8", newline="\n")
        print(f"Processed lab {lab_num:02d} -> {dst.name} ({len(html)} -> {len(cleaned)} chars)")

    print("\nDone! All labs processed.")


if __name__ == "__main__":
    main(sys.argv[1:])
