# Setting up AI Radar

No coding needed, and about 30 minutes in total. You'll create four accounts, copy a key from each into GitHub, then fill in one settings file.

**Keep your keys private.** Only ever paste them into GitHub Secrets (step 3). Never put them in `config.yaml` or send them in a message.

## 1. Make your copy on GitHub

1. Create a free account at [github.com](https://github.com/signup).
2. Open the [AI Radar template](https://github.com/yousuf-farid/ai-radar) and click **Use this template → Create a new repository**.
3. Name it `ai-radar` and choose **Public**.

> **Public or private?** On a free GitHub account, the dashboard only works from a public repository. Anyone who finds it can see your settings, profile and picks, though not your keys or email address. If that's a problem, ask whoever set this up about hosting the dashboard elsewhere.

## 2. Create the other accounts and copy a key from each

Keep these in a notepad for a few minutes, then delete them after step 3.

| Account | Cost | Where to find the key | Secret name |
|---|---|---|---|
| [Apify](https://console.apify.com/sign-up) | Free, no card, $5 of credit a month | Settings → API & Integrations → copy the personal token | `APIFY_TOKEN` |
| [Anthropic](https://console.anthropic.com) | Prepaid. Add about $10 of credit. A Claude subscription doesn't cover this | API Keys → Create Key | `ANTHROPIC_API_KEY` |
| [Resend](https://resend.com) | Free | API Keys → Create API Key | `RESEND_API_KEY` |

**Important for email:** sign up to Resend with the same address you want the digest sent to. Without your own web domain, Resend only delivers to the address on your account.

To use Slack instead, create an incoming webhook in Slack and save it as `SLACK_WEBHOOK_URL`. You then don't need Resend or `DIGEST_EMAIL`.

## 3. Add your keys to GitHub

In your new repository, go to **Settings → Secrets and variables → Actions → New repository secret**. Add one secret per key, using the exact names above, and then this one:

| Secret name | Value |
|---|---|
| `DIGEST_EMAIL` | The address you signed up to Resend with |

## 4. Turn on the dashboard

In your repository, go to **Settings → Pages**, and under **Source** choose **GitHub Actions**.

Your dashboard's address will be `https://YOUR-GITHUB-NAME.github.io/ai-radar/`. It appears after the first digest, and you can then add it to your phone's home screen.

## 5. Allow the job to save results

Go to **Settings → Actions → General → Workflow permissions**, choose **Read and write permissions**, and click **Save**.

## 6. Fill in your settings

Open `config.yaml` in your repository and click the pencil icon. Replace every `FILL IN`, leaving `enabled: false` for now, then click **Commit changes**. The notes in the file explain each setting.

## 7. Test the scraper

This costs a few cents of your free credit.

1. Go to the **Actions** tab. If asked, click to enable workflows.
2. Click **AI Radar** on the left, then **Run workflow**, and choose **test-harshmaur**.
3. When it finishes, open the run and the **Run** step to see the list of posts.

**You're checking that:**
- the posts are from the last day
- they have real upvote and comment counts, not all zeros
- every subreddit you chose appears

If not, run **test-clearpath**. If that one looks better, change `scraper:` in `config.yaml` to `clearpath`. Anything odd? See `OPTIONS.md` for other scrapers.

## 8. Check everything, then go

1. Run the workflow again and choose **check-setup**. It lists anything still missing.
2. Run the workflow and choose **run-now**. This creates today's digest for real, so it uses some credit. You should get the digest within a few minutes.
3. If you're happy with it, change `enabled: false` to `enabled: true` in `config.yaml`.

It now runs by itself every day.

## Afterwards

- **Tuning:** if the picks are off, improve the `profile` and `examples_of_useful_posts` settings first. They make the biggest difference.
- **Cost:** check your usage on Apify and Anthropic after the first week. Once you've seen the quality, you can try a cheaper `model:` in `config.yaml`.
- **If you get a failure alert:** the message says what went wrong. The usual cause is credit running out. Apify's free credit resets monthly, and Anthropic's needs topping up.
- **Inactivity:** GitHub can pause scheduled jobs on repositories with no activity for 60 days. The daily save counts as activity, but check here if digests stop after a long gap.
