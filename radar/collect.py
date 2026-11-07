"""Step 1: fetch top posts. This is the only file that knows about scrapers.

To add a scraper, write a build_input and a normalise function, add them to
SCRAPERS, and nothing else in the project has to change.
"""
import os
from datetime import datetime, timezone

import requests

APIFY_URL = "https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items"


class CollectError(Exception):
    pass


def _harshmaur_input(cfg, window):
    return {
        "startUrls": [
            {"url": f"https://www.reddit.com/r/{name}/top/?t={window}"}
            for name in cfg["subreddits"]
        ],
        "crawlCommentsPerPost": False,
        "maxPostsCount": cfg["posts_per_subreddit"],
    }


def _harshmaur_post(row):
    if row.get("dataType", "post") != "post":
        return None
    return {
        "id": row.get("parsedId") or row.get("id"),
        "title": row.get("title"),
        "body": row.get("body") or "",
        "url": row.get("postUrl") or row.get("url"),
        "subreddit": row.get("subredditName") or str(row.get("communityName", "")).removeprefix("r/"),
        "upvotes": row.get("upVotes", row.get("score")),
        "comments": row.get("commentsCount"),
        "created": row.get("createdAt"),
    }


def _clearpath_input(cfg, window):
    return {
        "subreddits": cfg["subreddits"],
        "sort": "top",
        "timeFilter": window,
        "maxPostsPerSubreddit": cfg["posts_per_subreddit"],
        "includeComments": False,
    }


def _clearpath_post(row):
    if row.get("_type", "post") != "post":
        return None  # status rows, e.g. a banned or empty subreddit
    created = row.get("created_utc")
    permalink = row.get("permalink") or ""
    return {
        "id": row.get("id") or row.get("_post_id"),
        "title": row.get("title"),
        "body": row.get("selftext") or "",
        "url": f"https://www.reddit.com{permalink}" if permalink.startswith("/") else (permalink or row.get("url")),
        "subreddit": row.get("_subreddit") or row.get("subreddit"),
        "upvotes": row.get("score"),
        "comments": row.get("num_comments"),
        "created": datetime.fromtimestamp(created, timezone.utc).isoformat() if created else None,
    }


SCRAPERS = {
    "harshmaur": ("harshmaur~reddit-scraper", _harshmaur_input, _harshmaur_post),
    "clearpath": ("clearpath~reddit-subreddit-posts-scraper", _clearpath_input, _clearpath_post),
}


def normalise(rows, scraper):
    """Turn a scraper's rows into our standard post shape, dropping unusable ones."""
    convert = SCRAPERS[scraper][2]
    posts, seen = [], set()
    for row in rows:
        post = convert(row)
        if post and post["id"] and post["title"] and post["url"] and post["id"] not in seen:
            seen.add(post["id"])
            post["upvotes"] = post["upvotes"] or 0
            post["comments"] = post["comments"] or 0
            posts.append(post)
    return posts


def health_check(posts, cfg, scraper):
    """Fail loudly rather than quietly sending a bad digest.

    Returns warnings. Raises CollectError if the data can't be trusted.
    """
    if not posts:
        raise CollectError(
            f"The {scraper} scraper returned no usable posts. It may be broken, or "
            "the Apify credit may have run out for this month."
        )
    if not any(p["upvotes"] for p in posts):
        raise CollectError(
            f"Every post from {scraper} has 0 upvotes, so its counts can't be trusted "
            "(often a sign it has switched to reading RSS feeds)."
        )
    found = {str(p["subreddit"]).lower() for p in posts}
    return [
        f"No posts came back from r/{name}."
        for name in cfg["subreddits"]
        if name.lower() not in found
    ]


def fetch(cfg):
    """Run the scraper once. One run covers every subreddit, which keeps run fees low."""
    scraper = cfg["scraper"]
    actor, build_input, _ = SCRAPERS[scraper]
    window = "week" if cfg["frequency"] == "weekly" else "day"
    try:
        response = requests.post(
            APIFY_URL.format(actor=actor),
            headers={"Authorization": f"Bearer {os.environ['APIFY_TOKEN']}"},
            json=build_input(cfg, window),
            timeout=320,
        )
    except requests.RequestException as error:
        raise CollectError(f"Could not reach Apify: {type(error).__name__}") from None
    if response.status_code >= 400:
        hint = {401: "the APIFY_TOKEN looks wrong", 402: "the Apify credit may have run out"}.get(
            response.status_code, "see the Apify console for details"
        )
        raise CollectError(f"Apify returned error {response.status_code}: {hint}.")
    return normalise(response.json(), scraper)
