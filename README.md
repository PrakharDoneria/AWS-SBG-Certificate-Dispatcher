# AWS SGB Certificate Dispatcher

A Python-based automated certificate generator and email dispatcher designed for the AWS Student Builder Group (SGB). This tool takes a base certificate template, dynamically overlays student names from a CSV file, and dispatches them via email with a personalized HTML body.

## Features

- **Automated Generation:** Uses `Pillow` to generate customized certificates by writing the student's name into a specified bounding box on the template.
- **Bulk Email Dispatching:** Sends personalized HTML emails with the generated certificate attached using Gmail's SMTP server.
- **Testing Mode:** Easily test certificate generation locally without sending out any emails.
- **Automatic Organization:** Saves test certificates to `certificates/test/` and dispatched certificates to `certificates/dispatch/`.
- **Modular Codebase:** Code logic is cleanly separated into image generation (`certificate.py`), email handling (`email_sender.py`), and a main coordinator script (`main.py`).

## Setup Instructions

### 1. Prerequisites
Ensure you have Python 3 installed on your machine.

### 2. Install Dependencies
Install the required python packages from `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory (you can copy the structure from the provided `.env` if one exists) and populate it with your email credentials and preferences:
```env
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
SENDER_NAME=Prakhar Doneria
DEFAULT_SUBJECT=AWS Cloud & DSA Coding Challenge 2026 Certificate
```
*(Note: To get a Gmail App Password, you must enable 2-Step Verification on your Google Account and generate an app password under Security settings.)*

### 4. Provide Required Files
Ensure the following files are present in the project root:
- **`certificate.png`**: The blank certificate image template.
- **`body.html`**: The HTML template used for the email body. It supports the following variables: `{{full_name}}`, `{{first_name}}`, `{{event_name}}`, and `{{issue_date}}`.
- **`data.csv`**: A CSV file containing the recipients. It must have exactly two columns: `name` and `email`.

*(If you only have `sample.data.csv`, make sure to rename it to `data.csv` or copy its contents into a new `data.csv` file before running the script.)*

## Usage

Run the main application script:

```bash
python main.py
```

Upon running, you will be prompted with a choice:

1. **Test (don't mail just show certificate):** Generates a certificate for the first person in your `data.csv` file, displays it locally, and saves it in `certificates/test/` so you can verify the alignment and font size.
2. **Send all:** Iterates through every row in your `data.csv`, generates the personalized certificate, dynamically populates the email template, sends the email via Gmail, and archives the certificate permanently in `certificates/dispatch/`.
