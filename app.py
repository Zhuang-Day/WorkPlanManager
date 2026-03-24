from unittest import result

from flask import Flask, render_template, request, redirect
from psycopg2 import Error
from datetime import datetime, timezone
from flask import session
import secrets
import psycopg2
import os
import psycopg2.extras


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key")


@app.before_request
def set_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)


# 連接資料庫
def get_db():
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        port=5432,
    )
    return conn


def get_cursor():
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    return conn, cursor


# 驗證CSRF Token
def validate_csrf():
    token = request.form.get("csrf_token")
    if not token:
        return False
    return token == session.get("csrf_token")


# 首頁：顯示所有資料
@app.route("/")
def task_list():
    conn, cursor = get_cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY start_at;")
    work_list = cursor.fetchall()
    cursor.close()
    conn.close()

    now = datetime.now(timezone.utc)

    result = []
    for item in work_list:
        start = item["start_at"]
        end = item["end_at"]
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
        if now <= start:
            progress = 0
        elif now >= end:
            progress = 100
        else:
            total = (end - start).total_seconds()
            done = (now - start).total_seconds()
            progress = int(done / total * 100)

        item = dict(item)
        item["progress"] = max(0, min(100, progress))
        result.append(item)

    error = session.pop("error", None)
    return render_template("index.html", work_list=result, error=error)


# 新增資料
@app.route("/add", methods=["POST"])
def add():
    if not validate_csrf():
        return "CSRF 驗證失敗", 403
        

    title = request.form.get("title")
    if not title:
        session["error"] = "title 不可為空"
        return redirect("/")
    try:
        start_at = datetime.fromisoformat(request.form.get("start_at")).replace(
            tzinfo=timezone.utc
        )
        end_at = datetime.fromisoformat(request.form.get("end_at")).replace(
            tzinfo=timezone.utc
        )
    except Exception:
        session["error"] = "時間格式錯誤"
        return redirect("/")

    if end_at <= start_at:
        session["error"] = "結束時間必須晚於開始時間"
        return redirect("/")
    conn, cursor = get_cursor()
    try:
        cursor.execute(
            """
            INSERT INTO tasks (title, start_at, end_at)
            VALUES (%s, %s, %s);
            """,
            (title, start_at, end_at),
        )
        conn.commit()
    except Error as e:
        conn.rollback()
        print(e)  # 或用 logging
        return "資料庫錯誤", 500
    finally:
        cursor.close()
        conn.close()

    return redirect("/")


# 刪除資料
@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    if not validate_csrf():
        return "CSRF 驗證失敗", 403
    conn, cursor = get_cursor()
    try:
        cursor.execute("DELETE FROM tasks WHERE id = %s RETURNING id;", (id,))
        deleted = cursor.fetchone()

        if not deleted:
            conn.rollback()
            return "資料不存在", 404

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(e)
        return "資料庫錯誤", 500
    finally:
        cursor.close()
        conn.close()

    return redirect("/")


if __name__ == "__main__":
    app.run()
