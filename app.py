from flask import Flask, render_template, request, redirect
import psycopg2
import os

app = Flask(__name__)

# 連接資料庫
def get_db():
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        port=5432
    )
    return conn

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
    app.run()