"""Process 2026 lab HTML files for the public website.

Strips:
- Instructor/professor headers
- Deliverables sections
- Submission checklists
- Grading rubrics
- TOC links to removed sections
"""

import re
import sys
from pathlib import Path

LABS_SRC = Path(r"D:\git_repos\intro-to-robotics-labs\2026_labs")
LABS_DST = Path(r"D:\git_repos\MEMS-Intro-to-Robotics.github.io\docs\labs")

LAB_TITLES = {
    1: "VM and Git Setup",
    2: "ROS 2 CLI Fundamentals",
    3: "Shell Scripting for Robot Control",
    4: "ROS 2 Python Nodes",
    5: "Motion Planning with MoveIt 2",
    6: "Pick-and-Place Manipulation",
    7: "Crazyflie PID Tuning",
    8: "Real Hardware Drone Control",
    9: "Autonomous SLAM-Based Exploration",
    10: "Real TurtleBot 4 Deployment",
}

# Section IDs to remove entirely (opening <section id="..."> to </section>)
REMOVE_SECTION_IDS = {
    "deliverables", "deliverables-glance", "checklist",
}


def remove_header_block(html: str) -> str:
    """Remove <header>...</header> blocks."""
    return re.sub(r'<header>\s*.*?</header>\s*', '', html, flags=re.DOTALL)


def remove_lab7_course_info(html: str) -> str:
    """Remove the course info paragraph from lab 7's format."""
    # Pattern: <div class="lab-manual-container"> followed by <p>Course: ECE 383...
    pattern = (
        r'(<div class="lab-manual-container">)\s*'
        r'<p>Course:.*?</p>\s*'
    )
    return re.sub(pattern, r'\1\n', html, flags=re.DOTALL)


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
        # Also from sec-4 style TOC (lab 7 deliverables)
        r'\s*<li><a href="#sec-4">4\. Deliverables</a></li>',
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


def clean_lab(html: str, lab_num: int) -> str:
    """Apply all cleaning transformations."""
    # 0. Replace Canvas-hosted images with placeholders
    html = replace_canvas_images(html)

    # 1. Remove instructor headers
    html = remove_header_block(html)

    # Lab 7 has a different header format
    if lab_num == 7:
        html = remove_lab7_course_info(html)

    # 2. Remove section-based deliverables/checklists
    html = remove_sections_by_id(html)

    # 3. Remove h1-based deliverables (labs 5, 6)
    if lab_num in (5, 6):
        html = remove_h1_deliverables_sections(html)
        html = remove_h3_deliverables_checklist(html)

    # Lab 7 uses h1 id="sec-4" for deliverables
    if lab_num == 7:
        html = remove_h1_deliverables_sections(html)

    # 4. Remove grading rubrics
    html = remove_grading_rubric(html)

    # 5. Remove TOC links to removed sections
    html = remove_toc_links(html)

    # 6. Remove inline "Deliverables (at a glance)" subsections
    # These are <h4>Deliverables...</h4> followed by lists and notes
    html = re.sub(
        r'<h4>Deliverables[^<]*</h4>\s*<ul>.*?</ul>\s*'
        r'(?:<blockquote[^>]*>.*?</blockquote>\s*)?',
        '', html, flags=re.DOTALL,
    )
    # Also remove "Deliverables At a Glance" as <h1> in labs 5/6 intro areas
    # (already handled by remove_h1_deliverables_sections)

    # 7. Clean up excess whitespace
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


def main():
    LABS_DST.mkdir(parents=True, exist_ok=True)

    for lab_num in range(1, 11):
        src = LABS_SRC / f"lab_{lab_num}.html"
        if not src.exists():
            print(f"WARNING: {src} not found, skipping")
            continue

        html = src.read_text(encoding="utf-8")
        cleaned = clean_lab(html, lab_num)
        md = wrap_in_markdown(cleaned, lab_num)

        dst = LABS_DST / f"lab_{lab_num:02d}.md"
        dst.write_text(md, encoding="utf-8")
        print(f"Processed lab {lab_num:02d} -> {dst.name} ({len(html)} -> {len(cleaned)} chars)")

    print("\nDone! All labs processed.")


if __name__ == "__main__":
    main()
