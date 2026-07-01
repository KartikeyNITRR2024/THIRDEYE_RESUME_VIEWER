"""
Optional: emails the generated PDF to yourself.
Uses Gmail SMTP with an App Password (not your normal Gmail password).
Setup: https://myaccount.google.com/apppasswords
"""

import os
import smtplib
from email.message import EmailMessage


def send_resume_email(to_email: str, pdf_path: str, company_name: str) -> None:
    sender = os.getenv("EMAIL_ADDRESS")
    app_password = os.getenv("EMAIL_APP_PASSWORD")

    if not sender or not app_password:
        raise RuntimeError("EMAIL_ADDRESS / EMAIL_APP_PASSWORD not set in .env")

    msg = EmailMessage()
    msg["Subject"] = f"Tailored Resume - {company_name}"
    msg["From"] = sender
    msg["To"] = to_email
    msg.set_content(f"Attached: your tailored resume for {company_name}.")

    with open(pdf_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="pdf",
            filename=os.path.basename(pdf_path),
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, app_password)
        smtp.send_message(msg)
