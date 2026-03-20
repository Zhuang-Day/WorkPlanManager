
from datetime import datetime
import os

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, IntegerField, DateTimeLocalField, SubmitField
from wtforms.validators import DataRequired, NumberRange, ValidationError
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# 讀取 .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_change_me")

if not DATABASE_URL:
    raise RuntimeError("請設定 .env 並提供 DATABASE_URL (需含 sslmode=require)")

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
csrf = CSRFProtect(app)

# 建立資料庫連線池
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
)

# ---- 表單 ----
class TaskForm(FlaskForm):
    title = StringField("任務標題", validators=[DataRequired(message="請輸入任務標題")])
    start_at = DateTimeLocalField(
        "開始時間",
        format="%Y-%m-%dT%H:%M",
        validators=[DataRequired(message="請選擇開始時間")]
    )
    end_at = DateTimeLocalField(
        "結束時間",
        format="%Y-%m-%dT%H:%M",
        validators=[DataRequired(message="請選擇結束時間")]
    )
    progress = IntegerField(
        "進度（0-100）",
        default=0,
        validators=[DataRequired(), NumberRange(min=0, max=100, message="進度需介於 0-100")]
    )
    submit = SubmitField("儲存")

    def validate_end_at(self, field):
        if self.start_at.data and field.data and field.data < self.start_at.data:
            raise ValidationError("結束時間需晚於或等於開始時間")

# ---- 路由 ----
@app.route("/", methods=["GET", "POST"])
def index():
    form = TaskForm()
    if form.validate_on_submit():
        try:
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        insert into public.tasks (title, start_at, end_at, progress)
                        values (:title, :start_at, :end_at, :progress)
                    """),
                    {
                        "title": form.title.data.strip(),
                        "start_at": form.start_at.data,
                        "end_at": form.end_at.data,
                        "progress": form.progress.data,
                    }
                )
            flash("任務已新增", "success")
            return redirect(url_for("index"))
        except SQLAlchemyError as e:
            app.logger.exception("新增任務失敗")
            flash(f"新增任務失敗：{e}", "danger")

    # 取得列表
    with engine.begin() as conn:
        rows = conn.execute(
            text(
                """
                select id, title, start_at, end_at, progress, created_at, updated_at
                from public.tasks
                order by start_at desc
                limit 200
                """
            )
        ).mappings().all()

    return render_template("index.html", form=form, tasks=rows)

@app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
def edit(task_id: int):
    form = TaskForm()

    if request.method == "GET":
        with engine.begin() as conn:
            row = conn.execute(
                text(
                    """
                    select id, title, start_at, end_at, progress
                    from public.tasks
                    where id = :id
                    """
                ),
                {"id": task_id}
            ).mappings().first()
        if not row:
            flash("找不到任務", "warning")
            return redirect(url_for("index"))

        # 填入表單（HTML datetime-local 需無秒）
        form.title.data = row["title"]
        form.start_at.data = row["start_at"].replace(second=0, microsecond=0)
        form.end_at.data = row["end_at"].replace(second=0, microsecond=0)
        form.progress.data = row["progress"]
        return render_template("edit.html", form=form, task_id=task_id)

    # POST 更新
    if form.validate_on_submit():
        try:
            with engine.begin() as conn:
                conn.execute(
                    text(
                        """
                        update public.tasks
                        set title = :title,
                            start_at = :start_at,
                            end_at = :end_at,
                            progress = :progress
                        where id = :id
                        """
                    ),
                    {
                        "id": task_id,
                        "title": form.title.data.strip(),
                        "start_at": form.start_at.data,
                        "end_at": form.end_at.data,
                        "progress": form.progress.data,
                    }
                )
            flash("任務已更新", "success")
            return redirect(url_for("index"))
        except SQLAlchemyError as e:
            app.logger.exception("更新任務失敗")
            flash(f"更新任務失敗：{e}", "danger")

    return render_template("edit.html", form=form, task_id=task_id)

@app.route("/tasks/<int:task_id>/progress", methods=["POST"])
def update_progress(task_id: int):
    # 行內小表單：只處理進度欄位
    try:
        progress_str = request.form.get("progress", "0").strip()
        progress = int(progress_str)
        if progress < 0 or progress > 100:
            raise ValueError("進度需介於 0-100")
        with engine.begin() as conn:
            conn.execute(
                text("update public.tasks set progress = :p where id = :id"),
                {"p": progress, "id": task_id}
            )
        flash("進度已更新", "success")
    except Exception as e:
        app.logger.exception("更新進度失敗")
        flash(f"更新進度失敗：{e}", "danger")
    return redirect(url_for("index"))

@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
def delete(task_id: int):
    try:
        with engine.begin() as conn:
            conn.execute(text("delete from public.tasks where id = :id"), {"id": task_id})
        flash("任務已刪除", "info")
    except SQLAlchemyError as e:
        app.logger.exception("刪除任務失敗")
        flash(f"刪除任務失敗：{e}", "danger")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
