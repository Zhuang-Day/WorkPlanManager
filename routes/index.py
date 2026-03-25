from flask import Blueprint, render_template, request, redirect, session
from datetime import datetime, timezone
from utils.db import get_cursor
from utils.csrf import validate_csrf

index_bp = Blueprint("index", __name__)

@index_bp.route("/")
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

@index_bp.route("/add", methods=["POST"])
def add():
    if not validate_csrf():
        return "CSRF 驗證失敗", 403
    
    title = request.form.get("title")
    if not title:
        session["error"] = "title 不可為空"
        return redirect("/")
    
    try:
        start_at = datetime.fromisoformat(request.form.get("start_at")).replace(tzinfo=timezone.utc)
        end_at = datetime.fromisoformat(request.form.get("end_at")).replace(tzinfo=timezone.utc)
    except Exception:
        session["error"] = "時間格式錯誤"
        return redirect("/")
    
    if end_at < start_at:
        session["error"] = "結束時間必須晚於開始時間"
        return redirect("/")

    conn, cursor = get_cursor()
    try:
        cursor.execute(
            "INSERT INTO tasks (title, start_at, end_at) VALUES (%s, %s, %s);",
            (title, start_at, end_at)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(e)
        return "資料庫錯誤", 500
    finally:
        cursor.close()
        conn.close()
    
    return redirect("/")

@index_bp.route("/delete/<int:id>", methods=["POST"])
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