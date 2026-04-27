import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

logger = logging.getLogger(__name__)


def send_reset_email(to_email: str, full_name: str, reset_link: str) -> None:
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning(
            "SMTP not configured — password reset link for %s: %s",
            to_email,
            reset_link,
        )
        return

    subject = "Reset Your Password — Requirements Super Tool"
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #1E2A4A; padding: 24px; border-radius: 12px 12px 0 0; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 22px;">Requirements Super Tool</h1>
        </div>
        <div style="background: #ffffff; padding: 32px; border: 1px solid #e5e7eb; border-radius: 0 0 12px 12px;">
            <h2 style="color: #1E2A4A; margin-top: 0;">Reset Your Password</h2>
            <p style="color: #374151;">Hi {full_name},</p>
            <p style="color: #374151;">We received a request to reset the password for your account. Click the button below to set a new password:</p>
            <div style="text-align: center; margin: 32px 0;">
                <a href="{reset_link}"
                   style="background: #FF6B6B; color: white; padding: 14px 32px; border-radius: 50px;
                          text-decoration: none; font-weight: 600; font-size: 15px; display: inline-block;">
                    Reset Password
                </a>
            </div>
            <p style="color: #6b7280; font-size: 13px;">This link expires in <strong>1 hour</strong>. If you did not request a password reset, you can safely ignore this email.</p>
            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 24px 0;" />
            <p style="color: #9ca3af; font-size: 12px; text-align: center; margin: 0;">
                If the button above doesn't work, copy and paste this URL into your browser:<br />
                <a href="{reset_link}" style="color: #6b7280; word-break: break-all;">{reset_link}</a>
            </p>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM or settings.SMTP_USER
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html"))

    try:
        if settings.SMTP_PORT == 465:
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(msg["From"], to_email, msg.as_string())
        else:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.ehlo()
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(msg["From"], to_email, msg.as_string())
        logger.info("Password reset email sent to %s", to_email)
    except Exception as exc:
        logger.error("Failed to send password reset email to %s: %s", to_email, exc, exc_info=True)
