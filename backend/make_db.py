import sqlite3
import os

# -------------------
# DB 경로 지정
# -------------------
DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

# -------------------
# DB 연결
# -------------------
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# -------------------
# 테이블 생성 (없으면 자동 생성)
# -------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT,
    company_name TEXT,
    owner_name TEXT,
    business_type TEXT,
    start_year TEXT,
    sales_range TEXT,
    employee_count TEXT,
    urgent_issue TEXT,
    loan_status TEXT,
    contact_method TEXT,
    phone TEXT,
    contact_time TEXT,
    status TEXT DEFAULT '미연락',
    memo TEXT
)
""")

conn.commit()
conn.close()

print("✅ database.db created and leads table initialized!")
