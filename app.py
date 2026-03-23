
import os
from flask import Flask, render_template, request, redirect
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# 本機才會用到 .env；Render 直接用環境變數
load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("缺少環境變數 DATABASE_URL")

app = Flask(__name__)


def get_db():
    # 用單一 DSN（DATABASE_URL）連線，Supabase/本機都通用
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


# 連接資料庫
# def get_db():
#     conn = psycopg2.connect(
#         host=os.environ.get("DB_HOST"),
#         database=os.environ.get("DB_NAME"),
#         user=os.environ.get("DB_USER"),
#         password=os.environ.get("DB_PASSWORD"),
#         port=5432
#     )
#     return conn

# 首頁：顯示所有資料
@app.route("/")
def home():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes;")
    notes = cursor.fetchall()
    conn.close()
    return render_template("index.html", notes=notes)

# 新增資料
@app.route("/add", methods=["POST"])
def add():
    content = request.form.get("content")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notes (content) VALUES (%s);", (content,))
    conn.commit()
    conn.close()
    return redirect("/")

# 刪除資料
@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = %s;", (id,))
    conn.commit()
    conn.close()
    return redirect("/")



if __name__ == "__main__":
    # 本機開發：預設 5000；Render 部署：使用環境變數 PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

