"""AI Radar's daily job. GitHub runs this every hour; it only acts when a digest is due.

  python run.py            normal run (does nothing until it's time)
  python run.py --check    list anything still to fill in
  python run.py --now      ignore the clock and run today's digest
  python run.py --test-scraper [harshmaur|clearpath]
                           fetch posts and print a health report (costs cents)
  python run.py --demo     build a sample dashboard from fake posts (free, no keys)
"""
import argparse
import json
import os
import sys
import traceback
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from radar import collect, curate, deliver, render, settings

ROOT = Path(__file__).parent
DASHBOARD_DAYS = 60
MAX_TRIES_PER_DAY = 3  # a broken scraper can still bill per post, so don't retry all day


def read_json(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def is_due(cfg, now, digest_exists):
    """Due once per period, on the first run after the chosen time.

    Checking hourly in local time handles the clock changes and GitHub's
    sometimes-late schedules, and catches up if an earlier run was missed.
    """
    if digest_exists:
        return False
    if cfg["frequency"] == "weekly" and now.weekday() != 0:
        return False
    hour, minute = map(int, str(cfg["delivery"]["time"]).split(":"))
    return (now.hour, now.minute) >= (hour, minute)


def new_candidates(posts, seen):
    return [p for p in posts if p["id"] not in seen]


def recent_titles(digest_dir, today, days=14):
    titles = []
    for path in sorted(digest_dir.glob("*.json"), reverse=True):
        if date.fromisoformat(path.stem) < today - timedelta(days=days):
            break
        titles += [p["title"] for p in read_json(path, {}).get("picks", [])]
    return titles


def prune_raw(raw_dir, today, keep_days):
    for path in raw_dir.glob("*.json"):
        if date.fromisoformat(path.stem) < today - timedelta(days=keep_days):
            path.unlink()


def remember(seen, picks, today, keep_days):
    """Add today's picks and forget anything older than keep_days."""
    updated = {**seen, **{p["id"]: today.isoformat() for p in picks}}
    cutoff = today - timedelta(days=keep_days)
    return {k: v for k, v in updated.items() if date.fromisoformat(v) >= cutoff}


def build_site(cfg, data_dir, site_dir):
    paths = sorted((data_dir / "digests").glob("*.json"), reverse=True)[:DASHBOARD_DAYS]
    digests = [read_json(p, {}) for p in paths]
    site_dir.mkdir(parents=True, exist_ok=True)
    (site_dir / "index.html").write_text(render.dashboard(digests, cfg["categories"]), encoding="utf-8")


def dashboard_url():
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if "/" not in repo:
        return ""
    owner, name = repo.split("/", 1)
    return f"https://{owner.lower()}.github.io/{name}/"


def run_digest(cfg, today, data_dir, site_dir):
    """Each step saves its result, so a retry never pays or emails twice."""
    raw_path = data_dir / "raw" / f"{today}.json"
    digest_path = data_dir / "digests" / f"{today}.json"
    seen_path = data_dir / "seen.json"

    digest = read_json(digest_path, None)
    if digest is None:
        if raw_path.exists():
            print("Reusing posts already fetched today.")
            posts = read_json(raw_path, [])
        else:
            posts = collect.fetch(cfg)
            for warning in collect.health_check(posts, cfg, cfg["scraper"]):
                print(f"Warning: {warning}")
            write_json(raw_path, posts)
        print(f"Collected {len(posts)} posts.")

        seen = read_json(seen_path, {})
        candidates = new_candidates(posts, seen)
        print(f"{len(candidates)} haven't been shown before.")
        picks, usage = [], None
        if candidates:
            titles = recent_titles(data_dir / "digests", today)
            picks, usage = curate.curate(cfg, candidates, titles)
            print(f"Picked {len(picks)}. AI usage: {usage}")
        digest = {"date": today.isoformat(), "picks": picks, "usage": usage, "delivered": False}
        write_json(digest_path, digest)
        write_json(seen_path, remember(seen, picks, today, cfg.get("remember_days", 30)))
        prune_raw(data_dir / "raw", today, cfg.get("keep_raw_days", 14))

    build_site(cfg, data_dir, site_dir)

    if not digest["delivered"]:
        deliver.digest(cfg, digest, dashboard_url())
        digest["delivered"] = True
        write_json(digest_path, digest)
        print(f"Delivered by: {cfg['delivery']['channel']}")


def demo(cfg):
    """A free preview using made-up posts. No keys or network needed."""
    posts = read_json(ROOT / "samples" / "demo_posts.json", [])
    today = datetime.now().date()
    digests = []
    for offset, chunk in enumerate((posts[:5], posts[5:])):
        picks = [
            {
                **{k: p[k] for k in ("id", "title", "url", "subreddit", "upvotes", "comments")},
                "category": cfg["categories"][i % len(cfg["categories"])],
                "what_it_is": p["what_it_is"],
                "why_its_good": p["why_its_good"],
                "why_useful_to_you": p["why_useful_to_you"],
                "caution": p.get("caution", False),
            }
            for i, p in enumerate(chunk)
        ]
        order = {c: i for i, c in enumerate(cfg["categories"])}
        picks.sort(key=lambda p: order[p["category"]])
        digests.append({"date": (today - timedelta(days=offset)).isoformat(), "picks": picks})
    out = ROOT / "preview"
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(render.dashboard(digests, cfg["categories"]), encoding="utf-8")
    (out / "email.html").write_text(render.email_html(digests[0], "https://example.com/"), encoding="utf-8")
    print(f"Sample dashboard: {out / 'index.html'}\nSample email: {out / 'email.html'}")


def test_scraper(cfg, name):
    if not os.environ.get("APIFY_TOKEN"):
        print("Add the APIFY_TOKEN secret first (see SETUP.md).")
        return 1
    cfg = {**cfg, "scraper": name or cfg["scraper"], "posts_per_subreddit": 10}
    print(f"Testing {cfg['scraper']} on: {', '.join(cfg['subreddits'])}")
    try:
        posts = collect.fetch(cfg)
        warnings = collect.health_check(posts, cfg, cfg["scraper"])
    except collect.CollectError as error:
        print(f"FAILED: {error}")
        return 1
    print(f"{len(posts)} posts")
    for p in posts:
        print(f"  r/{p['subreddit']:<14} {p['upvotes']:>6} up {p['comments']:>5} comments  {p['created']}  {p['title'][:60]}")
    for warning in warnings:
        print(f"Warning: {warning}")
    print("Check: are these from the last day, with real counts?")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--now", action="store_true")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--test-scraper", nargs="?", const="", default=None)
    args = parser.parse_args()

    cfg = settings.load(ROOT / "config.yaml")

    if args.demo:
        return demo(cfg)

    if args.check:
        found = settings.problems(cfg)
        if not cfg.get("enabled"):
            found.append("enabled: change to true when everything else is done.")
        print("\n".join(f"- {p}" for p in found) or "All set.")
        return 1 if found else 0

    if not cfg.get("enabled") and not args.now and args.test_scraper is None:
        print("Switched off (enabled: false in config.yaml). Nothing to do.")
        return 0

    if args.test_scraper is not None:
        return test_scraper(cfg, args.test_scraper)

    found = settings.problems(cfg)
    if found:
        print("Can't run yet:\n" + "\n".join(f"- {p}" for p in found))
        return 1

    now = datetime.now(ZoneInfo(cfg["delivery"]["timezone"]))
    data_dir = ROOT / "data"
    digest = read_json(data_dir / "digests" / f"{now.date()}.json", None)
    finished = digest is not None and digest["delivered"]
    # A digest that was written but not delivered still counts as due, so a retry sends it.
    if not args.now and not is_due(cfg, now, finished):
        print("Not due yet.")
        return 0

    status_path = data_dir / "status.json"
    status = read_json(status_path, {})
    failures = status.get("failures", 0) if status.get("date") == now.date().isoformat() else 0
    if failures >= MAX_TRIES_PER_DAY and not args.now:
        print(f"Already failed {failures} times today. Trying again tomorrow.")
        return 0

    try:
        run_digest(cfg, now.date(), data_dir, ROOT / "site")
        return 0
    except (collect.CollectError, curate.CurateError, deliver.DeliverError) as error:
        reason = str(error)
    except Exception as error:  # noqa: BLE001 - anything unexpected must still alert the owner
        traceback.print_exc()
        reason = f"Unexpected error: {type(error).__name__}. See the GitHub Actions log."

    print(f"FAILED: {reason}")
    failures += 1
    write_json(status_path, {"date": now.date().isoformat(), "failures": failures})
    if failures == 1:  # one alert a day is enough
        deliver.alert(cfg, f"{reason}\n\nIt will try up to {MAX_TRIES_PER_DAY - 1} more times today.")
    build_site(cfg, data_dir, ROOT / "site")  # the dashboard step needs a page even on a bad day
    return 1


if __name__ == "__main__":
    sys.exit(main())
