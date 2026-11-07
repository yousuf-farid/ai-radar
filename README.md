# AI Radar

Every morning, AI Radar fetches the top posts from the subreddits you choose, has Claude pick the ones useful to *you*, explains each in a few lines, adds them to a dashboard you can open on your phone, and sends you a digest. It runs online, so your laptop can be off.

**Status: template.** The code is written and tested with fake data. It hasn't yet run against the real scraper, the real AI or real email, because those need accounts and keys.

## To use it

1. Follow **[SETUP.md](SETUP.md)**, which takes about 30 minutes with no coding.
2. Everything personal lives in **[config.yaml](config.yaml)**. Replace each `FILL IN`.

## How it works

```
config.yaml ──► 1. Collect ──► 2. Filter + summarise ──► 3. Dashboard
 (your settings)   Apify          Claude                ──► 4. Email / Slack
```

GitHub starts the job hourly, and it only acts once per day, after your chosen time. That way the clock changes and GitHub's occasional late starts don't matter.

| File | Job |
|---|---|
| `config.yaml` | Your settings |
| `run.py` | Runs the steps in order |
| `radar/collect.py` | Fetches posts. The only file that knows about scrapers |
| `radar/curate.py` | The AI step and its instructions. Edit `SYSTEM` here to tune the picks |
| `radar/render.py` | The dashboard and email design |
| `radar/deliver.py` | Sends the email or Slack message |
| `data/` | Saved results, updated by the job |
| `OPTIONS.md` | The scraper and tool comparison behind these choices |

## What it does when things go wrong

- **Bad data:** if the scraper returns nothing, or every post has 0 upvotes, the job stops rather than sending a bad digest.
- **Failures:** you get one alert a day. It tries at most 3 times a day, so a broken scraper can't drain your credit.
- **Retries:** each step saves its result, so a retry doesn't pay for the scraper or AI again, or send a second email.
- **Hostile posts:** the AI treats posts as untrusted text and has no tools. Links come from the scraper rather than the AI, and all post text is made safe before it reaches the dashboard. Anything that asks you to install or run something gets a warning.

## Try it without any accounts

This builds a sample dashboard from made-up posts in `preview/`.

```bash
pip install -r requirements.txt
```

```bash
python run.py --demo
```

Run the tests with `pip install pytest`, then `python -m pytest`.
