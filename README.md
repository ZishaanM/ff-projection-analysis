# ff-projection-analysis

A small personal project comparing ESPN's 2025 preseason fantasy football projections to how players actually scored, by position. Still a work in progress.

**For reviewers:** Python · pandas · matplotlib · solo

## Problem

I wanted to see how far off ESPN's preseason projections were and whether some positions (QB, RB, WR, TE) are harder to project than others. Eventually I'd like to use that to test a few draft strategies in a simple PPR, 10-team league.

## Approach

- **Data:** two CSVs in `unfiltered_data/`. `ESPN_proj_pts.csv` has preseason ranks, projected 2025 points, and 2024 points. `end_of_season_points.csv` has final 2025 ranks and points.
- **Join:** `Scripts/merge_csv.py` matches players by name and keeps only those who appear in both files. That gives 142 players in `Scripts/master_df.csv`.
- **Error:** `Scripts/stdev_by_position.py` calculates `(actual − projected) / projected` for each player, so positions with different point totals can be compared, and plots a histogram for each position.
- **Tradeoff:** matching on exact names is simple but misses some players. Kickers, defenses, and name variants (for example "James Cook" vs. "James Cook III") get dropped.
- **Next:** finish the per-position error stats, then try simulating drafts. My rough plan is in [NOTES.md](NOTES.md).

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

`unfiltered_data/Archive/` has my earlier attempts at collecting the data. They're rough and not needed to run the analysis. They need Google Chrome and a few extra packages:

```bash
pip install -r requirements-scrapers.txt
```

- `Scrape_fantasy_pros.py` reads `fantasy_pros_data.csv`, splits FantasyPros' `"Player Team (Bye)"` column into separate columns, and overwrites `fantasy_pros_data3.csv`. Run it from its own folder: `cd unfiltered_data/Archive && python Scrape_fantasy_pros.py`.
- The `ESPN_*.py` scripts target an ESPN league projections page and need `ESPN_LEAGUE_ID` set. `ESPN_debug_scraper.py` also reads `ESPN_USERNAME` and `ESPN_PASSWORD` and prompts for them if they're unset. Copy `.env.example` to `.env`, fill it in, and load it with `set -a; source .env; set +a`. `ESPN_projection_scrape_v2.py` asks whether to try ESPN's API or log in manually in a browser. Private leagues need a login.

## What's interesting in the code

- `Scripts/merge_csv.py`: a short script, but it decides who's in the dataset. The join and `dropna` turn 161 projected players and 600 end-of-season players into 142 matches, and it's where kickers, defenses, and mismatched names get dropped.
- `unfiltered_data/Archive/Scrape_fantasy_pros.py`: `split_player_team_bye` splits strings like `"Christian McCaffrey SF (9)"` from the right, so names with spaces like "Amon-Ra St. Brown" stay together.

## Stack

Python · pandas · NumPy · matplotlib · CSV data · (scrapers) Selenium, webdriver-manager, requests
