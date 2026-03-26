from flask import Flask
import os

# 嘗試安全載入 Blueprint 與工具
try:
    from routes import index_bp, progress_bp, weekly_bp, auth_bp, task_sidebar_bp
except ImportError as e:
    print("Blueprint import error:", e)
    # 先把 Blueprint 設為空 list 避免 crash
    index_bp = progress_bp = weekly_bp = auth_bp = task_sidebar_bp = None

try:
    from utils.csrf import set_csrf_token
except ImportError as e:
    print("CSRF util import error:", e)
    # 用空函數替代
    def set_csrf_token():
        pass

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key")

# before_request 安全包裝
@app.before_request
def before_request():
    try:
        set_csrf_token()
        print("CSRF token set")
    except Exception as e:
        print("Error in set_csrf_token:", e)

# 註冊 Blueprint（如果有正確載入才註冊）
if index_bp:
    app.register_blueprint(index_bp)
if progress_bp:
    app.register_blueprint(progress_bp)
if task_sidebar_bp:
    app.register_blueprint(task_sidebar_bp)
if weekly_bp:
    app.register_blueprint(weekly_bp, url_prefix="/weekly")
if auth_bp:
    app.register_blueprint(auth_bp, url_prefix="/auth")

# 本地開發用，不影響 Render gunicorn
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)