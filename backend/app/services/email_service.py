import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger(__name__)

def send_email(to_email, subject, body):
    """
    Sends an email to the specified recipient.
    """
    from_email = settings.EMAILS_FROM_EMAIL  # Set your email address
    password = settings.SMTP_PASSWORD  # Set your email password

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the email server
        with smtplib.SMTP('smtp.example.com', 587) as server:  # Replace with your SMTP server
            server.starttls()  # Secure the connection
            server.login(from_email, password)  # Login to your email account
            server.send_message(msg)  # Send the email
            logger.info(f"Email sent to {to_email}.")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
