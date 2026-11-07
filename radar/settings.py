"""Load config.yaml and explain, in plain English, anything that needs fixing."""
import os
import re
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import yaml

PLACEHOLDER = "FILL IN"
MODELS = ("claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5")
SCRAPERS = ("harshmaur", "clearpath")
CHANNELS = ("email", "slack", "both", "none")


# Scraper prices: US dollars per 1,000 posts, and per run. See OPTIONS.md.
SCRAPER_PRICES = {"harshmaur": (2.00, 0.02), "clearpath": (1.99, 0.0)}
FREE_APIFY_CREDIT = 5.00


class ConfigError(Exception):
    pass


def load(path="config.yaml"):
    try:
        cfg = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        mark = getattr(error, "problem_mark", None)
        where = f" near line {mark.line + 1}" if mark else ""
        raise ConfigError(
            f"config.yaml has a formatting problem{where}. Check the spacing at the start of "
            "that line and the one above, and that any text with a colon is in quotes."
        ) from None
    if not isinstance(cfg, dict):
        raise ConfigError("config.yaml looks empty or damaged. Copy it again from the template.")
    return cfg


def monthly_scraper_cost(cfg):
    """Estimated scraper cost per month in US dollars."""
    per_thousand, per_run = SCRAPER_PRICES[cfg["scraper"]]
    runs = 4.3 if cfg["frequency"] == "weekly" else 30
    posts = len(cfg["subreddits"]) * cfg["posts_per_subreddit"] * runs
    return posts * per_thousand / 1000 + runs * per_run


def required_secrets(cfg):
    secrets = ["APIFY_TOKEN", "ANTHROPIC_API_KEY"]
    channel = cfg.get("delivery", {}).get("channel")
    if channel in ("email", "both"):
        secrets += ["RESEND_API_KEY", "DIGEST_EMAIL"]
    if channel in ("slack", "both"):
        secrets += ["SLACK_WEBHOOK_URL"]
    return secrets


def problems(cfg, check_secrets=True):
    """Return a list of things to fix. An empty list means ready to run."""
    found = []
    if PLACEHOLDER in str(cfg.get("profile", "")) or not str(cfg.get("profile") or "").strip():
        found.append("profile: replace every FILL IN with a few words about you.")
    for name in ("posts_per_subreddit", "posts_to_show"):
        value = cfg.get(name)
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            found.append(f"{name}: must be a whole number of 1 or more.")
    if any(PLACEHOLDER in str(e) for e in cfg.get("examples_of_useful_posts") or []):
        found.append("examples_of_useful_posts: add real examples, or delete the FILL IN line.")
    if not cfg.get("subreddits"):
        found.append("subreddits: list at least one.")
    if not cfg.get("categories"):
        found.append("categories: list at least one.")
    if cfg.get("frequency") not in ("daily", "weekly"):
        found.append("frequency: must be daily or weekly.")
    if cfg.get("scraper") not in SCRAPERS:
        found.append(f"scraper: must be one of {', '.join(SCRAPERS)}.")
    if cfg.get("model") not in MODELS:
        found.append(f"model: must be one of {', '.join(MODELS)}.")
    delivery = cfg.get("delivery", {})
    if delivery.get("channel") not in CHANNELS:
        found.append(f"delivery channel: must be one of {', '.join(CHANNELS)}.")
    if not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", str(delivery.get("time"))):
        found.append('delivery time: use the 24-hour clock in quotes, like "07:30".')
    try:
        ZoneInfo(str(delivery.get("timezone")))
    except (ZoneInfoNotFoundError, ValueError):
        found.append("delivery timezone: use a name like Europe/London.")
    if check_secrets:
        for name in required_secrets(cfg):
            if not os.environ.get(name):
                found.append(f"Missing secret {name}: add it in GitHub Secrets (see SETUP.md).")
    return found
