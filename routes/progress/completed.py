from flask import Blueprint, render_template

completed_bp = Blueprint("completed", __name__)

@completed_bp.route("/")
def index():
    return render_template("completed.html")
