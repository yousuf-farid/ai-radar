"""Run with: python -m pytest. No keys or network needed."""
import copy
import json
from datetime import date, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest
import requests
import yaml

import run
from radar import collect, curate, deliver, render, settings

ROOT = Path(__file__).parent.parent


@pytest.fixture
def cfg():
    config = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))
    config["profile"] = "I run a small business and use Claude daily."
    config["examples_of_useful_posts"] = []
    config["enabled"] = True
    return config


HARSHMAUR_ROW = {
    "dataType": "post", "id": "t3_abc", "parsedId": "abc", "title": "Hello",
    "body": "Text", "postUrl": "https://www.reddit.com/r/ClaudeAI/comments/abc/",
    "subredditName": "ClaudeAI", "createdAt": "2026-11-07T10:00:00.000Z",
    "upVotes": 50, "score": 50, "commentsCount": 7,
}
CLEARPATH_ROW = {
    "_type": "post", "_subreddit": "ClaudeAI", "id": "abc", "title": "Hello",
    "selftext": "Text", "permalink": "/r/ClaudeAI/comments/abc/", "score": 50,
    "num_comments": 7, "created_utc": 1794045600,
}


def post(id="abc", upvotes=50, subreddit="ClaudeAI"):
    return {"id": id, "title": f"Title {id}", "body": "Body", "url": f"https://www.reddit.com/{id}",
            "subreddit": subreddit, "upvotes": upvotes, "comments": 3, "created": None}


def raw_pick(id="abc", category="AI news and updates"):
    return {"post_id": id, "category": category, "what_it_is": "w", "why_its_good": "g",
            "why_useful_to_you": "u", "asks_you_to_install_or_run_something": False}


# ── Settings ────────────────────────────────────────────────

def test_shipped_template_lists_what_to_fill_in():
    template = settings.load(ROOT / "config.yaml")
    found = " ".join(settings.problems(template, check_secrets=False))
    assert "profile" in found and "examples_of_useful_posts" in found
    assert template["enabled"] is False


def test_filled_in_config_passes(cfg):
    assert settings.problems(cfg, check_secrets=False) == []


def test_bad_time_and_timezone_are_reported(cfg):
    cfg["delivery"]["time"] = 450  # what YAML can make of an unquoted 07:30
    cfg["delivery"]["timezone"] = "London"
    found = " ".join(settings.problems(cfg, check_secrets=False))
    assert "delivery time" in found and "timezone" in found


def test_missing_secret_is_reported(cfg, monkeypatch):
    for name in ("APIFY_TOKEN", "ANTHROPIC_API_KEY", "RESEND_API_KEY", "DIGEST_EMAIL"):
        monkeypatch.delenv(name, raising=False)
    assert any("DIGEST_EMAIL" in p for p in settings.problems(cfg))


# ── Collecting ──────────────────────────────────────────────

@pytest.mark.parametrize("scraper,row", [("harshmaur", HARSHMAUR_ROW), ("clearpath", CLEARPATH_ROW)])
def test_both_scrapers_give_the_same_shape(scraper, row):
    [result] = collect.normalise([row], scraper)
    assert result["id"] == "abc"
    assert result["upvotes"] == 50 and result["comments"] == 7
    assert result["subreddit"] == "ClaudeAI"
    assert result["url"] == "https://www.reddit.com/r/ClaudeAI/comments/abc/"
    assert result["body"] == "Text"


def test_non_post_rows_and_duplicates_are_dropped():
    status_row = {"_type": "subreddit", "_status": "banned"}
    assert collect.normalise([status_row, CLEARPATH_ROW, CLEARPATH_ROW], "clearpath") == \
        collect.normalise([CLEARPATH_ROW], "clearpath")
    assert len(collect.normalise([{"dataType": "comment", "id": "x", "title": "t"}], "harshmaur")) == 0


