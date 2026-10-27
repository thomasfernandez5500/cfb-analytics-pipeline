"""
Thin wrapper around the CFBD API.

Free tier = 1,000 calls/month, so callers should batch by season/week rather
than looping per-game. See https://collegefootballdata.com/api-tiers for
current limits before scheduling frequent pulls.
"""
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.collegefootballdata.com"
API_KEY = os.environ.get("CFBD_API_KEY")


class CFBDClient:
    def __init__(self, api_key: str = None, max_retries: int = 3, backoff_sec: float = 2.0):
        self.api_key = api_key or API_KEY
        if not self.api_key:
            raise RuntimeError("CFBD_API_KEY is not set. Copy .env.example to .env and fill it in.")
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
        self.max_retries = max_retries
        self.backoff_sec = backoff_sec

    def get(self, path: str, params: dict = None) -> list | dict:
        url = f"{BASE_URL}{path}"
        for attempt in range(1, self.max_retries + 1):
            resp = self.session.get(url, params=params or {})
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 429:
                # Rate limited / monthly quota hit on the free tier.
                wait = self.backoff_sec * attempt
                time.sleep(wait)
                continue
            resp.raise_for_status()
        raise RuntimeError(f"Failed GET {path} after {self.max_retries} retries")

    # --- Convenience endpoints (add more as needed) ---
    def games(self, year: int, season_type: str = "regular", week: int = None) -> list:
        params = {"year": year, "seasonType": season_type}
        if week:
            params["week"] = week
        return self.get("/games", params)

    def team_game_stats(self, year: int, week: int = None) -> list:
        params = {"year": year}
        if week:
            params["week"] = week
        return self.get("/games/teams", params)

    def recruiting_rankings(self, year: int) -> list:
        return self.get("/recruiting/teams", {"year": year})

    def betting_lines(self, year: int, week: int = None) -> list:
        params = {"year": year}
        if week:
            params["week"] = week
        return self.get("/lines", params)

    def advanced_stats(self, year: int, team: str = None) -> list:
        params = {"year": year}
        if team:
            params["team"] = team
        return self.get("/stats/season/advanced", params)
