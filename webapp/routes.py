import json
import urllib.request

from flask import jsonify, render_template, request, send_file, send_from_directory

from webapp.algo import DEFAULT_SECRET_KEY, decode_certificate_token
from webapp.services import ROOT, dispatch_certificates, render_preview


def register_routes(app):
    def page(template, **context):
        return render_template(template, active_path=request.path, **context)

    @app.get("/")
    def home():
        return page("home.html")

    @app.get("/about")
    def about_page():
        return page("about.html")

    @app.get("/assets/<path:asset>")
    def assets(asset):
        return send_from_directory(ROOT, asset)

    @app.get("/sbg-admin")
    def admin_gate():
        return page("admin_gate.html")

    @app.get("/sbg-admin/login")
    def login():
        return page("login.html")

    @app.get("/sbg-admin/dashboard")
    def dashboard():
        return page("dashboard.html")

    @app.get("/compose/new")
    def compose():
        return page("compose.html")

    @app.get("/sbg-admin/lists")
    def lists():
        return page("lists.html")

    @app.get("/verify/<token>")
    def verify(token):
        verification = decode_certificate_token(token, DEFAULT_SECRET_KEY)
        return page("verify.html", verification=verification)

    @app.get("/api/about")
    def about():
        try:
            headers = {"User-Agent": "AWS-SBG-Certificate-Dispatcher"}
            with urllib.request.urlopen(urllib.request.Request("https://api.github.com/users/PrakharDoneria", headers=headers), timeout=4) as response:
                user = json.loads(response.read().decode("utf-8"))
            with urllib.request.urlopen(urllib.request.Request("https://api.github.com/repos/PrakharDoneria/AWS-SBG-Certificate-Dispatcher", headers=headers), timeout=4) as response:
                user["project"] = json.loads(response.read().decode("utf-8"))
            return jsonify(user)
        except Exception:
            return jsonify({"name": "Prakhar Doneria", "login": "PrakharDoneria", "html_url": "https://github.com/PrakharDoneria", "project": {"html_url": "https://github.com/PrakharDoneria/AWS-SBG-Certificate-Dispatcher"}})

    @app.get("/api/sample-csv")
    def sample_csv():
        return send_file(ROOT / "sample.data.csv", as_attachment=True, download_name="sample.data.csv", mimetype="text/csv")

    @app.post("/api/preview-certificate")
    def preview_certificate():
        certificate_file = request.files.get("certificate")
        if not certificate_file or not certificate_file.filename:
            return jsonify({"error": "Upload a certificate template first."}), 400
        try:
            return jsonify({"image": render_preview(certificate_file)})
        except ValueError as error:
            return jsonify({"error": str(error)}), 400

    @app.post("/api/send")
    def send_certificates():
        credentials = {
            "email": request.form.get("sender_email", "").strip(),
            "password": request.form.get("sender_password", ""),
            "name": request.form.get("sender_name", "Prakhar Doneria").strip(),
        }
        details = {
            "subject": request.form.get("subject", "Certificate").strip(),
            "body": request.form.get("body", ""),
            "event_name": request.form.get("event_name", "AWS Student Builder Group Certificate"),
        }
        list_file = request.files.get("list")
        certificate_file = request.files.get("certificate")
        if not credentials["email"] or not credentials["password"] or not list_file or not certificate_file:
            return jsonify({"error": "Sender credentials, a mailing list, and a certificate are required."}), 400
        try:
            return jsonify(dispatch_certificates(credentials, details, list_file, certificate_file))
        except ValueError as error:
            return jsonify({"error": str(error)}), 400
        except Exception as error:
            app.logger.exception("Certificate dispatch failed")
            return jsonify({"error": f"Certificate dispatch failed: {error}"}), 502