def test_scraper_inputs_use_one_run_for_all_subreddits(cfg):
    harsh = collect._harshmaur_input(cfg, "day")
    assert [u["url"] for u in harsh["startUrls"]] == [
        "https://www.reddit.com/r/ClaudeAI/top/?t=day",
        "https://www.reddit.com/r/ClaudeCode/top/?t=day",
    ]
    assert harsh["crawlCommentsPerPost"] is False
    clear = collect._clearpath_input(cfg, "day")
    assert clear["timeFilter"] == "day" and clear["subreddits"] == cfg["subreddits"]


def test_health_check_fails_on_nothing_or_fake_counts(cfg):
    with pytest.raises(collect.CollectError, match="no usable posts"):
        collect.health_check([], cfg, "harshmaur")
    with pytest.raises(collect.CollectError, match="0 upvotes"):
        collect.health_check([post(upvotes=0)], cfg, "harshmaur")


def test_health_check_warns_about_a_missing_subreddit(cfg):
    assert collect.health_check([post()], cfg, "harshmaur") == ["No posts came back from r/ClaudeCode."]


def test_fetch_keeps_token_out_of_the_url_and_explains_errors(cfg, monkeypatch):
    calls = {}

    def fake_post(url, headers, json, timeout):
        calls.update(url=url, headers=headers)
        return SimpleNamespace(status_code=402, json=lambda: [])

    monkeypatch.setenv("APIFY_TOKEN", "secret-token")
    monkeypatch.setattr(requests, "post", fake_post)
    with pytest.raises(collect.CollectError, match="credit") as error:
        collect.fetch(cfg)
    assert "secret-token" not in calls["url"] and "secret-token" not in str(error.value)
    assert calls["headers"]["Authorization"] == "Bearer secret-token"


# ── Curating ────────────────────────────────────────────────

def test_links_come_from_scraper_and_invented_ids_are_dropped(cfg):
    picks = curate.clean_picks(
        [raw_pick("abc"), raw_pick("invented"), raw_pick("abc")], [post("abc")], cfg
    )
    assert [p["id"] for p in picks] == ["abc"]
    assert picks[0]["url"] == "https://www.reddit.com/abc"


def test_picks_follow_category_order_and_limit(cfg):
    cfg["posts_to_show"] = 2
    candidates = [post("a"), post("b"), post("c")]
    picks = curate.clean_picks(
        [raw_pick("a", "AI news and updates"), raw_pick("b", "Mindset and ways of working"),
         raw_pick("c", "Tools, skills and resources")],
        candidates, cfg,
    )
    assert [p["id"] for p in picks] == ["c", "a"]


def test_prompt_cuts_long_posts_and_marks_data(cfg):
    cfg["max_post_chars"] = 10
    long_post = {**post(), "body": "x" * 50}
    prompt = curate.build_prompt(cfg, [long_post], ["Old title"])
    assert "x" * 10 in prompt and "x" * 11 not in prompt
    assert "<posts>" in prompt and "Old title" in prompt


def test_fallback_only_on_models_that_support_it(cfg):
    assert curate._request_args(cfg, [post()], [])["fallbacks"] == "default"
    cfg["model"] = "claude-haiku-5-5"
    assert "fallbacks" not in curate._request_args(cfg, [post()], [])


def fake_client(monkeypatch, response):
    create = lambda **kwargs: response
    client = SimpleNamespace(messages=SimpleNamespace(create=create),
                             beta=SimpleNamespace(messages=SimpleNamespace(create=create)))
    monkeypatch.setattr(curate.anthropic, "Anthropic", lambda **kwargs: client)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "k")


def test_curate_parses_response_and_costs_it(cfg, monkeypatch):
    fake_client(monkeypatch, SimpleNamespace(
        stop_reason="end_turn", model="claude-opus-5-5",
        content=[SimpleNamespace(type="thinking"),
                 SimpleNamespace(type="text", text=json.dumps({"picks": [raw_pick()]}))],
        usage=SimpleNamespace(input_tokens=1_000_000, output_tokens=100_000),
    ))
    picks, usage = curate.curate(cfg, [post()], [])
    assert len(picks) == 1 and usage["estimated_cost_usd"] == 6.0


