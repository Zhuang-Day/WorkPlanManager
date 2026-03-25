from flask import Blueprint, render_template, request, redirect, session
from dateutil.parser import parse
from utils.csrf import validate_csrf
from utils.db import get_cursor

task_sidebar_bp = Blueprint("task_sidebar", __name__)


@task_sidebar_bp.route("/sidebar-template")
def sidebar_template():
    return render_template("task_sidebar.html")


@task_sidebar_bp.route("/update/<int:id>", methods=["POST"])
def update(id):
    if not validate_csrf():
        return "CSRF 驗證失敗", 403

    title = request.form.get("title")
    start_at = request.form.get("start_at")
    end_at = request.form.get("end_at")
    status = request.form.get("status")
    progress = request.form.get("progress")
    description = request.form.get("description")

    # 基本驗證
    if not title:
        session["error"] = "標題不可為空"
        return redirect("/")

    # 時間解析，支援多種 ISO 格式
    try:
        start_at_dt = parse(start_at).replace(tzinfo=None)
        end_at_dt = parse(end_at).replace(tzinfo=None)
    except Exception:
        session["error"] = "時間格式錯誤"
        return redirect("/")

    if end_at_dt < start_at_dt:
        session["error"] = "結束時間必須晚於開始時間"
        return redirect("/")

    conn, cursor = get_cursor()
    try:
        print(request.form)
        cursor.execute(
            """
            UPDATE tasks
            SET title=%s,
                start_at=%s,
                end_at=%s,
                status=%s,
                progress=%s,
                description=%s,
                updated_at = NOW()
            WHERE id=%s
            RETURNING id, updated_at;
            """,
            (title, start_at_dt, end_at_dt, status, progress, description, id),
        )
        updated = cursor.fetchone()
        if not updated:
            conn.rollback()
            return "資料不存在", 404
        conn.commit()
        print("Updated record successfully")
        # 回傳 JSON
        return {
            "id": updated[0],
            "title": title,
            "start_at": start_at_dt.strftime("%Y-%m-%d"),
            "end_at": end_at_dt.strftime("%Y-%m-%d"),
            "progress": progress,
            "status": status,
            "description": description,
        }, 200
    except Exception as e:
        conn.rollback()
        print(e)
        return "資料庫錯誤", 500
    finally:
        cursor.close()
        conn.close()

