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
    """Read dates such as 'Feb 22, 1732' and 'July 4, 1826'."""
    month_name, day, year = text.replace(",", "").split()
    # The source mixes abbreviated and full month names.
    month_number = MONTHS.index(month_name[:3]) + 1
    return date(int(year), month_number, int(day))


def load_presidents():
    """Keep the original fields and add birth year and completed lifespan units."""
    presidents = []
    with SOURCE.open(newline="", encoding="utf-8-sig") as source:
        for row in csv.DictReader(source):
            # The last CSV row is a citation, not a president.
            if row["PRESIDENT"].startswith("Reference:"):
                continue

            birth_date = parse_date(row["BIRTH DATE"])
            row["year_of_birth"] = birth_date.year
            row["lived_years"] = None
            row["lived_months"] = None
            row["lived_days"] = None

            # A missing death date means the completed lifespan is unknown.
            if row["DEATH DATE"].strip():
                death_date = parse_date(row["DEATH DATE"])
                if death_date < birth_date:
                    raise ValueError(f"Death precedes birth: {row['PRESIDENT']}")

                row["lived_days"] = (death_date - birth_date).days

                # Subtract one year if the final birthday was not reached.
                years = death_date.year - birth_date.year
                birthday = (birth_date.month, birth_date.day)
                if (death_date.month, death_date.day) < birthday:
                    years -= 1
                row["lived_years"] = years

                # Months is a total, rather than the months left after years.
                months = (death_date.year - birth_date.year) * 12
                months += death_date.month - birth_date.month
                if death_date.day < birth_date.day:
                    months -= 1
                row["lived_months"] = months

            presidents.append(row)
    return presidents