@pytest.mark.parametrize("reason,message", [("refusal", "declined"), ("max_tokens", "ran out of room")])
def test_curate_explains_stops(cfg, monkeypatch, reason, message):
    fake_client(monkeypatch, SimpleNamespace(stop_reason=reason, content=[], usage=None, model="m"))
    with pytest.raises(curate.CurateError, match=message):
        curate.curate(cfg, [post()], [])


# ── Rendering ───────────────────────────────────────────────

def pick(**overrides):
    return {"id": "a", "title": "T", "url": "https://www.reddit.com/a", "subreddit": "ClaudeAI",
            "upvotes": 5, "comments": 1, "category": "AI news and updates", "what_it_is": "w",
            "why_its_good": "g", "why_useful_to_you": "u", "caution": False, **overrides}


def test_page_escapes_hostile_text():
    attack = '<script>alert(1)</script>'
    html = render.dashboard(
        [{"date": "2026-11-07", "picks": [pick(title=attack, what_it_is=attack, subreddit=attack)]}],
        ["AI news and updates"],
    )
    assert attack not in html and "&lt;script&gt;" in html


def test_page_refuses_non_web_links():
    html = render.dashboard(
        [{"date": "2026-11-07", "picks": [pick(url="javascript:alert(1)")]}], ["AI news and updates"]
    )
    assert "javascript:alert" not in html


def test_caution_shows_only_when_flagged():
    day = {"date": "2026-11-07", "picks": [pick()]}
    assert render.CAUTION not in render.dashboard([day], ["AI news and updates"])
    day["picks"] = [pick(caution=True)]
    assert render.CAUTION in render.dashboard([day], ["AI news and updates"])
    assert render.CAUTION in render.plain_text(day)
    assert render.CAUTION in render.email_html(day)


def test_empty_day_and_empty_site_render():
    assert "Nothing worth" in render.dashboard([{"date": "2026-11-07", "picks": []}], ["x"])
    assert "No digests yet" in render.dashboard([], ["x"])


# ── Scheduling and memory ───────────────────────────────────

MONDAY = datetime(2026, 11, 9, 8, 0)


def test_due_only_after_chosen_time_and_once(cfg):
    assert run.is_due(cfg, MONDAY, False)
    assert not run.is_due(cfg, MONDAY.replace(hour=7, minute=17), False)
    assert not run.is_due(cfg, MONDAY, True)


def test_weekly_only_runs_on_mondays(cfg):
    cfg["frequency"] = "weekly"
    assert run.is_due(cfg, MONDAY, False)
    assert not run.is_due(cfg, MONDAY.replace(day=10), False)


def test_seen_posts_are_skipped_and_forgotten_in_time():
    today = date(2026, 11, 7)
    seen = run.remember({"old": "2026-09-01", "recent": "2026-11-01"}, [{"id": "new"}], today, 30)
    assert set(seen) == {"recent", "new"}
    assert [p["id"] for p in run.new_candidates([post("recent"), post("fresh")], seen)] == ["fresh"]


# ── Failures ────────────────────────────────────────────────

@pytest.fixture
def failing_day(cfg, tmp_path, monkeypatch):
    """main() on a day when the scraper is broken, with every outside call faked."""
    cfg["delivery"]["time"] = "00:00"
    monkeypatch.setattr(run, "ROOT", tmp_path)
    monkeypatch.setattr(settings, "load", lambda _: cfg)
    monkeypatch.setattr(settings, "problems", lambda _: [])
    monkeypatch.setattr("sys.argv", ["run.py"])
    log = SimpleNamespace(fetches=0, alerts=[])

    def broken(_):
        log.fetches += 1
        raise collect.CollectError("scraper down")

    monkeypatch.setattr(collect, "fetch", broken)
    monkeypatch.setattr(deliver, "alert", lambda c, reason: log.alerts.append(reason))
    return log, tmp_path


