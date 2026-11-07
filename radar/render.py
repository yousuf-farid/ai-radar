"""Step 3: turn digests into the dashboard page and the email/Slack text.

All text from Reddit or the AI is escaped here, so a post can't inject code into the page.
"""
from datetime import date
from html import escape

CAUTION = "Check who made this before installing or running it."

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>AI Radar</title>
<style>
:root{--bg:#f7f7f5;--card:#fff;--ink:#1c1c1a;--soft:#66665f;--line:#e4e4de;--accent:#b4451f;--warn-bg:#fdf3e1;--warn:#7a5310}
@media (prefers-color-scheme:dark){:root{--bg:#161615;--card:#20201e;--ink:#eeeeea;--soft:#a3a39b;--line:#33332f;--accent:#ef8a62;--warn-bg:#352a15;--warn:#e8c483}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
main{max-width:680px;margin:0 auto;padding:24px 16px 64px}
h1{font-size:24px;margin:0}
.sub{color:var(--soft);margin:2px 0 16px;font-size:14px}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:8px}
.chips button{font:inherit;font-size:14px;min-height:36px;padding:4px 12px;border-radius:18px;border:1px solid var(--line);background:var(--card);color:var(--ink);cursor:pointer}
.chips button[aria-pressed=true]{background:var(--ink);color:var(--bg);border-color:var(--ink)}
h2{font-size:15px;margin:32px 0 10px;color:var(--soft);font-weight:600}
article{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin-bottom:10px}
.cat{font-size:12px;font-weight:600;color:var(--accent)}
h3{font-size:17px;line-height:1.35;margin:2px 0 8px;overflow-wrap:anywhere}
h3 a{color:inherit}
p{margin:0 0 6px;font-size:15px}
.why{color:var(--soft)}
.meta{font-size:13px;color:var(--soft);margin-top:8px}
.warn{font-size:13px;background:var(--warn-bg);color:var(--warn);padding:6px 10px;border-radius:6px;margin:8px 0 0}
.empty{color:var(--soft)}
</style></head><body><main>
<h1>AI Radar</h1>
<p class="sub">%(updated)s</p>
<div class="chips" id="chips">%(chips)s</div>
%(days)s
</main>
<script>
var chips=document.querySelectorAll('#chips button');
chips.forEach(function(chip){chip.addEventListener('click',function(){
  chips.forEach(function(c){c.setAttribute('aria-pressed',c===chip)});
  var want=chip.dataset.cat;
  document.querySelectorAll('article').forEach(function(a){a.hidden=want&&a.dataset.cat!==want});
  document.querySelectorAll('section').forEach(function(s){s.hidden=!s.querySelector('article:not([hidden])')&&!!want});
})});
</script></body></html>
"""


def _nice_date(iso):
    d = date.fromisoformat(iso)
    return f"{d.strftime('%A')} {d.day} {d.strftime('%B %Y')}"


def _safe_url(url):
    """Only ever link to http(s) addresses."""
    url = str(url or "")
    return escape(url, quote=True) if url.startswith(("https://", "http://")) else "#"


def _card(pick):
    warn = f'<p class="warn">{CAUTION}</p>' if pick.get("caution") else ""
    return f"""<article data-cat="{escape(pick['category'], quote=True)}">
<div class="cat">{escape(pick['category'])}</div>
<h3><a href="{_safe_url(pick['url'])}" rel="noopener noreferrer" target="_blank">{escape(pick['title'])}</a></h3>
<p>{escape(pick['what_it_is'])}</p>
<p class="why">{escape(pick['why_its_good'])}</p>
<p class="why">{escape(pick['why_useful_to_you'])}</p>
{warn}<div class="meta">r/{escape(str(pick['subreddit']))} · {int(pick['upvotes'])} upvotes · {int(pick['comments'])} comments</div>
</article>"""


def dashboard(digests, categories):
    """digests: newest first."""
    chips = ['<button data-cat="" aria-pressed="true">All</button>'] + [
        f'<button data-cat="{escape(c, quote=True)}" aria-pressed="false">{escape(c)}</button>'
        for c in categories
    ]
    days = []
    for digest in digests:
        cards = "\n".join(_card(p) for p in digest["picks"]) or '<p class="empty">Nothing worth your time today.</p>'
        days.append(f"<section><h2>{_nice_date(digest['date'])}</h2>\n{cards}\n</section>")
    updated = f"Updated {_nice_date(digests[0]['date'])}" if digests else "No digests yet"
    return PAGE % {"updated": updated, "chips": "".join(chips), "days": "\n".join(days)}


def subject(digest):
    return f"AI Radar: {len(digest['picks'])} picks for {_nice_date(digest['date'])}"


def email_html(digest, dashboard_url=""):
    rows = []
    for p in digest["picks"]:
        warn = f'<br><em style="color:#7a5310">{CAUTION}</em>' if p.get("caution") else ""
        rows.append(
            f'<p style="margin:0 0 20px"><span style="font-size:12px;color:#b4451f">{escape(p["category"])}</span><br>'
            f'<a href="{_safe_url(p["url"])}" style="font-weight:600;color:#1c1c1a">{escape(p["title"])}</a><br>'
            f'{escape(p["what_it_is"])} {escape(p["why_its_good"])} {escape(p["why_useful_to_you"])}{warn}</p>'
        )
    body = "".join(rows) or "<p>Nothing worth your time today.</p>"
    link = f'<p><a href="{_safe_url(dashboard_url)}">Open the dashboard</a></p>' if dashboard_url else ""
    return f'<div style="font:15px/1.5 sans-serif;max-width:600px">{body}{link}</div>'


def plain_text(digest, dashboard_url=""):
    lines = []
    for p in digest["picks"]:
        lines += [f"[{p['category']}] {p['title']}", p["url"], p["what_it_is"], p["why_its_good"], p["why_useful_to_you"]]
        if p.get("caution"):
            lines.append(CAUTION)
        lines.append("")
    if not digest["picks"]:
        lines.append("Nothing worth your time today.")
    if dashboard_url:
        lines.append(f"Dashboard: {dashboard_url}")
    return "\n".join(lines)
