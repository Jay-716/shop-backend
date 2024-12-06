import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTPException

from email_validator import validate_email, EmailNotValidError

from app.utils.log_utils import logger
from config import smtp_server, smtp_port, account, account_name, account_password, subject


def send_mail(to: str, order_id: int, message: str):
    try:
        validate_email(to, check_deliverability=False)
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            content = MIMEMultipart()
            content["From"] = f"{account_name} <{account}>"
            content["To"] = to
            content["Subject"] = f"订单#{order_id}{subject}"

            # plain text
            text = MIMEText(message, "plain", "utf-8")
            content.attach(text)

            server.login(account, account_password)
            refused = server.sendmail(account, to, content.as_string())
            _ = refused
    except EmailNotValidError as e:
        logger.warning(f"send_email: invalid email address: {to}", exc_info=e)
    except SMTPException as e:
        logger.warning(f"send_email: failed to send an email: {message=}", exc_info=e)
    except Exception as e:
        logger.error(f"send_email: unexpected exception", exc_info=e)
