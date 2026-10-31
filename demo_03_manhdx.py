"""Kịch bản Demo CI/CD Pipeline & Chốt chặn Bảo mật & Chất lượng cho Kỹ sư Đào Xuân Mạnh (manhdx).

========================================================================================
THÔNG TIN THÀNH VIÊN VÀ PHÂN HỆ PHỤ TRÁCH:
- Kỹ sư thực hiện: Đào Xuân Mạnh (Mã nhánh: manhdx)
- Vai trò trong dự án: Kỹ sư Kiểm định Chất lượng & Bảo mật (QA / DevSecOps Engineer)
- Phân hệ phụ trách: Kiểm soát Quality Gate, Module Cẩm nang Hàng hải & Hệ thống Kết xuất Báo cáo
- Nhánh phát triển: feature/manhdx-guide-export ➔ Hợp nhất vào nhánh: dev

A. DANH MỤC 4 LỖ HỔNG AN NINH MÃ NGUỒN (SAST VULNERABILITIES):
1. Local File Inclusion (Path Traversal)     [CWE-22] tại InlaneWeb/web/src/pages/guide.php:54
2. PHP Stream Wrapper Inclusion             [CWE-98] tại InlaneWeb/web/src/pages/guide.php:56
3. Arbitrary File Read via LOAD_FILE        [CWE-89/22] tại InlaneWeb/web/src/pages/report_download.php:36
4. DDL SQL Injection (Báo cáo Quản trị)     [CWE-89] tại InlaneWeb/web/src/pages/admin_report_export.php:27

B. DANH MỤC 01 LỖI CHẤT LƯỢNG MÃ NGUỒN SONARQUBE (CODE QUALITY ISSUE):
5. Use 'include_once' Instead of 'include'  [BUG | MINOR] Rule: php:S2003 tại guide.php:56
   (Nạp lặp tệp gây nguy cơ lỗi fatal error Cannot redeclare function/class và rò rỉ bộ nhớ)

CÁC CHẾ ĐỘ THỰC THI (COMMAND LINE ARGUMENTS):
- python demo_03_manhdx.py --real    : Thực thi trực tiếp các Engine CI thật (Policy Guard, Semgrep Gate, IaC Validator).
- python demo_03_manhdx.py --cloud   : Kết nối GitHub CLI để kiểm tra trạng thái CI thật trên GitHub Actions.
- python demo_03_manhdx.py           : Chạy mô phỏng có hiệu ứng trễ, phát hiện lỗi và CHẶN ĐỨNG (Exit code 1).
- python demo_03_manhdx.py --real    : Thực thi trực tiếp các Engine CI thật (Policy Guard, Semgrep Gate, IaC Validator).
- python demo_03_manhdx.py --cloud   : Kết nối GitHub CLI để kiểm tra trạng thái CI thật trên GitHub Actions.
- python demo_03_manhdx.py --fast    : Chạy nhanh không chờ độ trễ hiệu ứng terminal.
- python demo_03_manhdx.py --real    : Thực thi trực tiếp các Engine CI thật (Policy Guard, Semgrep Gate, IaC Validator).
- python demo_03_manhdx.py --cloud   : Kết nối GitHub CLI để kiểm tra trạng thái CI thật trên GitHub Actions.
- python demo_03_manhdx.py --fix     : Chạy kịch bản sau khi áp dụng mã an toàn đã khắc phục (Exit code 0).
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
    # 1. Phân tích các tham số dòng lệnh
    remediate = "--fix" in sys.argv or "--remediate" in sys.argv
    fast = "--fast" in sys.argv

    # 2. Khởi chạy tiến trình CI mô phỏng cho thành viên 'manhdx':
    # - Bước 1: Policy Guard kiểm tra tiêu đề PR "[manhdx] feat(guide)..." & Conventional Commits.
    # - Bước 2: Semgrep & SonarQube quét:
    #           + 4 Lỗ hổng an ninh mã nguồn (LFI, Stream Wrapper, LOAD_FILE, DDL SQLi)
    #           + 1 Lỗi chất lượng mã nguồn SonarQube (php:S2003 - Reliability Bug)
    # - Bước 3: SonarQube Quality Gate & Semgrep Gate kích hoạt BREAK-THE-BUILD, ngắt CI với code 1.
    real = "--real" in sys.argv or "--live" in sys.argv
    cloud = "--cloud" in sys.argv

    exit_code = run_member_demo("manhdx", remediate=remediate, fast=fast, real=real, cloud=cloud)

    # 3. Kịch bản tương tác tại buổi báo cáo:
    if not remediate and not fast and not cloud and sys.stdin.isatty():
        try:
            prompt = input("\n💡 Bạn có muốn demo kịch bản KHẮC PHỤC (Remediation) để CI thông qua không? (y/N): ").strip().lower()
            if prompt in ("y", "yes"):
                # Quét lại sau khi khắc phục cả lỗ hổng và lỗi chất lượng mã nguồn
                run_member_demo("manhdx", remediate=True, fast=False, real=real)
        except (KeyboardInterrupt, EOFError):
            pass

    # 4. Trả về mã thoát (exit code 1 khi bị chặn, code 0 khi pass)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
