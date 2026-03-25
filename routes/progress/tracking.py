
from flask import Blueprint, render_template

tracking_bp = Blueprint("tracking", __name__)

@tracking_bp.route("/")
def index():
    return render_template('progress.html')
    