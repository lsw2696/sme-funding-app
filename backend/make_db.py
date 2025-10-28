import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

# 메인 진단 신청 테이블 생성
c.execute("""
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
print("✅ database.db created successfully!")