def test_failure_alerts_once_and_stops_retrying(failing_day):
    log, tmp_path = failing_day
    assert [run.main() for _ in range(5)] == [1, 1, 1, 0, 0]
    assert log.fetches == run.MAX_TRIES_PER_DAY
    assert len(log.alerts) == 1 and "scraper down" in log.alerts[0]
    assert (tmp_path / "site" / "index.html").exists()


def test_unexpected_crash_still_alerts(failing_day, monkeypatch):
    log, _ = failing_day

    def crash(_):
        raise ValueError("secret detail")

    monkeypatch.setattr(collect, "fetch", crash)
    assert run.main() == 1
    assert "ValueError" in log.alerts[0] and "secret detail" not in log.alerts[0]


def test_disabled_config_does_nothing(failing_day, cfg):
    log, _ = failing_day
    cfg["enabled"] = False
    assert run.main() == 0 and log.fetches == 0


# ── A whole day, end to end, with a fake outside world ──────

@pytest.fixture
def world(cfg, tmp_path, monkeypatch):
    log = SimpleNamespace(fetches=0, curates=0, sends=[])

    def fake_fetch(_):
        log.fetches += 1
        return [post("a"), post("b", subreddit="ClaudeCode")]

    def fake_curate(_, candidates, titles):
        log.curates += 1
        log.titles = titles
        return curate.clean_picks([raw_pick(p["id"]) for p in candidates], candidates, cfg), {"model": "m"}

    monkeypatch.setattr(collect, "fetch", fake_fetch)
    monkeypatch.setattr(curate, "curate", fake_curate)
    monkeypatch.setattr(deliver, "digest", lambda c, d, u: log.sends.append(d["date"]))
    return log, cfg, tmp_path / "data", tmp_path / "site"


def test_full_day_saves_everything(world):
    log, cfg, data, site = world
    run.run_digest(cfg, date(2026, 11, 7), data, site)
    saved = json.loads((data / "digests" / "2026-11-07.json").read_text(encoding="utf-8"))
    assert saved["delivered"] and len(saved["picks"]) == 2
    assert (site / "index.html").exists() and (data / "raw" / "2026-11-07.json").exists()
    assert set(json.loads((data / "seen.json").read_text(encoding="utf-8"))) == {"a", "b"}


def test_retry_after_failed_delivery_doesnt_pay_again(world, monkeypatch):
    log, cfg, data, site = world

    def broken(*_):
        raise deliver.DeliverError("down")

    monkeypatch.setattr(deliver, "digest", broken)
    with pytest.raises(deliver.DeliverError):
        run.run_digest(cfg, date(2026, 11, 7), data, site)
    monkeypatch.setattr(deliver, "digest", lambda c, d, u: log.sends.append(d["date"]))
    run.run_digest(cfg, date(2026, 11, 7), data, site)
    assert log.fetches == 1 and log.curates == 1 and log.sends == ["2026-11-07"]


def test_retry_after_failed_ai_doesnt_rescrape(world, monkeypatch):
    log, cfg, data, site = world
    working = curate.curate

    def broken(*_):
        raise curate.CurateError("down")

    monkeypatch.setattr(curate, "curate", broken)
    with pytest.raises(curate.CurateError):
        run.run_digest(cfg, date(2026, 11, 7), data, site)
    monkeypatch.setattr(curate, "curate", working)
    run.run_digest(cfg, date(2026, 11, 7), data, site)
    assert log.fetches == 1 and log.curates == 1


def test_next_day_doesnt_repeat_yesterdays_picks(world):
    log, cfg, data, site = world
    run.run_digest(cfg, date(2026, 11, 7), data, site)
    run.run_digest(cfg, date(2026, 11, 8), data, site)
    saved = json.loads((data / "digests" / "2026-11-08.json").read_text(encoding="utf-8"))
    assert saved["picks"] == [] and log.curates == 1 and log.sends == ["2026-11-07", "2026-11-08"]
