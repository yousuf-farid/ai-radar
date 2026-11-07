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


def load(path="config.yaml"):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


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
    if PLACEHOLDER in str(cfg.get("profile", "")):
        found.append("profile: replace every FILL IN with a few words about you.")
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
