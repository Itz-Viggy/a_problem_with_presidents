# Project guide

## Overview

This is a small Python project that analyzes a supplied snapshot of U.S.
presidential birth and death dates. README.md contains the assignment and usage
instructions. The generated report explains the methods and findings.

## Environment and commands

- Use Python 3.8 or newer. The project uses only the standard library.
- Run `python3 analyze.py` from the repository root to regenerate the outputs.
- File paths are resolved relative to the script, so it also runs from other directories.
- No package installation, credentials, or external services are needed.

## Repository layout

- `analyze.py`: CSV loading, date calculations, statistics, and report generation.
- `U.S. Presidents Birth and Death Information - Sheet1.csv`: original source data.
- `presidents.csv`: generated data with the calculated fields.
- `report.html`: self-contained report with tables and an inline SVG histogram.

## Coding and data conventions

- Keep the implementation small and prefer standard-library tools.
- Use descriptive names, focused functions, and straightforward control flow.
- Explain assumptions and non-obvious date rules in comments and the report.
- Preserve the original source data, license, and assignment text.
- Treat the supplied data as a historical snapshot. Keep missing values distinct
  from zero and do not replace them with newer information unless requested.
- Regenerate output files through the script rather than editing them by hand.

## Verification

There is no automated test suite or configured linter in this repository.
After changing analysis code, run `python3 analyze.py` and review the affected
calculations and generated files. Check the report in a browser when its layout
or plot changes. Run `git diff --check` before committing.

## Git workflow

`origin` points to the personal fork; `upstream` points to the original repository.
Keep commits focused. Keep changes local and do not push unless explicitly asked.
