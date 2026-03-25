# routes/progress/__init__.py
from flask import Blueprint
from .completed import completed_bp
from .pending import pending_bp
from .tracking import tracking_bp

# 建立統一的 progress Blueprint
progress_bp = Blueprint("progress", __name__, url_prefix="/progress")

# 註冊子 Blueprint
progress_bp.register_blueprint(completed_bp, url_prefix="/completed")
progress_bp.register_blueprint(pending_bp, url_prefix="/pending")
progress_bp.register_blueprint(tracking_bp, url_prefix="/tracking")