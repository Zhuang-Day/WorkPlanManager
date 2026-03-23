import os
import logging

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv

# ── 環境變數 ────────────────────────────────────────────
load_dotenv()  # 本機讀 .env；Render 直接用環境變數

# ── App 初始化 ───────────────────────────────────────────
app = Flask(__name__)

# ── 日誌 ────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ── 資料庫連線池 ─────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("缺少環境變數 DATABASE_URL")

pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dsn=DATABASE_URL,
    cursor_factory=RealDictCursor,
)


def get_db():
    """從連線池取得連線。"""
    return pool.getconn()


def release_db(conn):
    """歸還連線至連線池。"""
    pool.putconn(conn)


# ── 路由 ─────────────────────────────────────────────────

@app.route("/")
def home():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, content FROM notes ORDER BY id DESC;")
            notes = cur.fetchall()
    except Exception as e:
        logger.error("查詢失敗: %s", e)
        notes = []
        flash("讀取資料時發生錯誤，請稍後再試。", "error")
    finally:
        release_db(conn)

    return render_template("index.html", notes=notes)


@app.route("/add", methods=["POST"])
def add():
    content = request.form.get("content", "").strip()
    if not content:
        flash("筆記內容不能為空白。", "warning")
        return redirect(url_for("home"))

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO notes (content) VALUES (%s);", (content,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error("新增失敗: %s", e)
        flash("新增資料時發生錯誤，請稍後再試。", "error")
    finally:
        release_db(conn)

    return redirect(url_for("home"))


@app.route("/delete/<int:note_id>", methods=["POST"])
def delete(note_id):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM notes WHERE id = %s;", (note_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error("刪除失敗 (id=%s): %s", note_id, e)
        flash("刪除資料時發生錯誤，請稍後再試。", "error")
    finally:
        release_db(conn)

    return redirect(url_for("home"))


# ── 啟動 ─────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    # debug=True 僅供本機，Render 透過 gunicorn 啟動不會走這段
    app.run(host="0.0.0.0", port=port, debug=True)