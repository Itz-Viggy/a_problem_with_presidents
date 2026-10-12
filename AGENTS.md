# Repository rules

- Keep runtime dependencies limited to Python's standard library.
- Preserve the original source CSV, license, and assignment text.
- Keep missing data distinct from zero; do not fill gaps with guessed values.
- Regenerate `presidents.csv` and `report.html` with `python3 analyze.py`;
  do not edit generated results by hand.
- After analysis changes, review the affected calculations and outputs.
- Inspect the report in a browser when its layout or plot changes.
- Run `git diff --check` before committing.
- Do not push unless explicitly requested.
