# Set up your digest

From this template to your own working digest in about 30 minutes, with no coding. Work through the steps in order, and tick them off as you go. Website layouts change, so a button may look a little different from what's described.

**Before you start:** have an email address ready and a card for about $10 of prepaid AI credit.

> 🔒 **Keep your keys private.** Keys are like passwords. Only ever paste them into GitHub Secrets (step 3). Never put them in `config.yaml` or send them in a message.

- [1. Copy the template](#1-copy-the-template) · 2 min
- [2. Create your accounts](#2-create-your-accounts) · 10 min
- [3. Add your keys to GitHub](#3-add-your-keys-to-github) · 5 min
- [4. Turn on the dashboard](#4-turn-on-the-dashboard) · 1 min
- [5. Fill in your preferences](#5-fill-in-your-preferences) · 10 min
- [6. Test the scraper](#6-test-the-scraper) · 2 min
- [7. Create your first digest](#7-create-your-first-digest) · 3 min
- [8. Switch it on](#8-switch-it-on) · 1 min
- [If something goes wrong](#if-something-goes-wrong)

---

## 1. Copy the template

- [ ] Create a free [GitHub account](https://github.com/signup), if you don't have one.
- [ ] Open **[Use this template](https://github.com/yousuf-farid/ai-radar/generate)**.
- [ ] Set **Repository name** to `ai-radar`.
- [ ] Choose **Public**, then click **Create repository**.

**Why public?** On a free GitHub account, the dashboard only works from a public repository. Anyone who finds it can see your settings, profile and picks, but not your keys or email address.

✅ **You should see** your own copy, with your username at the top: `your-name/ai-radar`. Everything from here on happens in your copy.

---

## 2. Create your accounts

Open a blank note to hold your keys for a few minutes. You'll delete it after step 3. Some sites only show a key once, so copy it straight away.

### Apify: fetches the posts (free, no card)

- [ ] Sign up at [console.apify.com](https://console.apify.com/sign-up).
- [ ] Go to **Settings → API & Integrations**.
- [ ] Copy your **Personal API token** into your note, labelled `APIFY_TOKEN`.

### Anthropic: picks and summarises (prepaid)

This is separate from a Claude subscription, which doesn't cover it.

- [ ] Sign up at [console.anthropic.com](https://console.anthropic.com).
- [ ] Under **Billing**, add about $10 of credit. At the default setting that's roughly two months.
- [ ] Under **API Keys**, click **Create Key**.
- [ ] Copy the key into your note, labelled `ANTHROPIC_API_KEY`.

### Resend: sends the email (free)

- [ ] Sign up at [resend.com](https://resend.com) **using the address you want your digest sent to**. Without your own web domain, Resend only delivers to that address.
- [ ] Under **API Keys**, click **Create API Key**.
- [ ] Copy the key into your note, labelled `RESEND_API_KEY`.

**Prefer Slack?** Skip Resend. Create a Slack [incoming webhook](https://api.slack.com/messaging/webhooks), label its address `SLACK_WEBHOOK_URL`, and set `channel: slack` in step 5.

✅ **You should have** three labelled keys in your note.

---

## 3. Add your keys to GitHub

In your copy, go to **Settings → Secrets and variables → Actions**. For each row below, click **New repository secret**, enter the name exactly as shown, paste the value, and click **Add secret**.

| Name | Value |
|---|---|
| `APIFY_TOKEN` | Your Apify token |
| `ANTHROPIC_API_KEY` | Your Anthropic key |
| `RESEND_API_KEY` | Your Resend key |
| `DIGEST_EMAIL` | The address you signed up to Resend with |

✅ **You should see** all 4 names listed. GitHub hides the values, so it's normal that you can't read them back.

- [ ] Delete your note.

---

## 4. Turn on the dashboard

- [ ] In your copy, go to **Settings → Pages**.
- [ ] Under **Build and deployment → Source**, choose **GitHub Actions**.

✅ **You should see** "GitHub Actions" selected. The dashboard itself appears after your first digest in step 7.

---

## 5. Fill in your preferences

- [ ] In your copy, click **`config.yaml`**, then the **pencil icon** to edit it.
- [ ] Replace every `FILL IN`:
  - **`profile`** is the most important part. Write a few honest lines about what you do, your level, and what you do and don't want to see.
  - **`examples_of_useful_posts`**: add a few posts you've found valuable, or delete the example line.
- [ ] Set your `subreddits`. About 5 stays within the free scraper credit.
- [ ] Check `categories` and your delivery `time`.
- [ ] Leave `enabled: false` for now.
- [ ] Click **Commit changes**, then confirm.

Not sure what to write? [CUSTOMISE.md](CUSTOMISE.md) explains every setting, and there are complete examples for [AI at work](examples/ai-for-work.yaml) and [a hobby](examples/hobby-weekly.yaml).

**Keep the spaces at the start of each line as they are.** They matter in this file. If one goes wrong, step 6 will tell you which line.

### How to run a check

The next steps all use the same four clicks, so here they are once:

1. Click the **Actions** tab in your copy. If asked, click the button to enable workflows.
2. Click **AI Radar** on the left.
3. Click **Run workflow** on the right, choose the action, and click the green **Run workflow** button.
4. After a moment, refresh and click the new run at the top. When it finishes, the results are on its page.

Now confirm your setup: run **`check-setup`**.

✅ **You should see** "All filled in, and every key is present", plus your estimated scraper cost. A red ✗ here just means something's left to do: the page lists exactly what.

---

## 6. Test the scraper

This is the real test that fetching works. It uses a few cents of your free credit.

- [ ] Run **`test-harshmaur`**, using the steps above.
- [ ] Read the list of posts on the run's page.

✅ **You should see** posts where:
- [ ] the dates are from the last day
- [ ] the upvote and comment counts look real, and not all zero (compare one with Reddit)
- [ ] every subreddit you chose appears, unless one is very quiet

**If that looks wrong,** run **`test-clearpath`**. If it looks better, edit `config.yaml` and change `scraper: harshmaur` to `scraper: clearpath`. If neither works, see [OPTIONS.md](OPTIONS.md) for other scrapers.

---

## 7. Create your first digest

This is a real run, so it uses a little credit.

- [ ] Run **`run-now`**.
- [ ] Wait a few minutes, until the run shows a green ✓.

✅ **You should see:**
- [ ] a digest in your inbox. Check spam the first time, and mark it as not spam if it's there.
- [ ] your dashboard at `https://YOUR-GITHUB-NAME.github.io/ai-radar/`. It can take another minute to appear.

Add the dashboard to your phone's home screen so it's one tap away.

Picks not quite right? That's normal at first. Improve your `profile` using [the tuning tips](CUSTOMISE.md#improving-your-picks).

---

## 8. Switch it on

- [ ] Edit `config.yaml` again and change `enabled: false` to `enabled: true`.
- [ ] Click **Commit changes**.

🎉 **That's it.** Your digest now runs by itself, even with your computer off. It may arrive up to about an hour after your chosen time, as GitHub's schedule isn't exact.

**In your first week,** check your usage on Apify and Anthropic to confirm the costs look right.

---

## If something goes wrong

Failed runs show the reason on their page, and you'll also get an alert once a day.

| What you see | What it means | What to do |
|---|---|---|
| "Still to do: …" | Something isn't filled in yet | Follow the list. For a missing secret, check the name in step 3 matches exactly |
| "config.yaml has a formatting problem near line N" | A space or symbol is out of place | Look at that line and the one above. Text containing a colon needs quotes. Compare with an [example](examples/ai-for-work.yaml) |
| "Apify returned error 401" | The Apify token is wrong | Copy it again and update the `APIFY_TOKEN` secret |
| "Apify returned error 402" | Credit has probably run out | Wait for it to reset next month, or fetch fewer posts ([see costs](CUSTOMISE.md#how-much-to-fetch)) |
| "returned no usable posts" | The scraper is broken, or its credit is gone | Check your Apify balance, then try `test-clearpath` |
| "Every post … has 0 upvotes" | The scraper's data can't be trusted | Switch `scraper` in `config.yaml` |
| "The ANTHROPIC_API_KEY looks wrong" | The key is wrong or was deleted | Create a new key and update the secret |
| "The AI request was rejected" | Usually no API credit left | Top up in the Anthropic console |
| "The AI declined today's batch" | One post tripped a safety check | Nothing. It tries again, and tomorrow's posts will differ |
| "Resend returned error 403" | The digest address doesn't match your Resend account | Make `DIGEST_EMAIL` the address you signed up with |
| "Already failed 3 times today" | It has stopped retrying to protect your credit | Fix the cause, then choose `run-now` to try again straight away |
| No email, but a green ✓ | It may be in spam, or was already sent today | Check spam. Each day's digest is only sent once |
| Dashboard shows a 404 | Pages isn't on, or no digest has been created | Repeat step 4, then choose `run-now`. It republishes the page without paying or emailing again |
| Failed at "Save results" with a permission error | GitHub is blocking the job from saving | Go to **Settings → Actions → General → Workflow permissions**, choose **Read and write** and save |
| Digests stop after a long gap | GitHub can pause schedules on inactive repositories | In the **Actions** tab, click the button to re-enable the workflow |

**Still stuck?** [Open an issue](https://github.com/yousuf-farid/ai-radar/issues), including the message you saw. Never include your keys.
