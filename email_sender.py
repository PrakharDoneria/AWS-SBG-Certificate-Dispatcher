import os
import smtplib
from email.message import EmailMessage


class TemporaryEmailError(Exception):
    pass


def create_message(sender_email, sender_name, to_email, subject, html_content, attachment_path):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = f"{sender_name} <{sender_email}>"
    msg['To'] = to_email

    msg.add_alternative(html_content, subtype='html')

    if os.path.exists(attachment_path):
        with open(attachment_path, 'rb') as f:
            file_data = f.read()
            msg.get_payload()[-1].add_related(file_data, maintype='image', subtype='png', cid='<certificate-image>')
            msg.add_attachment(file_data, maintype='image', subtype='png', filename="certificate.png")

    return msg


def open_smtp_connection(sender_email, sender_password):
    smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30)
    try:
        smtp.login(sender_email, sender_password)
    except Exception:
        smtp.quit()
        raise
    return smtp


def send_email(sender_email, sender_password, sender_name, to_email, subject, html_content, attachment_path, smtp=None):
    msg = create_message(sender_email, sender_name, to_email, subject, html_content, attachment_path)
    owns_connection = smtp is None
    try:
        if owns_connection:
            with open_smtp_connection(sender_email, sender_password) as smtp:
                smtp.send_message(msg)
        else:
            smtp.send_message(msg)
        return True
    except smtplib.SMTPAuthenticationError:
        print("Failed to authenticate. Check the Gmail address and App Password.")
        return False
    except smtplib.SMTPResponseException as error:
        if 400 <= error.smtp_code < 500:
            raise TemporaryEmailError(f"SMTP {error.smtp_code}: {error.smtp_error}") from error
        print(f"Failed to send to {to_email}: {error}")
        return False
    except Exception as e:
        print(f"Failed to send to {to_email}: {e}")
        return False
