from itsdangerous import BadSignature, URLSafeSerializer

DEFAULT_SECRET_KEY = "aws-sbg-certificate-verification-v1"


def generate_certificate_link(base_url, student_name, date_of_issue, event_name, secret_key):
    """Create a stateless, signed URL containing public certificate details."""
    serializer = URLSafeSerializer(secret_key)
    payload = {
        "name": student_name.strip(),
        "date": date_of_issue.strip(),
        "event": event_name.strip(),
    }
    token = serializer.dumps(payload)
    return f"{base_url.rstrip('/')}/{token}"


def decode_certificate_token(token, secret_key):
    """Decode a certificate token and safely reject tampered values."""
    serializer = URLSafeSerializer(secret_key)
    try:
        return {"valid": True, "data": serializer.loads(token)}
    except BadSignature:
        return {
            "valid": False,
            "data": None,
            "error": "Tampered or invalid certificate token.",
        }