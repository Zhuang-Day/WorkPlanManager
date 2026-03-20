from flask import Flask, render_template, request, redirect
import psycopg2
from psycopg2 import pool
import os

app = Flask(__name__)

# 建立全域連線池
db_pool = pool.SimpleConnectionPool(
    1, 10,  # 最小 / 最大連線數
    host=os.environ.get("DB_HOST"),
    database=os.environ.get("DB_NAME"),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASSWORD"),
    port=int(os.environ.get("DB_PORT", 6543))  # transaction pool 預設 6543
)

def get_db():
    return db_pool.getconn()

def release_db(conn):
    db_pool.putconn(conn)


# 首頁：列出所有任務
@app.route("/")
def home():
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, title, description, status, start_at, end_at, progress
            FROM tasks
            ORDER BY id DESC;
        """)
        tasks = cursor.fetchall()
    finally:
        cursor.close()
        release_db(conn)
    return render_template("index.html", tasks=tasks)


# 新增任務
@app.route("/add", methods=["POST"])
def add():
    conn = get_db()
    cursor = conn.cursor()
    try:
        title = request.form.get("title")
        description = request.form.get("description")
        status = request.form.get("status")
        start_at = request.form.get("start_at")
        end_at = request.form.get("end_at")
        progress = int(request.form.get("progress") or 0)

        if progress == 100:
            status = "done"

        cursor.execute("""
            INSERT INTO tasks (title, description, status, start_at, end_at, progress)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (title, description, status, start_at, end_at, progress))
        conn.commit()
    finally:
        cursor.close()
        release_db(conn)
    return redirect("/")


# 更新進度
@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    conn = get_db()
    cursor = conn.cursor()
    try:
        progress = int(request.form.get("progress"))
        status = "done" if progress == 100 else "doing"

        cursor.execute("""
            UPDATE tasks
            SET progress = %s, status = %s
            WHERE id = %s;
        """, (progress, status, id))
        conn.commit()
    finally:
        cursor.close()
        release_db(conn)
    return redirect("/")


# 刪除任務
@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM tasks WHERE id = %s;", (id,))
        conn.commit()
    finally:
        cursor.close()
        release_db(conn)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=False)