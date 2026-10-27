"""
Backfill or incrementally pull game-level data from CFBD and load it to the
warehouse's raw layer. dbt staging models read from these raw tables.

Usage:
    python ingestion/pull_games.py --start-year 2015 --end-year 2025
    python ingestion/pull_games.py --year 2026 --week 9   # in-season incremental pull
"""
import argparse
import pandas as pd

from cfbd_client import CFBDClient
from warehouse_loader import load_dataframe


def pull_games_range(start_year: int, end_year: int) -> pd.DataFrame:
    client = CFBDClient()
    all_rows = []
    for year in range(start_year, end_year + 1):
        print(f"[pull_games] Fetching {year}...")
        rows = client.games(year=year)
        all_rows.extend(rows)
    return pd.DataFrame(all_rows)


def pull_single_week(year: int, week: int) -> pd.DataFrame:
    client = CFBDClient()
    rows = client.games(year=year, week=week)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-year", type=int)
    parser.add_argument("--end-year", type=int)
    parser.add_argument("--year", type=int)
    parser.add_argument("--week", type=int)
    args = parser.parse_args()

    if args.year and args.week:
        df = pull_single_week(args.year, args.week)
        load_dataframe(df, "raw_games", if_exists="append")
    elif args.start_year:
        end_year = args.end_year or args.start_year
        df = pull_games_range(args.start_year, end_year)
        load_dataframe(df, "raw_games", if_exists="replace")
    else:
        parser.error("Provide either --start-year (backfill) or --year/--week (incremental).")
