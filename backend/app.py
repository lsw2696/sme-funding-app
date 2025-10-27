import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Netlify에서 오는 요청 허용 (CORS)

# ---- DB 경로 ----
DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------------------------
# 기본 페이지 (Render에서도 직접 확인 가능하게 유지)
# ---------------------------------

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
    # 관리자 테이블 뷰(서버 렌더링 버전, 필요 없으면 삭제 가능)
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM leads ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return render_template("dashboard.html", leads=rows)


# ---------------------------------
# 공통으로 DB에 lead 저장하는 함수
# ---------------------------------

def insert_lead(category, data):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO leads (
            category,
            company_name,
            owner_name,
            business_type,
            start_year,
            sales_range,
            employee_count,
            urgent_issue,
            loan_status,
            contact_method,
            phone,
            contact_time,
            memo,
            created_at,
            status
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
        "미연락"
    ))
    conn.commit()
    conn.close()


# ---------------------------------
# API: 지원금 진단 폼 제출 (/ -> index.html)
# ---------------------------------

@app.route("/api/submit/support", methods=["POST"])
def api_submit_support():
    data = request.json
    insert_lead("지원금진단", data)
    return jsonify({"ok": True})


# ---------------------------------
# API: 운전자금 폼 제출 (/cash)
# ---------------------------------

@app.route("/api/submit/cash", methods=["POST"])
def api_submit_cash():
    data = request.json
    insert_lead("운전자금", data)
    return jsonify({"ok": True})


# ---------------------------------
# API: 세무·재무 진단 폼 제출 (/report)
# ---------------------------------

@app.route("/api/submit/report", methods=["POST"])
def api_submit_report():
    data = request.json
    insert_lead("세무·재무", data)
    return jsonify({"ok": True})


# ---------------------------------
# 관리자 API
# Netlify의 admin.html 에서 이 API들을 호출합니다.
# ---------------------------------

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "changeme")  # Render에서 환경변수로 바꿔주세요

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


# (선택) 관리자 엑셀 다운로드 API도 필요하다면 여기에 추가할 수 있음.
# /api/admin/export_excel 등


# ---------------------------------
# Render 실행 진입점
# ---------------------------------
if __name__ == "__main__":
    # Render는 PORT라는 환경변수를 준다. 없으면 로컬에서 5000으로.
    port = int(os.environ.get("PORT", 5000))
    # host=0.0.0.0 으로 해야 외부 접속 가능
    app.run(host="0.0.0.0", port=port)
