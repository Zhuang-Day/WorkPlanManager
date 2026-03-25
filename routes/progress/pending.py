from flask import Blueprint, render_template

pending_bp = Blueprint('pending', __name__)


@pending_bp.route("/")
def index():
    return render_template('pending.html')
