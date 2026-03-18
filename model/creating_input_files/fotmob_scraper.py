# fotmob_scraper.py
import json
import os
import time
from pathlib import Path
import requests
from playwright.sync_api import sync_playwright

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

MATCH_URL = "https://www.fotmob.com/match/{}"
API_URL = "https://www.fotmob.com/api/matchDetails?matchId={}"

def get_cached_match(match_id):
    cache_file = CACHE_DIR / f"match_{match_id}.json"
    if cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_cache(match_id, data):
    cache_file = CACHE_DIR / f"match_{match_id}.json"
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_match_stats(match_id, force_refresh=False):
    """
    Fetch match stats from FotMob using a real browser session.
    Automatically solves Cloudflare Turnstile.
    """

    # Check cache
    if not force_refresh:
        cached = get_cached_match(match_id)
        if cached:
            return cached

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        page = context.new_page()
        page.goto(MATCH_URL.format(match_id))

        # Wait for the page to fully load + Cloudflare to verify
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # small buffer for Turnstile completion

        # Extract cookies
        cookies = context.cookies()

        # Build a requests session with those cookies
        session = requests.Session()
        for c in cookies:
            session.cookies.set(c["name"], c["value"])

        # Hit the API endpoint
        response = session.get(API_URL.format(match_id))
        response.raise_for_status()
        data = response.json()

        browser.close()

    # Save to cache
    save_cache(match_id, data)
    return data