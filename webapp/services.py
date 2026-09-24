import base64
import csv
import html
import io
import os
import secrets
import tempfile
import time
from datetime import date
from pathlib import Path

from flask import request

from certificate import create_certificate
from email_sender import send_email
from webapp.algo import DEFAULT_SECRET_KEY, generate_certificate_link

ROOT = Path(__file__).resolve().parent.parent
PUBLIC_BASE_URL = os.getenv("CERTIFICATE_PUBLIC_URL", "https://aws-sbg-ieccet.antideploy.com")
EMAIL_DELAY_SECONDS = float(os.getenv("SGB_EMAIL_DELAY_SECONDS", "2"))


def parse_recipients(file_storage):
    try:
        rows = list(csv.DictReader(io.StringIO(file_storage.read().decode("utf-8-sig"))))
    except (UnicodeDecodeError, csv.Error) as error:
        raise ValueError("The mailing list must be a UTF-8 CSV file.") from error
    if not rows or not {"name", "email"}.issubset(rows[0].keys()):
        raise ValueError("CSV must include name and email columns.")
    return rows


def image_data_url(image_path):
    encoded = base64.b64encode(Path(image_path).read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def body_to_html(body):
    if "<" in body and ">" in body:
        return body
    paragraphs = [part.strip() for part in body.split("\n\n") if part.strip()]
    return "".join(f"<p style='margin:0 0 16px;line-height:1.6'>{html.escape(paragraph).replace(chr(10), '<br>')}</p>" for paragraph in paragraphs)


def recipients_to_csv(rows):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["name", "email"])
    writer.writeheader()
    writer.writerows({"name": row.get("name", ""), "email": row.get("email", "")} for row in rows)
    return output.getvalue()


def render_preview(template_storage):
    with tempfile.TemporaryDirectory(prefix="sbg-preview-") as temp_dir:
        template_path = Path(temp_dir) / "template.png"
        preview_path = Path(temp_dir) / "preview.png"
        template_storage.save(template_path)
        if not create_certificate("Prakhar Doneria", str(template_path), str(preview_path)):
            raise ValueError("The certificate template could not be rendered.")
        return image_data_url(preview_path)


def dispatch_certificates(credentials, details, list_file, certificate_file):
    rows = parse_recipients(list_file)
    sent, failed = 0, []
    remaining_csv = ""
    interrupted = False
    interruption_message = ""
    issued = date.today().strftime("%B %d, %Y")
    with tempfile.TemporaryDirectory(prefix="sbg-dispatch-") as temp_dir:
        template_path = Path(temp_dir) / "template.png"
        certificate_file.save(template_path)
        for index, row in enumerate(rows):
            name, email = row.get("name", "").strip(), row.get("email", "").strip()
            if not name or not email:
                continue
            certificate_id = secrets.token_urlsafe(12)
            output_path = Path(temp_dir) / f"{certificate_id}.png"
            if not create_certificate(name, str(template_path), str(output_path)):
                failed.append(email)
                continue
            html_body = body_to_html(details["body"])
            html_body = html_body.replace("{{full_name}}", html.escape(name)).replace("{{first_name}}", html.escape(name.split()[0]))
            html_body = html_body.replace("{{event_name}}", html.escape(details["event_name"])).replace("{{issue_date}}", issued)
            link = generate_certificate_link(
                f"{PUBLIC_BASE_URL.rstrip('/')}/verify",
                name,
                issued,
                details["event_name"],
                DEFAULT_SECRET_KEY,
            )
            html_body += f'<p style="margin-top:24px;font-size:12px;color:#667085">Verify Certificate at <a href="{link}">{link}</a></p>'
            html_body += '<p style="margin:24px 0 0"><img src="cid:certificate-image" alt="Your certificate" style="display:block;max-width:100%;height:auto"></p>'
            if send_email(credentials["email"], credentials["password"], credentials["name"], email, details["subject"], html_body, str(output_path)):
                sent += 1
                if index < len(rows) - 1:
                    time.sleep(EMAIL_DELAY_SECONDS)
            else:
                failed.append(email)
                interrupted = True
                interruption_message = f"Delivery stopped after an error sending to {email}."
                remaining_csv = recipients_to_csv(rows[index:])
                break
    return {
        "sent": sent,
        "total": len(rows),
        "failed": failed,
        "interrupted": interrupted,
        "message": interruption_message,
        "remaining_csv": remaining_csv,
    }