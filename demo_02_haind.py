"""Kịch bản Demo CI/CD Pipeline & Chốt chặn Bảo mật & Chất lượng cho Kỹ sư Nguyễn Đình Hải (haind).

========================================================================================
THÔNG TIN THÀNH VIÊN VÀ PHÂN HỆ PHỤ TRÁCH:
- Kỹ sư thực hiện: Nguyễn Đình Hải (Mã nhánh: haind)
- Vai trò trong dự án: Kỹ sư An ninh Phần mềm (Application Security Engineer)
- Phân hệ phụ trách: Kiểm định Taint Analysis, Module Xác thực người dùng & Theo dõi Vận đơn
- Nhánh phát triển: feature/haind-auth-tracking ➔ Hợp nhất vào nhánh: dev

A. DANH MỤC 4 LỖ HỔNG AN NINH MÃ NGUỒN (SAST VULNERABILITIES):
1. Authentication Bypass SQL Injection   [CWE-89] tại InlaneWeb/web/src/pages/login.php:19
2. XPath Error-based SQL Injection      [CWE-89] tại InlaneWeb/web/src/pages/port_detail.php:19
3. Time-based Blind SQL Injection       [CWE-89] tại InlaneWeb/web/src/pages/track_api.php:18
4. Hardcoded DB Password Fallback       [CWE-798] tại InlaneWeb/web/src/lib/db.php:19

B. DANH MỤC 01 LỖI CHẤT LƯỢNG MÃ NGUỒN SONARQUBE (CODE QUALITY ISSUE):
5. Missing Curly Braces in Nested Stmt   [CODE_SMELL | CRITICAL] Rule: php:S121 tại login.php:36
   (Khối lệnh if lồng không có ngoặc nhọn { }, vi phạm chuẩn Clean Code PSR-12)

CÁC CHẾ ĐỘ THỰC THI (COMMAND LINE ARGUMENTS):
- python demo_02_haind.py           : Chạy mô phỏng có hiệu ứng trễ, phát hiện lỗi và CHẶN ĐỨNG (Exit code 1).
- python demo_02_haind.py --fast    : Chạy nhanh không chờ độ trễ hiệu ứng terminal.
- python demo_02_haind.py --fix     : Chạy kịch bản sau khi áp dụng mã an toàn đã khắc phục (Exit code 0).
========================================================================================
"""

from __future__ import annotations

import os
from pathlib import Path
import sys

# Đảm bảo thư mục gốc của repository nằm trong sys.path để nạp module nội bộ
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Nạp động cơ mô phỏng luồng CI và chốt chặn an ninh
from ci.demo_runner import run_member_demo


def main() -> None:
    # 1. Phân tích các tham số dòng lệnh điều khiển kịch bản
    remediate = "--fix" in sys.argv or "--remediate" in sys.argv
    fast = "--fast" in sys.argv

    # 2. Khởi chạy tiến trình CI mô phỏng cho thành viên 'haind':
    # - Bước 1: Policy Guard kiểm tra tiêu đề PR "[haind] feat(auth)..." & Conventional Commits.
    # - Bước 2: Semgrep & SonarQube quét:
    #           + 4 Lỗ hổng an ninh mã nguồn (Auth SQLi, XPath SQLi, Blind SQLi, Hardcoded Fallback)
    #           + 1 Lỗi chất lượng mã nguồn SonarQube (php:S121 - Clean Code Smell)
    # - Bước 3: Đánh giá Dual Security & Quality Gate -> kích hoạt BREAK-THE-BUILD và trả về code 1.
    exit_code = run_member_demo("haind", remediate=remediate, fast=fast)

    # 3. Kịch bản tương tác tại buổi báo cáo:
    if not remediate and not fast and sys.stdin.isatty():
        try:
            prompt = input("\n💡 Bạn có muốn demo kịch bản KHẮC PHỤC (Remediation) để CI thông qua không? (y/N): ").strip().lower()
            if prompt in ("y", "yes"):
                # Quét lại sau khi khắc phục cả lỗ hổng và lỗi chất lượng mã nguồn
                run_member_demo("haind", remediate=True, fast=False)
        except (KeyboardInterrupt, EOFError):
            pass

    # 4. Trả về mã thoát (exit code 1 khi bị chặn, code 0 khi pass)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
