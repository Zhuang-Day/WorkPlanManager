import os
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras

# 載入本地 .env；Render 沒有也沒問題
load_dotenv()

def get_db():
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        port=int(os.environ.get("DB_PORT", 5432)),  # 建議從環境變數讀
    )
    return conn

def get_cursor():
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    return conn, cursor