import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS

# ---- Flask 앱 초기화 ----
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ---- DB 경로 설정 ----
DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

# ---- DB 연결 함수 ----
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ---- DB 초기화 함수 ----
def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
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
            memo TEXT,
            created_at TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

# ---- 메인 페이지 라우트 ----
@app.route("/")
def home_page():
    return render_template("index.html")

@app.route("/cash")
def cash_page():
    return render_template("cash.html")

@app.route("/report")
def report_page():
    return render_template("report.html")

@app.route("/about")
def about_page():
    return render_template("about.html")

@app.route("/success")
def success_page():
    return render_template("success.html")

@app.route("/dashboard")
def dashboard_page():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM leads ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return render_template("dashboard.html", leads=rows)

# ---- 데이터 삽입 공통 함수 ----
def insert_lead(category, data):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO leads (
            category, company_name, owner_name, business_type, start_year,
            sales_range, employee_count, urgent_issue, loan_status,
            contact_method, phone, contact_time, memo, created_at, status
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        category,
        data.get("company_name"),
        data.get("owner_name"),
        data.get("business_type"),
        data.get("start_year"),
        data.get("sales_range"),
        data.get("employee_count"),
        data.get("urgent_issue"),
        data.get("loan_status"),
        data.get("contact_method"),
        data.get("phone"),
        data.get("contact_time"),
        data.get("memo", ""),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "미연략"  # 미연락
    ))
    conn.commit()
    conn.close()

# ---- API: 지원금 진단 폼 제출 ----
@app.route("/api/submit/support", methods=["POST"])
def api_submit_support():
    data = request.json
    insert_lead("지원금진단", data)
    return jsonify({"ok": True})

# ---- API: 운전자금 폼 제출 ----
@app.route("/api/submit/cash", methods=["POST"])
def api_submit_cash():
    data = request.json
    insert_lead("운전자금", data)
    return jsonify({"ok": True})

# ---- API: 세무·재무 진단 폼 제출 ----
@app.route("/api/submit/report", methods=["POST"])
def api_submit_report():
    data = request.json
    insert_lead("세무·재무", data)
    return jsonify({"ok": True})

# ---- 관리자 API ----
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "changeme")

@app.route("/api/admin/login", methods=["POST"])
def api_admin_login():
    data = request.json
    if data.get("password") == ADMIN_PASSWORD:
        return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "비밀번호가 올바르지 않습니다."}), 401

@app.route("/api/admin/leads", methods=["GET"])
def api_admin_leads():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM leads ORDER BY id DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify({"ok": True, "leads": rows})

@app.route("/api/admin/update_status", methods=["POST"])
def api_admin_update_status():
    data = request.json
    lead_id = data.get("id")
    new_status = data.get("status")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE leads SET status=? WHERE id=?", (new_status, lead_id))
    conn.commit()
    conn.close()

    return jsonify({"ok": True})

# ---- 앱 실행 진입점 ----
if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)  # 이전 DB 삭제
    init_db()               # 새로 생성
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
