import csv
import statistics
from collections import Counter
from datetime import date
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "U.S. Presidents Birth and Death Information - Sheet1.csv"
AUTHOR = "Vignesh Sundararajan"
REPORT_DATE = date(2026, 10, 9)
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def parse_date(text):
    month, day, year = text.replace(",", "").split()
    return date(int(year), MONTHS.index(month[:3]) + 1, int(day))


def load_presidents():
    presidents = []
    with SOURCE.open(newline="", encoding="utf-8-sig") as source:
        for row in csv.DictReader(source):
            if row["PRESIDENT"].startswith("Reference:"):
                continue
            birth = parse_date(row["BIRTH DATE"])
            row.update(year_of_birth=birth.year, lived_years=None,
                       lived_months=None, lived_days=None)
            if row["DEATH DATE"].strip():
                death = parse_date(row["DEATH DATE"])
                if death < birth:
                    raise ValueError(f"Death precedes birth: {row['PRESIDENT']}")
                row["lived_days"] = (death - birth).days
                row["lived_years"] = death.year - birth.year - (
                    (death.month, death.day) < (birth.month, birth.day))
                row["lived_months"] = (
                    (death.year - birth.year) * 12 + death.month - birth.month
                    - (death.day < birth.day))
            presidents.append(row)
    return presidents


def table(headers, rows, css_class=""):
    headings = "".join(f'<th scope="col">{escape(str(h))}</th>' for h in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{escape(str(v))}</td>" for v in row) + "</tr>"
        for row in rows)
    return (f'<div class="table-wrap"><table class="{css_class}">'
            f"<thead><tr>{headings}</tr></thead><tbody>{body}</tbody></table></div>")


def ranking_table(presidents):
    return table(
        ["Rank", "President", "Birth year", "Years", "Months", "Days"],
        [(rank, row["PRESIDENT"], row["year_of_birth"], row["lived_years"],
          row["lived_months"], f"{row['lived_days']:,}")
         for rank, row in enumerate(presidents[:10], 1)], "ranking")


