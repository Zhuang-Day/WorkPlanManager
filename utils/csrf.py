from flask import session, request
import secrets

def set_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)

def validate_csrf():
    token = request.form.get("csrf_token")
    if not token:
        return False
    return token == session.get("csrf_token")