def save_presidents(presidents):
    with (ROOT / "presidents.csv").open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(
            output, fieldnames=list(presidents[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(presidents)


def calculate_statistics(lived_days):
    """Summarize completed lifespans, with one observation per president."""
    frequencies = Counter(lived_days)

    # No separate weights are supplied, so use each lifespan's frequency.
    weighted_total = 0
    for days, frequency in frequencies.items():
        weighted_total += days * frequency
    weighted_average = weighted_total / len(lived_days)

    if max(frequencies.values()) == 1:
        mode = "None (every value occurs once)"
    else:
        modes = sorted(statistics.multimode(lived_days))
        mode = ", ".join(f"{days:,}" for days in modes)

    return {
        "Mean": statistics.mean(lived_days),
        "Weighted average (frequency weights)": weighted_average,
        "Median": statistics.median(lived_days),
        "Mode": mode,
        "Maximum": max(lived_days),
        "Minimum": min(lived_days),
        # Describe the whole set of recorded lifespans, using population SD.
        "Standard deviation (population)": statistics.pstdev(lived_days),
    }


def table(headers, rows, css_class=""):
    """Build an HTML table, escaping text from the source data."""
    heading_cells = []
    for heading in headers:
        heading_cells.append(f'<th scope="col">{escape(str(heading))}</th>')
    headings = "".join(heading_cells)

    body_rows = []
    for row in rows:
        cells = []
        for value in row:
            cells.append(f"<td>{escape(str(value))}</td>")
        body_rows.append("<tr>" + "".join(cells) + "</tr>")
    body = "".join(body_rows)

    return (f'<div class="table-wrap"><table class="{css_class}">'
            f"<thead><tr>{headings}</tr></thead><tbody>{body}</tbody></table></div>")


def ranking_table(presidents):
    headers = ["Rank", "President", "Birth year", "Years", "Months", "Days"]
    rows = []
    for rank, president in enumerate(presidents[:10], start=1):
        rows.append([
            rank,
            president["PRESIDENT"],
            president["year_of_birth"],
            president["lived_years"],
            president["lived_months"],
            f"{president['lived_days']:,}",
        ])
    return table(headers, rows, "ranking")


def histogram(days):
    """Draw a histogram as SVG so the report needs no plotting packages."""
    bin_width = 2500
    start = min(days) // bin_width * bin_width
    stop = (max(days) // bin_width + 1) * bin_width
    edges = list(range(start, stop + 1, bin_width))

    counts = []
    intervals = []
    for lower, upper in zip(edges, edges[1:]):
        count = 0
        for day in days:
            if lower <= day < upper:
                count += 1
        counts.append(count)
        intervals.append(f"{lower:,} to under {upper:,} days: {count}")

    # Leave space around the plot for axis labels and counts above the bars.
    y_axis_max = (max(counts) // 2 + 1) * 2
    plot_left, plot_top = 65, 35
    plot_width, plot_height = 710, 240
    bar_width = plot_width / len(counts)
    description = "; ".join(intervals)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 335" '
        'role="img" aria-labelledby="plot-title plot-description">',
        '<title id="plot-title">Distribution of presidential lifespans</title>',
        '<desc id="plot-description">Number of presidents in each lifespan interval: '
        f'{description}.</desc>',
    ]

    for tick in range(0, y_axis_max + 1, 2):
        y = plot_top + plot_height - tick / y_axis_max * plot_height
        parts.append(f'<path d="M{plot_left},{y}h{plot_width}" stroke="#ddd"/>')
        parts.append(f'<text x="{plot_left - 12}" y="{y + 4}" '
                     f'text-anchor="end">{tick}</text>')

    for index, count in enumerate(counts):
        x = plot_left + index * bar_width
        bar_height = count / y_axis_max * plot_height
        y = plot_top + plot_height - bar_height
        parts.append(f'<rect x="{x + 1}" y="{y}" width="{bar_width - 2}" '
                     f'height="{bar_height}" fill="#35648a"/>')
        parts.append(f'<text x="{x + bar_width / 2}" y="{y - 7}" '
                     f'text-anchor="middle">{count}</text>')
    for index, edge in enumerate(edges):
        x = plot_left + index * bar_width
        parts.append(f'<text x="{x}" y="{plot_top + plot_height + 22}" '
                     f'text-anchor="middle">{edge:,}</text>')
    parts.extend([
        '<text x="420" y="327" text-anchor="middle">Days lived</text>',
        '<text transform="translate(18 155) rotate(-90)" '
        'text-anchor="middle">Number of presidents</text>', "</svg>"])
    return "".join(parts)


def write_report(presidents, completed_presidents, summary):
    ordered = sorted(completed_presidents, key=lambda row: row["lived_days"])
    longest_first = list(reversed(ordered))
    days = [row["lived_days"] for row in completed_presidents]
    mean = summary["Mean"]
    median = summary["Median"]
    deviation = summary["Standard deviation (population)"]

    statistics_rows = []
    for measure, value in summary.items():
        if isinstance(value, str):
            formatted_value = value
        elif measure in ("Maximum", "Minimum"):
            formatted_value = f"{value:,}"
        else:
            formatted_value = f"{value:,.2f}"
        statistics_rows.append([measure, formatted_value])
    measures = table(["Measure", "Lived days"], statistics_rows)

    shortest, longest = ordered[0], ordered[-1]
    missing = len(presidents) - len(completed_presidents)
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
<p>The supplied dataset contains {len(presidents)} presidents, of whom {len(completed_presidents)} have recorded death dates.
Among those {len(completed_presidents)}, the mean lifespan is {mean:,.2f} days and the median is {median:,.0f} days.
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
squared deviations by {len(completed_presidents)}, describing all recorded completed lifespans in this dataset.
There is no mode because every observed lived-days value occurs once.</p>

<h2>10 longest recorded lifespans</h2>
{ranking_table(longest_first)}
<h2>10 shortest recorded lifespans</h2>
{ranking_table(ordered)}
<p class="byline">Years and months are separate totals of completed calendar units.
Days is the exact elapsed lifespan.</p>

<h2>Descriptive statistics</h2>
{measures}

<h2>Distribution of lived days</h2>
<figure>
{histogram(days)}
<figcaption>The histogram groups the {len(completed_presidents)} recorded lifespans into intervals of 2,500 days.
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


def main():
    presidents = load_presidents()
    save_presidents(presidents)

    completed_presidents = []
    for president in presidents:
        if president["lived_days"] is not None:
            completed_presidents.append(president)

    lived_days = [president["lived_days"] for president in completed_presidents]
    summary = calculate_statistics(lived_days)
    write_report(presidents, completed_presidents, summary)

    missing = len(presidents) - len(completed_presidents)
    print(f"Analyzed {len(completed_presidents)} completed lifespans; {missing} death dates missing.")
    print("Created presidents.csv and report.html.")


if __name__ == "__main__":
    main()
