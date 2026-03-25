# MEMS Intro to Robotics Website

This repository hosts the public GitHub Pages site for the MEMS Intro to Robotics teaching materials.

The site is intended to support three audiences:

- students using the lab manuals and quick references
- course staff maintaining setup and support documentation
- outside educators looking for reusable robotics course infrastructure and lab materials

## Local preview

```bash
python -m pip install -r requirements-docs.txt
mkdocs serve
```

Then open `http://127.0.0.1:8000/`.

## Repository structure

- `docs/`: site pages and homepage layout
- `guides/`: source markdown for reusable guides
- `lab06_files/`: Lab 06 writeup
- `lab07_files/`: Lab 07 writeup
- `mkdocs.yml`: site navigation and theme config
- `.github/workflows/docs.yml`: GitHub Pages deployment workflow

## Publishing

This site is published with GitHub Pages using a custom GitHub Actions workflow.