def histogram(days):
    bin_width = 2500
    start = min(days) // bin_width * bin_width
    stop = (max(days) // bin_width + 1) * bin_width
    edges = list(range(start, stop + 1, bin_width))
    counts = [sum(low <= day < high for day in days)
              for low, high in zip(edges, edges[1:])]
    ceiling = (max(counts) // 2 + 1) * 2
    left, top, width, height = 65, 35, 710, 240
    bar_width = width / len(counts)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 335" '
        'role="img" aria-labelledby="plot-title plot-description">',
        '<title id="plot-title">Distribution of presidential lifespans</title>',
        '<desc id="plot-description">Number of presidents in each lifespan interval: '
        + "; ".join(f"{low:,} to under {high:,} days: {count}"
                    for low, high, count in zip(edges, edges[1:], counts)) + ".</desc>"]
    for tick in range(0, ceiling + 1, 2):
        y = top + height - tick / ceiling * height
        parts.append(f'<path d="M{left},{y}h{width}" stroke="#ddd"/>')
        parts.append(f'<text x="{left - 12}" y="{y + 4}" text-anchor="end">{tick}</text>')
    for i, count in enumerate(counts):
        x = left + i * bar_width
        bar_height = count / ceiling * height
        y = top + height - bar_height
        parts.append(f'<rect x="{x + 1}" y="{y}" width="{bar_width - 2}" '
                     f'height="{bar_height}" fill="#35648a"/>')
        parts.append(f'<text x="{x + bar_width / 2}" y="{y - 7}" '
                     f'text-anchor="middle">{count}</text>')
    for i, edge in enumerate(edges):
        parts.append(f'<text x="{left + i * bar_width}" y="{top + height + 22}" '
                     f'text-anchor="middle">{edge:,}</text>')
    parts.extend([
        '<text x="420" y="327" text-anchor="middle">Days lived</text>',
        '<text transform="translate(18 155) rotate(-90)" '
        'text-anchor="middle">Number of presidents</text>', "</svg>"])
    return "".join(parts)


def main():
    presidents = load_presidents()
    with (ROOT / "presidents.csv").open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=list(presidents[0]),
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(presidents)

    deceased = [row for row in presidents if row["lived_days"] is not None]
    ordered = sorted(deceased, key=lambda row: row["lived_days"])
    days = [row["lived_days"] for row in deceased]
    frequencies = Counter(days)
    mean = statistics.mean(days)
    weighted_average = sum(value * count for value, count in frequencies.items()) / sum(
        frequencies.values())
    modes = statistics.multimode(days)
    mode = ("None (every value occurs once)" if max(frequencies.values()) == 1
            else ", ".join(f"{value:,}" for value in sorted(modes)))
    median = statistics.median(days)
    deviation = statistics.pstdev(days)
    measures = table(["Measure", "Lived days"], [
        ("Mean", f"{mean:,.2f}"),
        ("Weighted average (frequency weights)", f"{weighted_average:,.2f}"),
        ("Median", f"{median:,.2f}"),
        ("Mode", mode),
        ("Maximum", f"{max(days):,}"),
        ("Minimum", f"{min(days):,}"),
        ("Standard deviation (population)", f"{deviation:,.2f}"),
    ])
    shortest, longest = ordered[0], ordered[-1]
    missing = len(presidents) - len(deceased)
    report = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>U.S. Presidential Lifespans</title>
<style>
body {{ max-width: 850px; margin: 40px auto; padding: 0 24px;
        color: #222; font: 16px/1.6 Georgia, serif; }}
h1, h2, th {{ font-family: Arial, sans-serif; }}
h1 {{ font-size: 30px; line-height: 1.2; margin-bottom: 8px; }}
h2 {{ font-size: 21px; margin-top: 30px; }}
.byline, figcaption {{ color: #555; font-size: 14px; }}
.table-wrap {{ overflow-x: auto; }}
table {{ width: 100%; border-collapse: collapse; font: 14px/1.5 Arial, sans-serif; }}
th, td {{ padding: 9px 10px; border-bottom: 1px solid #ddd; text-align: right; }}
th {{ background: #eef2f5; }}
th:first-child, td:first-child, .ranking th:nth-child(2),
.ranking td:nth-child(2) {{ text-align: left; }}
.ranking td:nth-child(2) {{ white-space: nowrap; }}
figure {{ margin: 20px 0; }}
svg {{ display: block; width: 100%; height: auto; font: 13px Arial, sans-serif; }}
@media print {{ body {{ margin: 0; }} table, figure {{ break-inside: avoid; }}
                 h2 {{ break-after: avoid; }} }}
</style>
</head>
<body>
<h1>U.S. Presidential Lifespans</h1>
<p class="byline">{escape(AUTHOR)}<br>{REPORT_DATE.strftime('%B %d, %Y')}</p>
<p>The supplied dataset contains {len(presidents)} presidents, of whom {len(deceased)} have recorded death dates.
Among those {len(deceased)}, the mean lifespan is {mean:,.2f} days and the median is {median:,.0f} days.
{escape(longest['PRESIDENT'])} has the longest recorded lifespan at {longest['lived_days']:,} days,
and {escape(shortest['PRESIDENT'])} has the shortest at {shortest['lived_days']:,} days.
The {missing} records without death dates are excluded from lifespan comparisons.</p>

<h2>Methods and assumptions</h2>
<p>This analysis uses the supplied CSV as a historical snapshot, with no updated death dates.
The reference row at the end is excluded. Each president appears once, including Grover Cleveland.
Birth year is extracted from the birth date. Lived years and lived months are total completed
calendar years and months, respectively. Lived days is the exact difference between death and
birth dates, including leap days. Missing death dates leave all three lifespan fields blank
in the accompanying presidents.csv. These blanks are excluded from the tables and plot.</p>
<p>Rankings use exact lived days. The weighted average uses each distinct lifespan's frequency
as its weight: sum(days &times; frequency) / sum(frequency). This equals the mean because each
president contributes one observation. The population standard deviation divides the sum of
squared deviations by {len(deceased)}, describing all recorded completed lifespans in this dataset.
There is no mode because every observed lived-days value occurs once.</p>

<h2>10 longest recorded lifespans</h2>
{ranking_table(list(reversed(ordered)))}
<h2>10 shortest recorded lifespans</h2>
{ranking_table(ordered)}
<p class="byline">Years and months are separate totals of completed calendar units.
Days is the exact elapsed lifespan.</p>

<h2>Descriptive statistics</h2>
{measures}

<h2>Distribution of lived days</h2>
<figure>
{histogram(days)}
<figcaption>The histogram groups the {len(deceased)} recorded lifespans into intervals of 2,500 days.
Each interval includes its lower boundary and excludes its upper boundary.
This shows where lifespans cluster and how widely they vary.</figcaption>
</figure>

<h2>Conclusions</h2>
<p>The recorded lifespans range from {min(days):,} to {max(days):,} days,
a difference of {max(days) - min(days):,} days. The mean and median are close,
with a population standard deviation of {deviation:,.2f} days indicating substantial variation.
These results describe presidents with death dates in the supplied historical dataset.
They do not estimate the eventual lifespans of presidents whose death dates are missing.</p>
<p class="byline">Source: U.S. Presidents Birth and Death Information - Sheet1.csv,
supplied with the repository. Its reference credits
<a href="https://www.presidentsusa.net/birth.html">PresidentsUSA.Net</a>,
retrieved September 28, 2021.</p>
</body>
</html>
"""
    (ROOT / "report.html").write_text(report, encoding="utf-8")
    print(f"Analyzed {len(deceased)} completed lifespans; {missing} death dates missing.")
    print("Created presidents.csv and report.html.")


if __name__ == "__main__":
    main()
