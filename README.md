# ff-projection-analysis

An analysis of how ESPN's 2025 preseason fantasy football projections compare to actual end-of-season points, broken down by position. Work in progress.

**For reviewers:** Python · pandas · matplotlib · solo

## Problem

Preseason projections drive most fantasy drafts, but they often miss badly. Before testing which draft strategies hold up, I want to know how far off the projections are and whether that error differs by position (QB, RB, WR, TE). The target setting is a PPR, 10-team league with no trades or lineup changes.

## Approach

- **Data:** ESPN preseason ranks and projected 2025 points (`unfiltered_data/ESPN_proj_pts.csv`, with 2024 points for reference) and end-of-season 2025 ranks and points (`unfiltered_data/end_of_season_points.csv`), saved as CSVs so the analysis doesn't depend on scraping.
- **Join:** `Scripts/merge_csv.py` strips whitespace from names, outer-joins on player name, and keeps only players with both a preseason and a postseason rank. That leaves 142 skill-position players in `Scripts/master_df.csv`.
- **Error metric:** `Scripts/stdev_by_position.py` computes relative error, `(actual − projected) / projected`, so a 300-point QB and a 150-point TE are on the same scale, and plots one histogram per position.
- **Tradeoff:** exact name matching is simple but lossy. Kickers, defenses, and name variants (ESPN's "James Cook" vs. "James Cook III" in the season totals) drop out of the join.
- **Next:** finish the per-position error stats, then simulate drafts to test strategies like reaching past ADP or prioritizing one position early. The full roadmap is in [NOTES.md](NOTES.md).

## How to run

**Prerequisites:** Python 3.9+ and a terminal. Everything runs locally from the checked-in CSVs; no API keys or network access are needed for the analysis.

**1. Clone and install**

```bash
git clone https://github.com/ZishaanM/ff-projection-analysis.git
cd ff-projection-analysis
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**2. Rebuild the joined table**

The scripts use paths relative to `Scripts/`, so run them from that folder.

```bash
cd Scripts
python merge_csv.py
```

This reads the two CSVs in `../unfiltered_data/`, writes `master_df.csv`, and prints the first five rows.

**3. Plot relative error by position**

```bash
python stdev_by_position.py
```

A 2×2 window opens with histograms for WR, RB, QB, and TE, each with a black line at 0 marking a perfect projection. Bars left of the line are players who scored below their projection.

**Verify:** the rebuilt table should have 142 rows and 8 columns, matching the committed file.

```bash
python -c "import pandas as pd; print(pd.read_csv('master_df.csv').shape)"   # (142, 8)
git status --short master_df.csv                                            # no output = identical
```

**Gotchas**

- **No display (SSH, containers):** `plt.show()` needs a GUI. Run `MPLBACKEND=Agg python stdev_by_position.py` to run headless; matplotlib warns that it can't show the figure, and nothing is saved.
- **Error stats aren't done yet:** `calculateErrorStats` in `stdev_by_position.py` is an unfinished stub and is never called, so the script prints a placeholder line instead of RMSE.
- **Histogram counts are inflated:** `getPositionalError` adds the whole position column once per player, so each value appears *n* times. The shape of each histogram is right, but the y-axis counts aren't.

**Optional: archived scrapers**

`unfiltered_data/Archive/` holds the scrapers used to collect data. You don't need them to reproduce the analysis. They need Google Chrome and extra packages:

```bash
pip install -r requirements-scrapers.txt
```

- `Scrape_fantasy_pros.py` reads `fantasy_pros_data.csv`, splits FantasyPros' `"Player Team (Bye)"` column into separate columns, and overwrites `fantasy_pros_data3.csv`. Run it from its own folder: `cd unfiltered_data/Archive && python Scrape_fantasy_pros.py`.
- The `ESPN_*.py` scripts target an ESPN league projections page and need `ESPN_LEAGUE_ID` set. `ESPN_debug_scraper.py` also reads `ESPN_USERNAME` and `ESPN_PASSWORD` and prompts for them if they're unset. Copy `.env.example` to `.env`, fill it in, and load it with `set -a; source .env; set +a`. These are exploratory: `ESPN_projection_scrape_v2.py` offers an API probe or a manual browser login, and private leagues require logging in.

## What's interesting in the code

- `Scripts/merge_csv.py`: a short script whose join and `dropna` define the dataset. Its outer join plus rank filter is where 161 projected players and 600 season finishers become 142 matched players, and where kickers, defenses, and name mismatches fall out.
- `unfiltered_data/Archive/Scrape_fantasy_pros.py`: `split_player_team_bye` parses strings like `"Christian McCaffrey SF (9)"` by splitting from the right, which keeps multi-word names like "Amon-Ra St. Brown" intact.

## Stack

Python · pandas · NumPy · matplotlib · CSV data · (scrapers) Selenium, webdriver-manager, requests
