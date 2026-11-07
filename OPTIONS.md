# Scrapers and tools: what else is out there

Researched 7 November 2026. **None of these has been run yet.** Prices and features come from each vendor's own page where possible. Many comparison articles are written by vendors, so treat their rankings with care. Monthly costs assume 5 subreddits, 10 posts each, once a day: 1,500 posts and 30 runs a month, with no comments.

## Bottom line

- **The brief's main decision holds.** A paid third-party scraper is still the practical route for this project.
- **Keep harshmaur as the first scraper to test, with ClearPath as backup.** Both are already built into this template. Apify's free $5 a month should cover either, though its pricing page doesn't confirm the credit applies to third-party scraper fees, and the first test will show that.
- **Test one newcomer: RedditAPI (redditapis.com).** It charges per call rather than per post, so it could cost about $0.25 a month and make top comments affordable. The catch is that it names no company and doesn't say where its data comes from, so it needs a trial before anyone relies on it.
- **Reliability matters more than price here.** The gap between the Apify options is at most about $3 a month. A scraper that quietly returns zeros costs far more in lost trust.

## Reddit scrapers compared

| Option | Monthly cost | Top of today? | Real upvotes and comments? | Track record | Verdict |
|---|---|---|---|---|---|
| **[harshmaur](https://apify.com/harshmaur/reddit-scraper)** (Apify) | $3.60 | Likely. `/top/?t=week` is documented; `t=day` needs the test | Yes: `upVotes`, `commentsCount` | 99% run success, 4.7 rating, by far the most users | **Test first.** Can also fetch comments for only the chosen posts |
| **[ClearPath](https://apify.com/clearpath/reddit-subreddit-posts-scraper)** (Apify) | $3.00 | Yes, documented: `timeFilter: day` | Yes: `score`, `num_comments` | 100% success, about 440 monthly users, no reviews | **Backup.** No run fee, and flags banned or empty subreddits. Comments $0.99 per 1,000, but it has no option for chosen posts only |
| **[prodiger](https://apify.com/prodiger/reddit-scraper)** (Apify) | $1.80 | Yes, documented | Claimed: `score`, `numComments` | 98% success, about 50 monthly users, no reviews | **Possible.** Its page shows two prices, $1.15 and $6 per 1,000, and its examples name `automation-lab`, which the brief ruled out. Check both before trusting it |
| **[RedditAPI](https://www.redditapis.com/pushshift-alternative)** | About $0.25 ($0.50 free credit) | Yes, [documented](https://docs.redditapis.com/docs/listings/posts): `sort=top&t=day` | Claimed live: `upvotes`, `comments` | No SLA, no named company, data source not stated | **Worth a trial.** Replaces Apify if it holds up. Needs a small new adapter |
| **[Bright Data](https://brightdata.com/products/web-scraper/reddit)** | $0 within 5,000 free records, then $1.50 per 1,000 | Not confirmed. Takes a subreddit URL, but no sort or time option is listed | Comments yes, upvotes not confirmed | Large established company | **Check if the others fail.** The free tier is attractive, but setup is heavier |
| **[Arctic Shift](https://github.com/ArthurHeitmann/arctic_shift/blob/master/api/README.md)** | Free | No | Not for about 36 hours: scores show 0 or 1 until then | Volunteer-run, no uptime promise | **Emergency only.** A digest would have to be about two days behind |
| [bovi](https://apify.com/bovi/reddit-scraper) (Apify) | $2.25 | Partly | Same 36-hour delay, as it reads Arctic Shift | 90% success | **Ruled out** |
| [Serpent](https://apiserpent.com/blog/reddit-api-comparison-2026) | Under $0.10 | Not confirmed | Yes | Vendor's own claims | **Ruled out:** requires a $500 deposit |
| [ScrapeCreators, SocialCrawl](https://www.socialcrawl.dev/blog/best-reddit-data-apis-2026), [Decodo, Xpoz](https://www.xpoz.ai/blog/comparisons/best-reddit-api-alternatives-2026/) | $19 to $47 up front or monthly | Varies | Varies | Varies | **Ruled out on minimum spend** at this tiny volume |
| [khadinakbar](https://apify.com/khadinakbar/reddit-subreddit-scraper) (Apify) | About $3 | Not confirmed | Yes | 3 users | **Ruled out:** too unproven |
| [PullPush](https://think-pol.com/blogs/reddit-deleted-content-tools-tested) | Free | n/a | n/a | Reported down or refusing automated requests in 2026 | **Ruled out** |

### The trial

Run each for a few days. Test harshmaur and ClearPath from the Actions tab (see SETUP.md). They're pass or fail on these checks:

1. Are the posts really from the last day?
2. Are the upvote and comment counts real, and close to what Reddit shows?
3. Does every subreddit come back?
4. Does the bill match the estimate?

## If top comments become wanted

Comments are billed separately, so the choice of scraper matters here. Assuming 5 comments on each of the 10 picks:

| Option | Monthly total with comments | Notes |
|---|---|---|
| RedditAPI | About $0.70 | One extra call per pick |
| prodiger | About $2.80 | If its $1.15 price is the real one |
| harshmaur | About $7.20 | **Over the free $5**, so it needs a paid Apify plan (from [$19 a month](https://apify.com/pricing)) or fewer posts |

## Could we use something off the shelf?

Nothing found fits closely enough to replace this build.

- **[Daily AI Signal](https://github.com/vascode2/Daily-AI-Signal)** is the closest. It has no stars, no dashboard and no email, and by default reads Reddit's RSS feeds, which [close on 13 November](https://www.techrepublic.com/article/news-reddit-rss-public-api-shutdown/).
- **[tech-digest](https://github.com/CainPatel/tech-digest)** reports that its Reddit source is often skipped because of blocking.
- **[Latent Space AINews](https://latent.space/news/)** is a daily AI briefing with a free option and [RSS feeds](https://latent.space/feeds/). It isn't personal or Reddit-focused, but it could be a cheap extra source later.

## The brief's other facts and choices

- **Reddit's shutdown dates are confirmed by mainstream tech press.** [TechRepublic](https://www.techrepublic.com/article/news-reddit-rss-public-api-shutdown/) and [heise](https://www.heise.de/en/news/Reddit-to-shut-down-RSS-feeds-and-public-API-11473400.html) report RSS ending on 13 November 2026 and public API access closing by March 2027, from a 30 September announcement.
- **Email: Resend stays.** [About 3,000 emails a month free](https://freetier.co/compare/brevo-vs-resend). Without a domain, it [only delivers to the account's own address](https://resend.com/docs/knowledge-base/403-error-resend-dev-domain), which is fine when everyone has their own account. Gmail's SMTP is [generally advised against](https://www.sequenzy.com/blog/best-free-email-apis) for app email, and [Brevo](https://freetier.co/compare/brevo-vs-resend) is the fallback.
- **Apify's free plan really does stop instead of billing you.** [Access is blocked until the next monthly cycle](https://apify.com/pricing), and no card is needed.

## The risk to know about

Reddit is hostile to scraping and is taking it to court. It [sued SerpApi, Oxylabs, AWMProxy and Perplexity](https://searchengineland.com/reddit-sues-perplexity-serpapi-scraping-google-463681) in October 2025, and [one secondary report](https://www.kucoin.com/news/flash/reddit-lawsuit-against-serpapi-survives-dismissal-motion) says the SerpApi case survived a motion to dismiss in July 2026. Those cases target companies reselling data at scale. A personal digest is very different, and I found nothing on personal use, but this isn't legal advice.

The practical risk is that **any scraper here could break or disappear at short notice**. That's why only `radar/collect.py` knows about scrapers, and why the job stops and alerts you rather than sending bad data. Offering the template more widely, especially commercially, deserves a closer look at the terms first.
