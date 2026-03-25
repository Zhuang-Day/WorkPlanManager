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
    result = []
    for item in work_list:
        item = dict(item)
        result.append(item)
    todo_list = []
    pending_list = []
    doing_list = []
    done_list = []

    for item in result:
        if item["status"] == "todo":
            todo_list.append(item)
        elif item["status"] == "pending":
            pending_list.append(item)
        elif item["status"] == "done":
            done_list.append(item)
        else:
            doing_list.append(item)
    error = session.pop("error", None)
    return render_template(
        "index.html",
        todo_list=todo_list,
        pending_list=pending_list,
        doing_list=doing_list,
        done_list=done_list,
        error=error,
    )


@index_bp.route("/add", methods=["POST"])
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

    if end_at < start_at:
        session["error"] = "結束時間必須晚於開始時間"
        return redirect("/")

    conn, cursor = get_cursor()
    try:
        cursor.execute(
            "INSERT INTO tasks (title, start_at, end_at) VALUES (%s, %s, %s);",
            (title, start_at, end_at),
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
