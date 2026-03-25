from flask import Blueprint, redirect, render_template, url_for, session

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/")
def index():
    session.clear()
    return render_template('index.html')