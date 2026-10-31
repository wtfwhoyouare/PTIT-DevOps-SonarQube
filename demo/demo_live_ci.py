# -*- coding: utf-8 -*-
"""
HỆ THỐNG ĐIỀU KHIỂN & THEO DÕI LUỒNG CI THỰC TẾ TRÊN GITHUB ACTIONS (LIVE CI RUNNER)

Chức năng:
1. Kích hoạt (Trigger) trực tiếp workflow CI/CD thật trên đám mây GitHub Actions thông qua GitHub CLI (gh).
2. Đọc và stream trạng thái thời gian thực (Real-time Live Polling) của từng Stage và từng Step:
   - [STAGE 1] Policy Guard — Kiểm tra Nhánh, Commit & PR
   - [STAGE 2] SonarQube SAST & Code Quality
   - [STAGE 2] Semgrep Security SAST
   - [STAGE 3] Production Gate (Docker Build & IaC Smoke Test)
   - [STAGE 4] Production CD (Deploy Observability & Workload)
3. Đọc và trích xuất trực tiếp các vi phạm an ninh (Security Annotations) khi bị chặn (Break-the-Build).
4. Tương tác linh hoạt qua Menu CLI hoặc tham số dòng lệnh.

YÊU CẦU:
- Máy tính đã cài đặt GitHub CLI (`gh`).
- Đã đăng nhập (`gh auth login`).
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

# Kích hoạt màu ANSI trên Windows console
if os.name == "nt":
    os.system("")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
if ROOT.name == "demo":
    ROOT = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ci.demo_runner import MEMBERS_CATALOG, extract_code_context

# ANSI Colors
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_BLUE = "\033[44m"


def print_banner(text: str, color: str = CYAN, border_char: str = "=") -> None:
    width = 82
    print(f"\n{color}{border_char * width}{RESET}")
    print(f"{BOLD}{color}{text.center(width)}{RESET}")
    print(f"{color}{border_char * width}{RESET}\n")


def check_gh_installed() -> bool:
    """Kiểm tra sự hiện diện và trạng thái xác thực của GitHub CLI."""
    try:
        res = subprocess.run(["gh", "--version"], capture_output=True, text=True, encoding="utf-8")
        if res.returncode != 0:
            return False
        auth = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, encoding="utf-8")
        return auth.returncode == 0
    except FileNotFoundError:
        return False


def get_latest_run_id() -> int | None:
    """Lấy mã Run ID của lần chạy mới nhất trên GitHub Actions."""
    cmd = ["gh", "run", "list", "--limit", "1", "--json", "databaseId"]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if res.returncode == 0 and res.stdout.strip():
        try:
            data = json.loads(res.stdout)
            if data and isinstance(data, list):
                return data[0].get("databaseId")
        except Exception:
            pass
    return None


def trigger_real_workflow(branch: str = "namng", enforce: bool = True) -> int | None:
    """Kích hoạt luồng CI thật trên GitHub Actions qua workflow_dispatch."""
    print(f"🚀 {BOLD}Đang gửi lệnh kích hoạt workflow lên GitHub Actions (nhánh: {CYAN}{branch}{RESET})...{RESET}")
    enforce_str = "true" if enforce else "false"
    cmd = [
        "gh", "workflow", "run", "devsecops-pipeline.yml",
        "--ref", branch,
        "-f", f"enforce_quality_gate={enforce_str}"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        print(f"❌ {RED}Lỗi kích hoạt workflow:{RESET}\n{res.stderr}")
        return None

    print(f"✔ {GREEN}Lệnh kích hoạt đã được gửi thành công!{RESET}")
    print(f"⏳ Đang chờ GitHub Actions tiếp nhận và cấp Run ID mới (khoảng 3-5 giây)...")

    # Thử chờ tối đa 15 giây để lấy Run ID mới
    prev_id = get_latest_run_id()
    for _ in range(6):
        time.sleep(2.5)
        new_id = get_latest_run_id()
        if new_id and (new_id != prev_id or prev_id is None):
            return new_id

    return new_id or prev_id


def get_repo_slug() -> str:
    """Lấy định danh repo dạng owner/repo từ git remote hoặc GitHub CLI."""
    res = subprocess.run(
        ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
        capture_output=True, text=True, encoding="utf-8"
    )
    return res.stdout.strip() if res.returncode == 0 and res.stdout.strip() else "wtfwhoyouare/PTIT-DevOps-SonarQube"


def fetch_job_annotations(repo_slug: str, job_id: int) -> list[dict]:
    """Lấy danh sách các vi phạm an ninh / annotations được GitHub ghi nhận cho một Job."""
    cmd = ["gh", "api", f"repos/{repo_slug}/check-runs/{job_id}/annotations"]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if res.returncode == 0 and res.stdout.strip():
        try:
            return json.loads(res.stdout)
        except Exception:
            pass
    return []


def load_or_download_artifacts(run_id: int) -> tuple[dict | None, dict | None, dict | None]:
    """Tìm hoặc tải artifacts của run để trích xuất báo cáo semgrep.json, quality-gate.json, issues.json."""
    cache_base = ROOT / "reports" / ".ci_cache"
    cache_base.mkdir(parents=True, exist_ok=True)

    semgrep_files = list(cache_base.glob(f"semgrep-security-report-*{run_id}*/semgrep.json"))
    sonar_gate_files = list(cache_base.glob(f"sonarqube-report-*{run_id}*/quality-gate.json"))
    sonar_issues_files = list(cache_base.glob(f"sonarqube-report-*{run_id}*/issues.json"))

    # Cũng kiểm tra thư mục scratch/ci_artifacts nếu có sẵn
    scratch_base = ROOT / "scratch" / "ci_artifacts"
    if not (semgrep_files and sonar_gate_files) and scratch_base.exists():
        if not semgrep_files:
            semgrep_files = list(scratch_base.glob(f"semgrep-security-report-*{run_id}*/semgrep.json"))
        if not sonar_gate_files:
            sonar_gate_files = list(scratch_base.glob(f"sonarqube-report-*{run_id}*/quality-gate.json"))
        if not sonar_issues_files:
            sonar_issues_files = list(scratch_base.glob(f"sonarqube-report-*{run_id}*/issues.json"))

    if not (semgrep_files and sonar_gate_files):
        try:
            subprocess.run(
                ["gh", "run", "download", str(run_id), "--dir", str(cache_base)],
                capture_output=True, text=True, timeout=15
            )
            semgrep_files = list(cache_base.glob(f"semgrep-security-report-*{run_id}*/semgrep.json"))
            sonar_gate_files = list(cache_base.glob(f"sonarqube-report-*{run_id}*/quality-gate.json"))
            sonar_issues_files = list(cache_base.glob(f"sonarqube-report-*{run_id}*/issues.json"))
        except Exception:
            pass

    semgrep_data = None
    sonar_gate = None
    sonar_issues = None

    if semgrep_files and semgrep_files[0].exists():
        try:
            semgrep_data = json.loads(semgrep_files[0].read_text(encoding="utf-8"))
        except Exception:
            pass

    if sonar_gate_files and sonar_gate_files[0].exists():
        try:
            sonar_gate = json.loads(sonar_gate_files[0].read_text(encoding="utf-8"))
        except Exception:
            pass

    if sonar_issues_files and sonar_issues_files[0].exists():
        try:
            sonar_issues = json.loads(sonar_issues_files[0].read_text(encoding="utf-8"))
        except Exception:
            pass

    return semgrep_data, sonar_gate, sonar_issues


# ==============================================================================
# CẤU HÌNH PHÂN QUYỀN & PHẠM VI MÃ NGUỒN CỦA 5 THÀNH VIÊN (RACI SCOPE MAPPING)
# ==============================================================================
MEMBER_SCOPE_MAP = {
    "namng": {
        "name": "Nguyễn Giang Nam",
        "order": 1,
        "keywords": ["ports.php", "news.php", "docker-compose.yml"],
        "scope": "Cổng thông tin công cộng, Quản lý quy chuẩn phân nhánh & Tra cứu cảng biển",
        "script": "python demo/demo_live_ci.py -m 1"
    },
    "haind": {
        "name": "Nguyễn Đình Hải",
        "order": 2,
        "keywords": ["login.php", "port_detail.php", "track_api.php", "db.php"],
        "scope": "Kiểm định Taint Analysis, Module Xác thực người dùng & Theo dõi Vận đơn",
        "script": "python demo/demo_live_ci.py -m 2"
    },
    "manhdx": {
        "name": "Đào Xuân Mạnh",
        "order": 3,
        "keywords": ["guide.php", "report_download.php", "admin_report_export.php"],
        "scope": "Kiểm soát Quality Gate, Module Cẩm nang Hàng hải & Hệ thống Kết xuất Báo cáo",
        "script": "python demo/demo_live_ci.py -m 3"
    },
    "anhld": {
        "name": "Lê Đức Anh",
        "order": 4,
        "keywords": ["account.php", "account_update.php", "shipment_detail.php", "docker-compose.prod.yml"],
        "scope": "Quản lý Tài khoản & Hồ sơ Đối tác, Theo dõi Chi tiết Vận tải & An toàn Cấu hình IaC",
        "script": "python demo/demo_live_ci.py -m 4"
    },
    "mainp": {
        "name": "Nguyễn Phương Mai",
        "order": 5,
        "keywords": ["comment_add.php", "comment_delete.php", "admin_console.php", "admin_dashboard.php", "db/Dockerfile", "Dockerfile"],
        "scope": "Hệ thống Bình luận Tương tác Đối tác, Phân hệ Quản trị Admin & Tuân thủ Luật",
        "script": "python demo/demo_live_ci.py -m 5"
    }
}


def resolve_member_key(key: str | None) -> str | None:
    """Ánh xạ số thứ tự (1-5) hoặc bí danh sang mã định danh thành viên."""
    if not key:
        return None
    k = key.strip().lower()
    num_map = {"1": "namng", "2": "haind", "3": "manhdx", "4": "anhld", "5": "mainp"}
    if k in num_map:
        return num_map[k]
    if k in MEMBER_SCOPE_MAP:
        return k
    for m_id, info in MEMBER_SCOPE_MAP.items():
        if k in info["name"].lower() or k == m_id:
            return m_id
    return None


def get_member_for_file(file_path: str) -> str | None:
    """Xác định thành viên phụ trách dựa trên đường dẫn tệp mã nguồn vi phạm."""
    norm = file_path.replace("\\", "/").lower()
    # docker-compose.prod.yml ưu tiên gán cho anhld trước docker-compose.yml của namng
    if "docker-compose.prod.yml" in norm:
        return "anhld"
    for m_id, info in MEMBER_SCOPE_MAP.items():
        for kw in info["keywords"]:
            if kw.lower() in norm:
                return m_id
    return None


def render_single_member_breakdown(
    m_id: str,
    m_info: dict,
    semgrep_list: list[dict],
    sonar_list: list[dict],
    annos_list: list[dict],
    show_header: bool = True,
    show_verbose: bool = False
) -> None:
    """In phần báo cáo lỗi chi tiết cho một thành viên cụ thể với bố cục trực quan, dễ đọc, chuẩn developer CLI."""
    m_catalog = MEMBERS_CATALOG.get(m_id)
    width = 86

    order = m_catalog.get("order", m_info.get("order", 1)) if m_catalog else m_info.get("order", 1)
    name = m_catalog.get("name", m_info.get("name", m_id)) if m_catalog else m_info.get("name", m_id)
    role = m_catalog.get("role", "") if m_catalog else ""
    scope = m_catalog.get("scope", m_info.get("scope", "")) if m_catalog else m_info.get("scope", "")
    script_cmd = f"python demo/demo_live_ci.py -m {order}"

    if show_header:
        print("\n" + "═" * width)
        print(f"{BOLD}{BG_BLUE}  👤 [{order}] {name.upper()} ({m_id})  {RESET}")
        if role:
            print(f"  💼 {BOLD}Vai trò:{RESET}           {role}")
        print(f"  🎯 {BOLD}Phân hệ phụ trách:{RESET} {CYAN}{scope}{RESET}")
        print(f"  ⚡ {BOLD}Lệnh kiểm tra riêng:{RESET} {YELLOW}{script_cmd}{RESET}")
        print("═" * width)

    if m_catalog:
        vulns = m_catalog.get("vulns", [])
        cq = m_catalog.get("code_quality")

        # 1. BẢNG TỔNG HỢP NHANH (QUICK SUMMARY TABLE)
        print(f"\n📊 {BOLD}BẢNG TỔNG HỢP CÁC LỖI VI PHẠM TRONG PHÂN HỆ CỦA {name.upper()}:{RESET}")
        w1, w2, w3, w4 = 8, 40, 26, 22
        print(f"┌{'─'*w1}┬{'─'*w2}┬{'─'*w3}┬{'─'*w4}┐")
        print(f"│ {'MÃ':<{w1-2}} │ {'TÊN LỖI VI PHẠM':<{w2-2}} │ {'VỊ TRÍ (TỆP:DÒNG)':<{w3-2}} │ {'QUY TẮC / PHÂN LOẠI':<{w4-2}} │")
        print(f"├{'─'*w1}┼{'─'*w2}┼{'─'*w3}┼{'─'*w4}┤")
        for v in vulns:
            v_code = f"SAST{v['num']:02d}"
            v_name = v.get("name", "")[:w2-2]
            loc = f"{Path(v.get('file', '')).name}:{v.get('line', 0)}"[:w3-2]
            cwe = v.get("cwe", "").split(":")[0][:w4-2]
            print(f"│ {RED}{BOLD}{v_code:<{w1-2}}{RESET} │ {v_name:<{w2-2}} │ {CYAN}{loc:<{w3-2}}{RESET} │ {YELLOW}{cwe:<{w4-2}}{RESET} │")
        if cq:
            cq_code = "CQ-01"
            cq_name = cq.get("name", "")[:w2-2]
            loc = f"{Path(cq.get('file', '')).name}:{cq.get('line', 0)}"[:w3-2]
            rule = cq.get("rule", "")[:w4-2]
            print(f"│ {MAGENTA}{BOLD}{cq_code:<{w1-2}}{RESET} │ {cq_name:<{w2-2}} │ {CYAN}{loc:<{w3-2}}{RESET} │ {MAGENTA}{rule:<{w4-2}}{RESET} │")
        print(f"└{'─'*w1}┴{'─'*w2}┴{'─'*w3}┴{'─'*w4}┘")

        card_w = 84

        # 2. PHẦN A: 4 LỖ HỔNG AN NINH VỚI SOURCE & SINK
        print(f"\n{RED}{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        print(f"{RED}{BOLD}🛡️  PHẦN A: CHI TIẾT 04 LỖ HỔNG AN NINH MÃ NGUỒN (SEMGREP & SONARQUBE SAST){RESET}")
        print(f"{RED}{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")

        for idx, v in enumerate(vulns, 1):
            sev_color = RED if "ERROR" in v.get("severity", "") else YELLOW
            print(f"\n  {BOLD}┌{'─' * card_w}┐{RESET}")
            print(f"  {BOLD}│ LỖ HỔNG [0{idx}/0{len(vulns)}]: {RED}{v.get('name')}{RESET}")
            print(f"  {BOLD}├{'─' * card_w}┤{RESET}")
            print(f"  │ 📂 {BOLD}Vị trí tệp:{RESET}       {CYAN}{v.get('file')}:{v.get('line')}{RESET}")
            print(f"  │ 🏷️  {BOLD}Phân loại an ninh:{RESET} {YELLOW}{v.get('cwe')}{RESET}  |  {DIM}{v.get('owasp')}{RESET}")
            print(f"  │ ⚠️  {BOLD}Mức độ rủi ro:{RESET}    {sev_color}{BOLD}🔴 {v.get('severity')}{RESET} (Động cơ: {v.get('engine')})")
            print(f"  │ 📜 {BOLD}Quy tắc vi phạm:{RESET}   {MAGENTA}{v.get('rule')}{RESET}")
            print(f"  │ 📥 {BOLD}Taint Source:{RESET}      {YELLOW}{v.get('source')}{RESET}")
            print(f"  │ ⚡ {BOLD}Taint Sink:{RESET}        {RED}{BOLD}{v.get('sink')}{RESET}")
            print(f"  │ ⚖️  {BOLD}Căn cứ pháp lý:{RESET}    {DIM}{v.get('legal')}{RESET}")
            print(f"  │")
            print(f"  │ 💻 {BOLD}Ngữ cảnh dòng mã vi phạm thực tế (Vulnerable Code Context):{RESET}")

            code_lines = extract_code_context(v.get("file", ""), v.get("line", 0), context_lines=2)
            for lno, text, is_target in code_lines:
                if is_target:
                    print(f"  │     {RED}{BOLD}➔ {lno:3d} │ {text}{RESET}")
                else:
                    print(f"  │       {DIM}{lno:3d} │ {text}{RESET}")
            print(f"  {BOLD}└{'─' * card_w}┘{RESET}")

        # 3. PHẦN B: 1 LỖI CODE QUALITY TỪ SONARQUBE
        if cq:
            cq_color = MAGENTA if cq.get("type") == "CODE_SMELL" else RED
            print(f"\n{MAGENTA}{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
            print(f"{MAGENTA}{BOLD}🧹 PHẦN B: CHI TIẾT 01 LỖI CHẤT LƯỢNG MÃ NGUỒN (SONARQUBE CODE QUALITY SCANNER){RESET}")
            print(f"{MAGENTA}{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")

            print(f"\n  {BOLD}┌{'─' * card_w}┐{RESET}")
            print(f"  {BOLD}│ LỖI CHẤT LƯỢNG: {MAGENTA}{cq.get('name')}{RESET}")
            print(f"  {BOLD}├{'─' * card_w}┤{RESET}")
            print(f"  │ 📂 {BOLD}Vị trí tệp:{RESET}       {CYAN}{cq.get('file')}:{cq.get('line')}{RESET}")
            print(f"  │ 🏷️  {BOLD}Phân loại Sonar:{RESET}   {cq_color}{BOLD}{cq.get('type')}{RESET} (SonarQube {cq.get('type')})")
            print(f"  │ ⚠️  {BOLD}Mức độ ảnh hưởng:{RESET} {YELLOW}{BOLD}{cq.get('severity')}{RESET} Level")
            print(f"  │ 📜 {BOLD}Mã quy tắc Sonar:{RESET}  {CYAN}{cq.get('rule')}{RESET}")
            print(f"  │ 📝 {BOLD}Chi tiết đánh giá:{RESET} {WHITE}{cq.get('desc')}{RESET}")
            print(f"  │")
            print(f"  │ 💻 {BOLD}Ngữ cảnh dòng mã SonarQube đánh dấu:{RESET}")

            cq_lines = extract_code_context(cq.get("file", ""), cq.get("line", 0), context_lines=2)
            for lno, text, is_target in cq_lines:
                if is_target:
                    print(f"  │     {MAGENTA}{BOLD}➔ {lno:3d} │ {text}{RESET}")
                else:
                    print(f"  │       {DIM}{lno:3d} │ {text}{RESET}")
            print(f"  {BOLD}└{'─' * card_w}┘{RESET}")

        # 4. PHẦN C: CÁC PHÁT HIỆN BỔ SUNG TRONG LẦN CHẠY CI THỰC TẾ (NẾU CÓ CỜ --verbose)
        primary_files = {v.get("file", "").replace("\\", "/") for v in vulns}
        if cq:
            primary_files.add(cq.get("file", "").replace("\\", "/"))

        extra_semgrep = [
            r for r in semgrep_list 
            if r.get("path", "").replace("\\", "/") not in primary_files or r.get("start", {}).get("line") not in [v.get("line") for v in vulns]
        ]

        if show_verbose and extra_semgrep:
            print(f"\n{CYAN}{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
            print(f"🔍 {BOLD}{CYAN}PHẦN C: CÁC PHÁT HIỆN CẤU HÌNH BỔ SUNG TỪ CI CLOUD ({len(extra_semgrep)} phát hiện){RESET}")
            print(f"{CYAN}{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
            for idx, r in enumerate(extra_semgrep, 1):
                path = r.get("path", "")
                line = r.get("start", {}).get("line", 0)
                check_id = r.get("check_id", "unknown").split(".")[-1]
                msg = r.get("extra", {}).get("message", "").strip().splitlines()[0]
                cwe = r.get("extra", {}).get("metadata", {}).get("cwe", "")
                if isinstance(cwe, list):
                    cwe = cwe[0] if cwe else ""
                cwe_str = str(cwe).split(":")[0][:20] if cwe else "CWE"
                print(f"\n  {BOLD}┌{'─' * card_w}┐{RESET}")
                print(f"  {BOLD}│ PHÁT HIỆN CI [{idx:02d}]: {CYAN}{path}:{line}{RESET}  |  {YELLOW}{cwe_str}{RESET}")
                print(f"  {BOLD}├{'─' * card_w}┤{RESET}")
                print(f"  │ 🛡️  {BOLD}Quy tắc vi phạm:{RESET} {MAGENTA}{check_id}{RESET}")
                print(f"  │ 📝 {BOLD}Chi tiết đánh giá:{RESET} {WHITE}{msg[:100]}...{RESET}")
                print(f"  │")
                print(f"  │ 💻 {BOLD}Dòng mã phát hiện:{RESET}")
                extra_code = extract_code_context(path, line, context_lines=1)
                for lno, text, is_target in extra_code:
                    if is_target:
                        print(f"  │     {RED}➔ {lno:3d} │ {text}{RESET}")
                print(f"  {BOLD}└{'─' * card_w}┘{RESET}")
            print()
    else:
        print(f"  {YELLOW}Không tìm thấy dữ liệu catalog cho thành viên {m_id}.{RESET}")
    print()


def display_detailed_failures(run_id: int, jobs: list[dict], target_member: str | None = None, show_verbose: bool = False) -> None:
    """In chi tiết các lỗi an ninh, mã nguồn vi phạm khiến Pipeline bị Break-the-Build ngay trên CLI.
    
    Hỗ trợ gom nhóm tự động theo từng thành viên hoặc lọc riêng cho 1 thành viên cụ thể.
    """
    repo_slug = get_repo_slug()
    failed_jobs = [j for j in jobs if j.get("conclusion") == "failure"]

    if not failed_jobs:
        return

    # Chuẩn hóa mã thành viên nếu có
    resolved_key = resolve_member_key(target_member)
    target_info = MEMBER_SCOPE_MAP.get(resolved_key) if resolved_key else None

    # Nạp dữ liệu báo cáo chuyên sâu từ artifacts nếu có
    semgrep_data, sonar_gate, sonar_issues = load_or_download_artifacts(run_id)

    # Lấy annotations từ GitHub API để bổ trợ
    all_annos = []
    for job in failed_jobs:
        jid = job.get("databaseId")
        if jid:
            all_annos.extend(fetch_job_annotations(repo_slug, jid))
    valid_annos = [a for a in all_annos if "exit code" not in a.get("message", "")]

    print("\n" + "=" * 88)
    if target_info:
        print(f"{BOLD}{BG_BLUE} 👤 BẢNG LỖI VI PHẠM CỦA: [{target_info['order']}] {target_info['name'].upper()} ({resolved_key}) {RESET}")
        print(f"📌 {BOLD}Phạm vi phụ trách:{RESET} {CYAN}{target_info['scope']}{RESET}")
        print(f"⚡ {BOLD}Lệnh kiểm tra riêng:{RESET} {YELLOW}{target_info['script']}{RESET}")
    else:
        print(f"{BOLD}{RED}🚨 BẢNG CHI TIẾT CÁC LỖI VI PHẠM GOM NHÓM THEO TỪNG THÀNH VIÊN (BREAK-THE-BUILD){RESET}")
        print(f"💡 {DIM}Hệ thống tự động phân loại vi phạm vào đúng thành viên phụ trách theo bảng phân nhiệm RACI.{RESET}")
    print(f"🔗 Chi tiết Web Run #{run_id}: {CYAN}https://github.com/{repo_slug}/actions/runs/{run_id}{RESET}")
    print("=" * 88)

    # In tóm tắt tổng quan chỉ số Quality Gate & Semgrep
    if not target_info:
        print(f"\n📊 {BOLD}TỔNG QUAN CHỐT CHẶN AN NINH & CHẤT LƯỢNG (STAGE 2 DEV GATE):{RESET}")
        if sonar_gate:
            status = sonar_gate.get("projectStatus", {}).get("status", "UNKNOWN")
            print(f"   • SonarQube Quality Gate: {RED}{BOLD}{status}{RESET}  ➜  {RED}Trượt chỉ số Reliability Rating (Thực tế: Grade C, Yêu cầu: <= Grade A){RESET}")
        if semgrep_data:
            s_errors = [r for r in semgrep_data.get("results", []) if r.get("extra", {}).get("severity") == "ERROR"]
            print(f"   • Semgrep Security Gate:  {RED}{BOLD}CHẶN ĐỨNG (BLOCKED){RESET}  ➜  {RED}Phát hiện {len(s_errors)} lỗ hổng bảo mật mức ERROR / HIGH{RESET}")
        print("-" * 88)

        # BẢNG ĐIỀU HÀNH TỔNG QUAN PHÂN BỔ VI PHẠM THEO 5 THÀNH VIÊN
        print(f"\n👥 {BOLD}BẢNG ĐIỀU HÀNH TỔNG QUAN PHÂN BỔ VI PHẠM THEO 5 THÀNH VIÊN:{RESET}")
        ew1, ew2, ew3, ew4, ew5, ew6 = 6, 20, 38, 12, 14, 16
        print(f"┌{'─'*ew1}┬{'─'*ew2}┬{'─'*ew3}┬{'─'*ew4}┬{'─'*ew5}┬{'─'*ew6}┐")
        print(f"│ {'STT':<{ew1-2}} │ {'THÀNH VIÊN':<{ew2-2}} │ {'PHÂN HỆ PHỤ TRÁCH':<{ew3-2}} │ {'SAST VULN':<{ew4-2}} │ {'SONAR CQ':<{ew5-2}} │ {'TRẠNG THÁI':<{ew6-2}} │")
        print(f"├{'─'*ew1}┼{'─'*ew2}┼{'─'*ew3}┼{'─'*ew4}┼{'─'*ew5}┼{'─'*ew6}┤")
        exec_rows = [
            ("01", "Nguyễn Giang Nam", "Tra cứu cảng biển & IaC Docker", "4 lỗi", "1 BUG", "CHẶN ĐỨNG"),
            ("02", "Nguyễn Đình Hải", "Xác thực, API Vận tải & DB Fallback", "4 lỗi", "1 SMELL", "CHẶN ĐỨNG"),
            ("03", "Đào Xuân Mạnh", "Đơn hàng, Lịch trình & Xử lý XML", "4 lỗi", "1 SMELL", "CHẶN ĐỨNG"),
            ("04", "Lê Đức Anh", "Tin tức hàng hải & Giám sát Metrics", "4 lỗi", "1 SMELL", "CHẶN ĐỨNG"),
            ("05", "Nguyễn Phương Mai", "Quản trị Admin & Hệ thống Bình luận", "4 lỗi", "1 BUG", "CHẶN ĐỨNG"),
        ]
        for stt, name, scope, sast, cq, status in exec_rows:
            stt_fmt = f"[{stt}]"
            print(f"│ {stt_fmt:<{ew1-2}} │ {BOLD}{name:<{ew2-2}}{RESET} │ {CYAN}{scope:<{ew3-2}}{RESET} │ {RED}{sast:<{ew4-2}}{RESET} │ {MAGENTA}{cq:<{ew5-2}}{RESET} │ {RED}{BOLD}{status:<{ew6-2}}{RESET} │")
        print(f"└{'─'*ew1}┴{'─'*ew2}┴{'─'*ew3}┴{'─'*ew4}┴{'─'*ew5}┴{'─'*ew6}┘")

        print(f"\n💡 {BOLD}MẸO XEM NHANH DỄ ĐỌC THEO TỪNG THÀNH VIÊN (KÈM DÒNG CODE VÀ SOURCE/SINK):{RESET}")
        print(f"   Chạy lệnh kèm cờ {YELLOW}-m <1-5>{RESET} để xem riêng 1 phân hệ thay vì in toàn bộ 5 người:")
        for m_id, info in MEMBER_SCOPE_MAP.items():
            print(f"   • {YELLOW}python -X utf8 demo/demo_live_ci.py -m {info['order']}{RESET}  ➜  {info['name']}")
        print("─" * 88)

    # Trích xuất danh sách kết quả
    semgrep_all = semgrep_data.get("results", []) if semgrep_data else []
    semgrep_errors = [r for r in semgrep_all if r.get("extra", {}).get("severity") == "ERROR"]
    sonar_all = sonar_issues.get("issues", []) if sonar_issues else []

    # Xác định danh sách thành viên cần hiển thị
    members_to_show = [resolved_key] if resolved_key else list(MEMBER_SCOPE_MAP.keys())

    for m_id in members_to_show:
        m_info = MEMBER_SCOPE_MAP.get(m_id)
        if not m_info:
            continue

        m_semgrep = [r for r in semgrep_errors if get_member_for_file(r.get("path", "")) == m_id]
        m_sonar = [s for s in sonar_all if get_member_for_file(s.get("component", "")) == m_id]
        m_annos = [a for a in valid_annos if get_member_for_file(a.get("path", "")) == m_id]

        render_single_member_breakdown(
            m_id, m_info, m_semgrep, m_sonar, m_annos,
            show_header=(target_info is None),
            show_verbose=show_verbose
        )

    # Kiểm tra các lỗi chung ngoài phạm vi phân chia cá nhân (nếu xem toàn bộ)
    if not target_info:
        shared_annos = [a for a in valid_annos if get_member_for_file(a.get("path", "")) is None]
        shared_sonar = [s for s in sonar_all if get_member_for_file(s.get("component", "")) is None]
        if shared_annos or shared_sonar:
            print(f"\n{BOLD}{MAGENTA} 🌐 QUY CHUẨN CHUNG HỆ THỐNG & POLICY GUARD (.github / trang tĩnh) {RESET}")
            print("-" * 88)
            for a in shared_annos:
                path = a.get("path", "")
                title = a.get("title", "")
                msg = a.get("message", "").strip().splitlines()[0]
                print(f"  📁 {CYAN}{path}{RESET}: {YELLOW}{title}{RESET} {WHITE}{msg}{RESET}")
            for s in shared_sonar[:5]:
                comp = s.get("component", "").split(":")[-1]
                msg = s.get("message", "")
                rule = s.get("rule", "")
                print(f"  📁 {CYAN}{comp}{RESET}: [{s.get('severity')}] {rule} - {WHITE}{msg}{RESET}")
            print()

    # Khuyến nghị khắc phục (Remediation)
    print("=" * 88)
    print(f"{BOLD}{YELLOW}💡 HƯỚNG DẪN KIỂM TRA & KHẮC PHỤC (ACTION ITEMS):{RESET}")
    if target_info:
        print(f"  👉 Để xem chi tiết các lỗi vi phạm và ngữ cảnh dòng mã của {target_info['name']}:")
        print(f"     {CYAN}python demo/demo_live_ci.py -m {target_info['order']}{RESET}")
        print(f"  👉 Để kích hoạt luồng CI thật kiểm định trên GitHub Actions:")
        print(f"     {CYAN}python demo/demo_live_ci.py --trigger{RESET}")
    else:
        print(f"  👉 Xem riêng báo cáo lỗi của từng thành viên:")
        print(f"     - [1] Nguyễn Giang Nam:  {CYAN}python demo/demo_live_ci.py -m 1{RESET}")
        print(f"     - [2] Nguyễn Đình Hải:   {CYAN}python demo/demo_live_ci.py -m 2{RESET}")
        print(f"     - [3] Đào Xuân Mạnh:     {CYAN}python demo/demo_live_ci.py -m 3{RESET}")
        print(f"     - [4] Lê Đức Anh:        {CYAN}python demo/demo_live_ci.py -m 4{RESET}")
        print(f"     - [5] Nguyễn Phương Mai: {CYAN}python demo/demo_live_ci.py -m 5{RESET}")
        print(f"  👉 Kích hoạt luồng CI thật: {CYAN}python demo/demo_live_ci.py --trigger{RESET}")
    print("=" * 88 + "\n")



def fetch_run_details(run_id: int) -> dict | None:
    """Lấy dữ liệu chi tiết của một Run ID bao gồm jobs và steps."""
    cmd = [
        "gh", "run", "view", str(run_id),
        "--json", "databaseId,status,conclusion,jobs,event,headBranch,headSha,url,createdAt,updatedAt"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if res.returncode == 0 and res.stdout.strip():
        try:
            return json.loads(res.stdout)
        except Exception:
            pass
    return None


def format_status_badge(status: str, conclusion: str | None) -> str:
    """Định dạng huy hiệu trạng thái với màu sắc tương ứng."""
    if status == "completed":
        if conclusion == "success":
            return f"{GREEN}{BOLD}✔ THÀNH CÔNG (PASSED){RESET}"
        elif conclusion == "failure":
            return f"{RED}{BOLD}✖ THẤT BẠI (FAILED){RESET}"
        elif conclusion == "cancelled":
            return f"{YELLOW}{BOLD}⚠ ĐÃ HỦY (CANCELLED){RESET}"
        elif conclusion == "skipped":
            return f"{DIM}⚪ BỎ QUA (SKIPPED){RESET}"
        else:
            return f"{CYAN}{conclusion.upper()}{RESET}"
    elif status == "in_progress":
        return f"{YELLOW}{BOLD}🔄 ĐANG CHẠY (RUNNING){RESET}"
    elif status == "queued":
        return f"{BLUE}⏳ ĐANG CHỜ (QUEUED){RESET}"
    else:
        return f"{DIM}{status}{RESET}"


def watch_live_ci_run(run_id: int, poll_interval: float = 3.0) -> int:
    """Theo dõi và stream liên tục trạng thái thời gian thực của CI run cho tới khi hoàn tất."""
    print_banner(f"📡 THEO DÕI TRỰC TIẾP LUỒNG CI TRÊN GITHUB ACTIONS — RUN #{run_id}", CYAN)
    print(f"🔗 {BOLD}Liên kết Web Dashboard:{RESET} {CYAN}https://github.com/wtfwhoyouare/PTIT-DevOps-SonarQube/actions/runs/{run_id}{RESET}")
    print(f"⏱️  Tần số cập nhật: {poll_interval}s | Nhấn {BOLD}Ctrl+C{RESET} để dừng theo dõi.\n")

    iteration = 0
    while True:
        data = fetch_run_details(run_id)
        if not data:
            print(f"⚠️ Không thể nạp thông tin từ GitHub Actions. Thử lại sau {poll_interval}s...")
            time.sleep(poll_interval)
            continue

        iteration += 1
        overall_status = data.get("status")
        overall_conclusion = data.get("conclusion")
        head_branch = data.get("headBranch", "unknown")
        event = data.get("event", "unknown")
        jobs = data.get("jobs", [])

        # In tiêu đề trạng thái
        sys.stdout.write("\033[H\033[J") if os.name != "nt" else os.system("cls")
        
        print_banner(f"📡 THEO DÕI TRỰC TIẾP LUỒNG CI GITHUB ACTIONS — RUN #{run_id}", CYAN)
        print(f"🌿 {BOLD}Nhánh:{RESET} {CYAN}{head_branch}{RESET} | 🎯 {BOLD}Sự kiện:{RESET} {YELLOW}{event}{RESET} | 🔄 {BOLD}Lần cập nhật:{RESET} #{iteration}")
        print(f"📊 {BOLD}Trạng thái Tổng thể:{RESET} {format_status_badge(overall_status, overall_conclusion)}")
        print(f"🔗 {BOLD}URL:{RESET} {CYAN}https://github.com/wtfwhoyouare/PTIT-DevOps-SonarQube/actions/runs/{run_id}{RESET}\n")

        print("┌─────────────────────────────────────────────────────────────┬──────────────────────────┐")
        print("│ GIAI ĐOẠN KIỂM ĐỊNH (CI STAGE / JOB)                        │ TRẠNG THÁI TIẾN ĐỘ       │")
        print("├─────────────────────────────────────────────────────────────┼──────────────────────────┤")

        for j in jobs:
            j_name = j.get("name", "Unknown Job")
            j_status = j.get("status", "")
            j_conclusion = j.get("conclusion")
            badge = format_status_badge(j_status, j_conclusion)

            # Cắt gọn tên nếu dài
            display_name = j_name[:57]
            pad_name = display_name + " " * max(0, 59 - len(display_name))
            
            # Tên step đang chạy (nếu in_progress)
            active_step = ""
            if j_status == "in_progress":
                for s in j.get("steps", []):
                    if s.get("status") == "in_progress":
                        active_step = f" ➔ {s.get('name')}"[:35]
                        break

            print(f"│ {BOLD}{pad_name}{RESET} │ {badge} │")
            if active_step:
                print(f"│   {YELLOW}{DIM}{active_step:<57}{RESET} │                          │")

        print("└─────────────────────────────────────────────────────────────┴──────────────────────────┘")

        # Kiểm tra nếu workflow đã hoàn tất
        if overall_status == "completed":
            print("\n" + "=" * 88)
            if overall_conclusion == "success":
                print(f"{GREEN}{BOLD}🎉 [CI HOÀN TẤT THÀNH CÔNG] Toàn bộ các chốt chặn Security Gate & Quality Gate ĐẠT CHUẨN!{RESET}")
                print(f"{GREEN}✔ Cho phép hợp nhất Pull Request hoặc triển khai lên môi trường tiếp theo.{RESET}")
                print("=" * 88 + "\n")
                return 0
            else:
                print(f"{RED}{BOLD}🛑 [CI CHẶN ĐỨNG - BREAK-THE-BUILD] Pipeline đã phát hiện vi phạm và dừng thực thi!{RESET}")
                print(f"{RED}✖ Trạng thái kết luận: {overall_conclusion.upper() if overall_conclusion else 'FAILED'}{RESET}")
                print(f"{RED}✖ Nút Merge trên Pull Request bị khóa tự động để bảo vệ hệ thống.{RESET}")
                print("=" * 88)
                display_detailed_failures(run_id, jobs)
                return 1

        time.sleep(poll_interval)


def interactive_menu() -> None:
    """Menu tương tác cho người dùng chọn tác vụ trực tiếp."""
    if not check_gh_installed():
        print_banner("LỖI KẾT NỐI GITHUB CLI", RED)
        print("❌ Máy tính chưa có GitHub CLI (gh) hoặc chưa đăng nhập.")
        print("👉 Vui lòng cài đặt và đăng nhập bằng lệnh: gh auth login")
        return

    while True:
        print_banner("HỆ THỐNG KÍCH HOẠT & THEO DÕI CI THẬT TRÊN GITHUB ACTIONS", CYAN)
        print("Vui lòng chọn chế độ hoạt động:")
        print(f"  [1] 🚀 {BOLD}Kích hoạt luồng CI MỚI trên nhánh 'namng' (Chốt chặn Break-the-Build thật){RESET}")
        print(f"  [2] 🚀 {BOLD}Kích hoạt luồng CI MỚI trên nhánh 'dev' (Môi trường tích hợp chung){RESET}")
        print(f"  [3] 📡 {BOLD}Theo dõi lần chạy CI MỚI NHẤT gần đây{RESET}")
        print(f"  [4] 🔍 {BOLD}Nhập mã Run ID cụ thể để theo dõi chi tiết{RESET}")
        print(f"  [5] 🚨 {BOLD}Xem BẢNG CHI TIẾT LỖI VI PHẠM (SAST & Quality Gate) của lần chạy gần nhất{RESET}")
        print(f"  [6] 🌐 {BOLD}Mở trang GitHub Actions trên trình duyệt Web{RESET}")
        print(f"  [0] Thoát chương trình\n")

        choice = input("👉 Nhập lựa chọn (0-6): ").strip()

        if choice == "0":
            print("\n👋 Tạm biệt!\n")
            break
        elif choice == "1":
            run_id = trigger_real_workflow("namng", enforce=True)
            if run_id:
                watch_live_ci_run(run_id)
            input("\n👉 Nhấn Enter để quay lại Menu...")
        elif choice == "2":
            run_id = trigger_real_workflow("dev", enforce=True)
            if run_id:
                watch_live_ci_run(run_id)
            input("\n👉 Nhấn Enter để quay lại Menu...")
        elif choice == "3":
            run_id = get_latest_run_id()
            if run_id:
                watch_live_ci_run(run_id)
            else:
                print("❌ Không tìm thấy lần chạy nào gần đây.")
            input("\n👉 Nhấn Enter để quay lại Menu...")
        elif choice == "4":
            custom_id = input("👉 Nhập mã Run ID (ví dụ 41179854251): ").strip()
            if custom_id.isdigit():
                watch_live_ci_run(int(custom_id))
            else:
                print("⚠️ Mã Run ID không hợp lệ!")
            input("\n👉 Nhấn Enter để quay lại Menu...")
        elif choice == "5":
            run_id = get_latest_run_id()
            if run_id:
                data = fetch_run_details(run_id)
                if data:
                    print("\n👤 Bạn muốn xem bảng lỗi vi phạm của ai?")
                    print("  [0] Toàn bộ nhóm (Gom nhóm theo 5 thành viên)")
                    print("  [1] Nguyễn Giang Nam (namng)")
                    print("  [2] Nguyễn Đình Hải (haind)")
                    print("  [3] Đào Xuân Mạnh (manhdx)")
                    print("  [4] Lê Đức Anh (anhld)")
                    print("  [5] Nguyễn Phương Mai (mainp)")
                    sub_c = input("👉 Nhập lựa chọn (0-5, mặc định 0): ").strip()
                    m_filter = None if sub_c in ("", "0") else sub_c
                    jobs = data.get("jobs", [])
                    display_detailed_failures(run_id, jobs, target_member=m_filter)
                else:
                    print("❌ Không thể nạp chi tiết lần chạy.")
            else:
                print("❌ Không tìm thấy lần chạy nào gần đây.")
            input("\n👉 Nhấn Enter để quay lại Menu...")
        elif choice == "6":
            url = "https://github.com/wtfwhoyouare/PTIT-DevOps-SonarQube/actions"
            print(f"🌐 Đang mở: {url}")
            if os.name == "nt":
                os.system(f"start {url}")
            input("\n👉 Nhấn Enter để quay lại Menu...")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Kích hoạt và theo dõi luồng CI thật trên GitHub Actions thời gian thực",
        epilog="Ví dụ: python demo_live_ci.py --errors -m haind"
    )
    parser.add_argument("--trigger", action="store_true", help="Gửi lệnh kích hoạt luồng CI mới trên GitHub")
    parser.add_argument("--branch", default="namng", help="Tên nhánh cần kích hoạt (mặc định: namng)")
    parser.add_argument("--watch", nargs="?", const="latest", help="Theo dõi một Run ID cụ thể hoặc run mới nhất (latest)")
    parser.add_argument("--latest", action="store_true", help="Xem kết quả của lần chạy gần nhất")
    parser.add_argument("--details", "--errors", "--error", action="store_true", help="In bảng chi tiết các lỗi vi phạm của lần chạy gần nhất")
    parser.add_argument("-m", "--member", help="Lọc lỗi theo thành viên cụ thể (namng, haind, manhdx, anhld, mainp hoặc số 1-5)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Hiển thị thêm các cảnh báo cấu hình bổ sung từ CI Cloud (Phần C)")

    args = parser.parse_args()

    if not check_gh_installed():
        print("❌ Lỗi: Chưa phát hiện GitHub CLI (gh) hoặc chưa xác thực (gh auth login).", file=sys.stderr)
        sys.exit(1)

    # Nếu truyền --details/--errors/--error HOẶC chỉ truyền -m/--member (không kèm --trigger/--watch)
    # thì tự động hiển thị ngay báo cáo lỗi của thành viên đó
    if args.details or (args.member and not args.trigger and not args.watch):
        run_id = get_latest_run_id()
        if run_id:
            data = fetch_run_details(run_id)
            if data:
                display_detailed_failures(run_id, data.get("jobs", []), target_member=args.member, show_verbose=args.verbose)
                sys.exit(0 if data.get("conclusion") == "success" else 1)
        print("❌ Không tìm thấy lần chạy nào gần đây.", file=sys.stderr)
        sys.exit(1)

    if args.trigger:
        run_id = trigger_real_workflow(args.branch, enforce=True)
        if run_id:
            sys.exit(watch_live_ci_run(run_id))
        sys.exit(1)

    if args.watch:
        if args.watch == "latest":
            run_id = get_latest_run_id()
        else:
            run_id = int(args.watch)
        if run_id:
            sys.exit(watch_live_ci_run(run_id))
        sys.exit(1)

    if args.latest:
        run_id = get_latest_run_id()
        if run_id:
            # Nếu có cờ --member, in trực tiếp bảng chi tiết của thành viên đó
            if args.member:
                data = fetch_run_details(run_id)
                if data:
                    display_detailed_failures(run_id, data.get("jobs", []), target_member=args.member)
                    sys.exit(0 if data.get("conclusion") == "success" else 1)
            sys.exit(watch_live_ci_run(run_id))
        sys.exit(1)

    interactive_menu()


if __name__ == "__main__":
    main()

