# For educators

This site is designed to be more than an internal course appendix. The goal is to make the lab setup, references, and workflow notes understandable and reusable for instructors outside the original course context.

## What transfers well

- ROS 2 and Docker onboarding patterns for student lab environments
- Quick-reference documentation for Linux, Git, Docker, and ROS 2
- Simulation-first lab organization for manipulation and controls work
- Technical reference pages that sit beside, not inside, assignment PDFs

## What is still course-specific

- Duke VCM and FastX assumptions in the quick-start workflow
- Local image tags and registry paths
- Course-specific package names and support channels
- Any grading or sign-off expectations described in individual labs

## A practical adaptation path

1. Start by copying the high-level structure rather than every course detail.
2. Replace infrastructure-specific setup pages first.
3. Keep lab pages task-oriented and move long references into shared technical guides.
4. Publish the result as a public docs site so students and outside instructors can use the same canonical URL.

## Why a public docs site helps

- It is easier to cite in papers, workshops, and course materials.
- Outside educators can browse before they commit to adopting anything.
- References remain accessible even when a handout or LMS page changes.
- Documentation review can happen in the same repository as the code and starter assets.

## Reuse recommendation

If you want other educators to reuse this material with minimal ambiguity, add an explicit repository license if you have not already done so. A public site improves discoverability, but a license clarifies reuse expectations.

## Good site patterns for robotics courses

- Keep the homepage short and audience-aware.
- Separate quick-start tasks from deep technical references.
- Give each lab its own landing page.
- Keep setup, troubleshooting, and robot-specific notes in different pages so updates stay focused.

## Related pages

- [Quick Start](guides/quick_start.md)
- [Quick Reference](guides/quick_reference.md)
- [Lab 06](lab06_files/README.md)
- [Lab 07](lab07_files/README.md)
- [Setup Scripts](guides/setup_scripts.md)
