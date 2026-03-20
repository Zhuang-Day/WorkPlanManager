from flask import Flask, render_template, request, redirect
import psycopg2
import os

app = Flask(__name__)

# 資料庫連線
def get_db():
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        port=5432
    )
    return conn


# 首頁：顯示所有任務
@app.route("/")
def home():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, description, status, start_at, end_at, progress
        FROM tasks
        ORDER BY id DESC;
    """)

    tasks = cursor.fetchall()
    conn.close()

    return render_template("index.html", tasks=tasks)


# 新增任務
@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    description = request.form.get("description")
    status = request.form.get("status")
    start_at = request.form.get("start_at")
    end_at = request.form.get("end_at")
    progress = request.form.get("progress") or 0

    progress = int(progress)

    # 同步規則
    if progress == 100:
        status = "done"

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tasks (title, description, status, start_at, end_at, progress)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (title, description, status, start_at, end_at, progress))

    conn.commit()
    conn.close()

    return redirect("/")


# 更新進度
@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    progress = int(request.form.get("progress"))

    # 同步 status
    status = "done" if progress == 100 else "doing"

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks
        SET progress = %s, status = %s
        WHERE id = %s;
    """, (progress, status, id))

    conn.commit()
    conn.close()

    return redirect("/")


# 刪除任務
@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tasks WHERE id = %s;", (id,))

    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    app.run()