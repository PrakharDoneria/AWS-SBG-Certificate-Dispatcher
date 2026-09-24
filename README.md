# AWS SBG Certificate Dispatcher

A community-built web app for generating personalized certificates and sending them through Gmail. It is made by SBGL **Prakhar Doneria** for the public and is not offered by AWS or its affiliates.

## Features

- Render certificate names with Pillow and the configured certificate bounding box.
- Preview the real rendered certificate before sending.
- Upload a CSV or select a mailing list already saved in the browser.
- Send personalized HTML email with a unique verification link per recipient.
- Verify certificates with signed, stateless links without a database.
- Keep Gmail credentials and mailing lists in browser local storage; they are not stored by the server.

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the server:

```bash
python main.py
```

Open `http://127.0.0.1:5000`.

The private workspace is available at `/sbg-admin` and uses the client-side key:

```text
aws-sbgl-certs
```

Use a Gmail App Password rather than a normal Gmail password. Credentials are entered in the browser and kept only in local storage for that browser.

## Project Structure

```text
certificate.py          Pillow certificate rendering
email_sender.py         Gmail SMTP delivery
main.py                 Application entry point
webapp/routes.py        Flask pages and API routes
webapp/services.py      CSV parsing, previews, dispatch, signed links
static/js/              Browser modules for auth, lists, home, and compose
static/css/             Global and component styles
templates/              Jinja page templates
fonts/                  Amazon Ember project fonts
icons/                  AWS SBG project icons
```

## Required Files

- `certificate.png`: blank certificate template.
- `body.html`: optional reusable email template with `{{full_name}}`, `{{first_name}}`, `{{event_name}}`, and `{{issue_date}}` placeholders.
- `sample.data.csv`: example CSV with `name,email` columns.

## Stateless Verification

The dispatcher signs the recipient name, event, and issue date with `webapp/algo/linkGenerator.py`. The resulting token is appended to `/verify/<token>`. The verification page decodes and validates the token directly, so no certificate database is required.

For production deployments, replace `DEFAULT_SECRET_KEY` in `webapp/algo/linkGenerator.py` with a private, stable deployment secret. Changing it invalidates previously generated links.

## Community

- Project: [PrakharDoneria/AWS-SBG-Certificate-Dispatcher](https://github.com/PrakharDoneria/AWS-SBG-Certificate-Dispatcher)
- Maintainer: [Prakhar Doneria](https://github.com/PrakharDoneria)
- Sponsorship: [Sponsor maintenance](https://github.com/sponsors/PrakharDoneria)