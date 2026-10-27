"""
Pulls the supporting datasets used as model features: team-level box score
stats, recruiting rankings, betting lines, and advanced (EPA/PPA) stats.

TODO: add CLI args like pull_games.py once you've decided your backfill window.
Mind the 1,000 calls/month free-tier cap: a full multi-year backfill of all
four endpoints can burn through it fast -- backfill once, then only pull
incrementally during the season.
"""
import pandas as pd
import time

from cfbd_client import CFBDClient
from warehouse_loader import load_dataframe

BACKFILL_YEARS = range(2019, 2027)


def pull_team_game_stats():
    client = CFBDClient()
    rows = []
    for year in BACKFILL_YEARS:
        for week in range(1, 16):
            rows.extend(client.team_game_stats(year=year, week=week))
            time.sleep(1)
    load_dataframe(pd.DataFrame(rows), "raw_team_game_stats")


def pull_recruiting():
    client = CFBDClient()
    rows = []
    for year in BACKFILL_YEARS:
        rows.extend(client.recruiting_rankings(year=year))
    load_dataframe(pd.DataFrame(rows), "raw_recruiting_rankings")


def pull_betting_lines():
    client = CFBDClient()
    rows = []
    for year in BACKFILL_YEARS:
        rows.extend(client.betting_lines(year=year))
    load_dataframe(pd.DataFrame(rows), "raw_betting_lines")


def pull_advanced_stats():
    client = CFBDClient()
    rows = []
    for year in BACKFILL_YEARS:
        rows.extend(client.advanced_stats(year=year))
    load_dataframe(pd.DataFrame(rows), "raw_advanced_stats")


if __name__ == "__main__":
    pull_team_game_stats()
    pull_recruiting()
    pull_betting_lines()
    pull_advanced_stats()
