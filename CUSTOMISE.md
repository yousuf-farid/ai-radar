# Make it yours

Everything personal lives in one file, [`config.yaml`](config.yaml). To change a setting, open that file in your repository, click the pencil icon, edit, and click **Commit changes**. It applies from the next run, and you never need to touch the code.

Want a head start? Borrow from the complete examples: [AI at work](examples/ai-for-work.yaml), or [a weekly hobby digest](examples/hobby-weekly.yaml).

## Every setting at a glance

| Setting | What it does | Options | Default |
|---|---|---|---|
| `enabled` | Whether it runs by itself | `true`, `false` | `false` |
| `name` | Name on the dashboard and emails | Any text | `AI Radar` |
| `profile` | Tells the AI what's useful to you | [A few honest lines](#your-profile-the-setting-that-matters-most) | Required |
| `examples_of_useful_posts` | Shows the AI what good looks like | A list of titles or links, or empty | Required, or delete the line |
| `subreddits` | Where to look | Names without `r/` | `ClaudeAI`, `ClaudeCode` |
| `posts_per_subreddit` | How many top posts to fetch from each | A whole number | `10` |
| `posts_to_show` | The most that reach your digest | A whole number | `10` |
| `frequency` | How often | `daily`, or `weekly` (Mondays) | `daily` |
| `categories` | The labels, shown in this order | A list | 4 AI categories |
| `delivery: channel` | Where the digest goes | `email`, `slack`, `both`, `none` | `email` |
| `delivery: time` | When to send it, in quotes | `"07:30"` (24-hour clock) | `"07:30"` |
| `delivery: timezone` | Your timezone | [A name like](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) `Europe/London` | `Europe/London` |
| `scraper` | Which service fetches posts | `harshmaur`, `clearpath` | `harshmaur` |
| `model` | Which AI does the choosing | [See below](#which-ai-model) | `claude-opus-5-5` |
| `effort` | How hard the AI thinks | `low`, `medium`, `high` | `medium` |
| `max_post_chars` | Longer posts are cut to this before the AI reads them | A whole number | `2000` |
| `remember_days` | Won't repeat a post shown within this many days | A whole number | `30` |
| `keep_raw_days` | How long raw scraper files are kept | A whole number | `14` |

## Your profile: the setting that matters most

The AI only knows what you tell it. Be specific about your work, your level and your dislikes. Remember that it's public, so leave out anything private.

**Too vague:**

```yaml
profile: |
  I'm interested in AI and want to stay up to date.
```

**Much better:**

```yaml
profile: |
  What I do and what I use AI for:
  I run a five-person marketing agency. I use AI to draft client reports,
  and I'm trying to automate our weekly reporting.

  How technical I am, and the AI tools I already use:
  Not a developer. I can follow step-by-step guides but can't debug code.
  I use Claude and Claude Code every day.

  What I want more of:
  Ready-made skills I can use the same day, and workflows from other small
  businesses, with real results.

  What I never want to see:
  Benchmark arguments, model drama, memes, and complaints about usage limits.
```

Keep the two spaces at the start of each line under `profile: |`.

## Choosing subreddits

Use the name from the web address. For `reddit.com/r/ClaudeAI`, write `ClaudeAI`.

- **Mix them:** one or two busy general communities, plus a few small, specific ones where the useful detail tends to live.
- **It works for any interest.** Change the subreddits, profile and categories, and the digest follows.
- **Starting points for AI:** `ClaudeAI`, `ClaudeCode`, `ChatGPTPro`, `LocalLLaMA`, `PromptEngineering`, `automation`.

## How much to fetch

The AI picks from whatever is fetched, so fetching more gives it more choice but costs more. Apify's free credit is $5 a month, and if it runs out, runs stop until next month. This table shows the estimated monthly cost of a daily digest on the default scraper:

| Subreddits | 5 posts each | 10 posts each | 15 posts each | 25 posts each |
|---|---|---|---|---|
| **2** | $1.20 | $1.80 | $2.40 | $3.60 |
| **3** | $1.50 | $2.40 | $3.30 | $5.10 ⚠️ |
| **5** | $2.10 | $3.60 | $5.10 ⚠️ | $8.10 ⚠️ |
| **8** | $3.00 | $5.40 ⚠️ | $7.80 ⚠️ | $12.60 ⚠️ |

⚠️ is over the free credit. `check-setup` works out your own estimate and warns you if it's too high. A weekly digest costs about a seventh as much, since it runs far less often and fetches the same amount each time.

## Categories

List them in the order you want to see them, since posts appear in that order. So put what you most want to act on at the top. Three to five works well, and each post gets exactly one.

```yaml
categories:
  - Tools, skills and resources
  - Tutorials and how-tos
  - AI news and updates
```

Changing them only affects new digests.

## Delivery

```yaml
delivery:
  channel: email
  time: "07:30"
  timezone: Europe/London
```

- **Timing:** the digest goes out on the first check after your chosen time, usually within the hour. Clock changes are handled for you.
- **Email:** your address is kept in the `DIGEST_EMAIL` secret, not this file. To change it, see below.
- **Slack:** add a `SLACK_WEBHOOK_URL` secret and set `channel: slack`.
- **Both:** set `channel: both`, with the secrets for each.
- **Dashboard only:** set `channel: none`. You'll then get no failure alerts either, so check in now and then.

**Changing your email address:** Resend only delivers to the address on your Resend account. So update your Resend account's address too, or use a new account with a new `RESEND_API_KEY`. To send to anyone else, you'd need to [verify your own domain](https://resend.com/domains) with Resend and add a `DIGEST_FROM` secret holding an address on that domain, such as `digest@yourdomain.com`.

## Which AI model

These are estimates for one digest a day from about 50 posts. Actual costs vary, so check your Anthropic usage after a week.

| `model` | Per month | Best for |
|---|---|---|
| `claude-opus-5-5` | About $4 | The sharpest picks. A good place to start |
| `claude-sonnet-5-5` | About $2 | A solid middle ground |
| `claude-haiku-5-5` | About $0.10 | Lowest cost. Check that its picks are still good enough |

**A good way to choose:** start with the best, run it for a week, then try a cheaper one for a week. If you can't tell the difference, keep the cheaper one.

## Improving your picks

Do these in order, as the earlier ones help most:

1. **Getting posts you don't want?** Add them to "What I never want to see" in your profile. Be concrete: "benchmark arguments" beats "low-quality posts".
2. **Missing posts you'd want?** Add them to `examples_of_useful_posts`.
3. **Wrong level?** Be more exact about what you can and can't do.
4. **Good posts never appear?** They may not be fetched at all. Add a smaller subreddit or raise `posts_per_subreddit`, checking the [cost table](#how-much-to-fetch).
5. **Too much?** Lower `posts_to_show`. The AI can already pick fewer on a quiet day.
6. **Same topic again and again?** It already skips posts it has shown and is told about the last 14 days of titles, so raise `remember_days` only if the same posts return.

## Pausing or stopping

- **Pause:** set `enabled: false`. Nothing runs and nothing is charged.
- **Stop completely:** delete your repository, and delete your keys on Apify, Anthropic and Resend.
