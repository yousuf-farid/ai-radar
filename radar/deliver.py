"""Step 4: send messages by email (Resend) and/or Slack."""
import os

import requests

from . import render

FROM_ADDRESS = "AI Radar <onboarding@resend.dev>"


class DeliverError(Exception):
    pass


def _email(subject, html, text):
    response = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {os.environ['RESEND_API_KEY']}"},
        json={
            "from": os.environ.get("DIGEST_FROM") or FROM_ADDRESS,
            "to": [os.environ["DIGEST_EMAIL"]],
            "subject": subject,
            "html": html,
            "text": text,
        },
        timeout=30,
    )
    if response.status_code >= 400:
        hint = (
            " Without your own domain, Resend only delivers to the address you signed up with."
            if response.status_code == 403
            else ""
        )
        raise DeliverError(f"Resend returned error {response.status_code}.{hint}")


def _slack(subject, text):
    # Slack "mrkdwn" treats these characters as markup, so post text is neutralised.
    safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    response = requests.post(
        os.environ["SLACK_WEBHOOK_URL"], json={"text": f"*{subject}*\n\n{safe}"[:39000]}, timeout=30
    )
    if response.status_code >= 400:
        raise DeliverError(f"Slack returned error {response.status_code}.")


def _send(cfg, subject, html, text):
    channel = cfg["delivery"]["channel"]
    if channel in ("email", "both"):
        _email(subject, html, text)
    if channel in ("slack", "both"):
        _slack(subject, text)


def digest(cfg, the_digest, dashboard_url=""):
    _send(
        cfg,
        render.subject(the_digest),
        render.email_html(the_digest, dashboard_url),
        render.plain_text(the_digest, dashboard_url),
    )


def alert(cfg, reason):
    """Tell the owner something broke. Never raises: the failure itself must still be reported."""
    try:
        _send(cfg, "AI Radar could not run today", f"<p>{render.escape(reason)}</p>", reason)
    except Exception as error:  # noqa: BLE001 - a failed alert must not hide the original failure
        print(f"Could not send the failure alert either: {type(error).__name__}")
