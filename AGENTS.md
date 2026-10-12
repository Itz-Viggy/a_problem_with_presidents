# Repository instructions

## Purpose

Complete the presidential lifespan analysis described in README.md. Keep the
solution small, readable, and easy to explain during a code walkthrough.

## Setup and files

- Use Python 3 and the standard library. No package installation is needed.
- Run `python3 analyze.py` from the repository to regenerate the results.
- `analyze.py` reads the supplied CSV and writes `presidents.csv` and `report.html`.
- Preserve the original CSV, license, and assignment instructions.
- Edit the script and regenerate the outputs instead of editing results by hand.

## Analysis rules

- Exclude the citation row at the end of the source CSV.
- Keep one observation per president, including Grover Cleveland.
- Add `year_of_birth`, `lived_years`, `lived_months`, and `lived_days`.
- Years and months are total completed calendar units. Days is the exact date
  difference, including leap days.
- Leave lifespan fields blank when the supplied death date is missing. Exclude
  these records from rankings, statistics, and the histogram. Do not look up or
  add newer death dates unless asked.
- Rank by exact days lived. Report the 10 longest and 10 shortest lifespans.
- Calculate the mean, frequency-weighted average, median, mode, maximum, minimum,
  and population standard deviation. Document the weighting and SD conventions.
- If no days value repeats, report that there is no mode.
- Keep the report title, author, date, four-sentence summary, tables, histogram,
  methods, and conclusions together in `report.html`.

## Style and verification

- Use descriptive names and straightforward functions and loops.
- Add comments for assumptions and date rules, rather than describing every line.
- Run `python3 analyze.py` after changes and check that there are 45 presidents,
  39 completed lifespans, and six missing death dates.
- Check that John F. Kennedy is shortest at 16,978 days and George Bush is longest
  at 34,504 days. The mean is 26,097.18 days, median 25,673 days, and population
  standard deviation 4,536.77 days.
- If the generated layout or plot changes, open the report in a browser to check it.
- Run `git diff --check` before committing.

## Git

- `origin` is the personal fork at `https://github.com/Itz-Viggy/a_problem_with_presidents.git`.
- `upstream` is the assignment repository at `https://github.com/senrabc/a_problem_with_presidents.git`.
- Keep changes local. Do not push or contact CTS-IT unless the user explicitly asks.
