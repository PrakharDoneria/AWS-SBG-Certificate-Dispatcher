import os
import smtplib
from email.message import EmailMessage


def send_email(sender_email, sender_password, sender_name, to_email, subject, html_content, attachment_path):
    msg = EmailMessage()
    msg['Subject'] = subject
    # Format the sender properly as "Name <email@example.com>"
    msg['From'] = f"{sender_name} <{sender_email}>"
    msg['To'] = to_email
    
    msg.add_alternative(html_content, subtype='html')
    
    if os.path.exists(attachment_path):
        with open(attachment_path, 'rb') as f:
            file_data = f.read()
            msg.get_payload()[-1].add_related(file_data, maintype='image', subtype='png', cid='<certificate-image>')
            msg.add_attachment(file_data, maintype='image', subtype='png', filename="certificate.png")
            
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        return True
    except smtplib.SMTPAuthenticationError:
        print("Failed to authenticate. Check the Gmail address and App Password.")
        return False
    except Exception as e:
        print(f"Failed to send to {to_email}: {e}")
        return False
