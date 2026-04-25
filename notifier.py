import requests
import smtplib
from email.mime.text import MIMEText
import os


# ── Slack ──────────────────────────────────────────────────────────────────────

def send_slack_notification(webhook_url: str, message: str):
    """
    Sends a message to a Slack channel via Incoming Webhook.
    Set up a webhook at: https://api.slack.com/messaging/webhooks
    """
    if not webhook_url:
        return

    payload = {"text": message}
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code == 200:
            print("  📣 Slack notification sent.")
        else:
            print(f"  ⚠️ Slack notification failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"  ⚠️ Slack error: {e}")


# ── Email ──────────────────────────────────────────────────────────────────────

def send_email_notification(to_email: str, subject: str, body: str):
    """
    Sends an email using Gmail SMTP.
    Set these environment variables before running:
        SMTP_EMAIL    - your Gmail address
        SMTP_PASSWORD - your Gmail App Password (not your regular password)
                        Get one at: https://myaccount.google.com/apppasswords

    Or update SMTP_HOST/PORT below for another provider.
    """
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_EMAIL", "")
    smtp_pass = os.getenv("SMTP_PASSWORD", "")

    if not smtp_user or not smtp_pass:
        print("  ⚠️ Email not configured. Set SMTP_EMAIL and SMTP_PASSWORD env vars.")
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_email, msg.as_string())
        print(f"  📧 Email sent to {to_email}.")
    except Exception as e:
        print(f"  ⚠️ Email error: {e}")
