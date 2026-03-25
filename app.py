from flask import Flask, session
from routes import index_bp, progress_bp, weekly_bp, auth_bp
from utils.csrf import set_csrf_token
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key")

@app.before_request
def before_request():
    set_csrf_token()

app.register_blueprint(index_bp)
app.register_blueprint(progress_bp)
app.register_blueprint(weekly_bp, url_prefix="/weekly")
app.register_blueprint(auth_bp, url_prefix="/auth")

if __name__ == "__main__":
    app.run(debug=True)