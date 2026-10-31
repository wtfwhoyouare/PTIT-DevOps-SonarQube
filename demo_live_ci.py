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
            print("\n" + "=" * 82)
            if overall_conclusion == "success":
                print(f"{GREEN}{BOLD}🎉 [CI HOÀN TẤT THÀNH CÔNG] Toàn bộ các chốt chặn Security Gate & Quality Gate ĐẠT CHUẨN!{RESET}")
                print(f"{GREEN}✔ Cho phép hợp nhất Pull Request hoặc triển khai lên môi trường tiếp theo.{RESET}")
                print("=" * 82 + "\n")
                return 0
            else:
                print(f"{RED}{BOLD}🛑 [CI CHẶN ĐỨNG - BREAK-THE-BUILD] Pipeline đã phát hiện vi phạm và dừng thực thi!{RESET}")
                print(f"{RED}✖ Trạng thái kết luận: {overall_conclusion.upper() if overall_conclusion else 'FAILED'}{RESET}")
                print(f"{RED}✖ Nút Merge trên Pull Request bị khóa tự động để bảo vệ hệ thống.{RESET}")
                print("=" * 82 + "\n")
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
        print(f"  [5] 🌐 {BOLD}Mở trang GitHub Actions trên trình duyệt Web{RESET}")
        print(f"  [0] Thoát chương trình\n")

        choice = input("👉 Nhập lựa chọn (0-5): ").strip()

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
            custom_id = input("👉 Nhập mã Run ID (ví dụ 41179102416): ").strip()
            if custom_id.isdigit():
                watch_live_ci_run(int(custom_id))
            else:
                print("⚠️ Mã Run ID không hợp lệ!")
            input("\n👉 Nhấn Enter để quay lại Menu...")
        elif choice == "5":
            url = "https://github.com/wtfwhoyouare/PTIT-DevOps-SonarQube/actions"
            print(f"🌐 Đang mở: {url}")
            if os.name == "nt":
                os.system(f"start {url}")
            input("\n👉 Nhấn Enter để quay lại Menu...")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Kích hoạt và theo dõi luồng CI thật trên GitHub Actions thời gian thực",
        epilog="Ví dụ: python demo_live_ci.py --trigger --branch dev"
    )
    parser.add_argument("--trigger", action="store_true", help="Gửi lệnh kích hoạt luồng CI mới trên GitHub")
    parser.add_argument("--branch", default="namng", help="Tên nhánh cần kích hoạt (mặc định: namng)")
    parser.add_argument("--watch", nargs="?", const="latest", help="Theo dõi một Run ID cụ thể hoặc run mới nhất (latest)")
    parser.add_argument("--latest", action="store_true", help="Xem kết quả của lần chạy gần nhất")

    args = parser.parse_args()

    if not check_gh_installed():
        print("❌ Lỗi: Chưa phát hiện GitHub CLI (gh) hoặc chưa xác thực (gh auth login).", file=sys.stderr)
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
            sys.exit(watch_live_ci_run(run_id))
        sys.exit(1)

    interactive_menu()


if __name__ == "__main__":
    main()

