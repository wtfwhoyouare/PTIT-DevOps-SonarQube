"""Kịch bản Demo CI/CD Pipeline & Chốt chặn Bảo mật & Chất lượng cho Kỹ sư Nguyễn Phương Mai (mainp).

========================================================================================
THÔNG TIN THÀNH VIÊN VÀ PHÂN HỆ PHỤ TRÁCH:
- Kỹ sư thực hiện: Nguyễn Phương Mai (Mã nhánh: mainp)
- Vai trò trong dự án: Kỹ sư Quản trị Rủi ro & An ninh Dữ liệu (Security Governance Specialist)
- Phân hệ phụ trách: Hệ thống Bình luận Tương tác Đối tác, Module Quản trị Admin & Tuân thủ Luật
- Nhánh phát triển: feature/mainp-comments-admin ➔ Hợp nhất vào nhánh: dev

A. DANH MỤC 4 LỖ HỔNG AN NINH MÃ NGUỒN (SAST VULNERABILITIES):
1. INSERT Statement SQL Injection             [CWE-89] tại InlaneWeb/web/src/pages/comment_add.php:19
2. DELETE Statement SQL Injection             [CWE-89] tại InlaneWeb/web/src/pages/comment_delete.php:18
3. Reflected XSS (Link Injection)              [CWE-79] tại InlaneWeb/web/src/pages/comment_add.php:29
4. Admin Console Multi-Statement Stacked SQLi  [CWE-89] tại InlaneWeb/web/src/pages/admin_console.php:33

B. DANH MỤC 01 LỖI CHẤT LƯỢNG MÃ NGUỒN SONARQUBE (CODE QUALITY ISSUE):
5. Admin Filter Input Without Associated Label [BUG | MAJOR] Rule: Web:InputWithoutLabelCheck tại admin_dashboard.php:26
   (Ô lọc dữ liệu quản trị thiếu nhãn label và id, vi phạm tiêu chuẩn Code Quality và Trợ năng)

CĂN CỨ PHÁP LÝ & TUÂN THỦ:
- Nghị định 13/2023/NĐ-CP (Điều 9, 13, 17, 26 - Nghĩa vụ bảo vệ CSDL & báo cáo sự cố 72 giờ).
- GDPR (Article 32 & 33 - Nghĩa vụ bảo đảm an ninh kỹ thuật và thông báo vi phạm dữ liệu).

CÁC CHẾ ĐỘ THỰC THI (COMMAND LINE ARGUMENTS):
- python demo_05_mainp.py --real    : Thực thi trực tiếp các Engine CI thật (Policy Guard, Semgrep Gate, IaC Validator).
- python demo_05_mainp.py --cloud   : Kết nối GitHub CLI để kiểm tra trạng thái CI thật trên GitHub Actions.
- python demo_05_mainp.py           : Chạy mô phỏng có hiệu ứng trễ, phát hiện lỗi và CHẶN ĐỨNG (Exit code 1).
- python demo_05_mainp.py --real    : Thực thi trực tiếp các Engine CI thật (Policy Guard, Semgrep Gate, IaC Validator).
- python demo_05_mainp.py --cloud   : Kết nối GitHub CLI để kiểm tra trạng thái CI thật trên GitHub Actions.
- python demo_05_mainp.py --fast    : Chạy nhanh không chờ độ trễ hiệu ứng terminal.
- python demo_05_mainp.py --real    : Thực thi trực tiếp các Engine CI thật (Policy Guard, Semgrep Gate, IaC Validator).
- python demo_05_mainp.py --cloud   : Kết nối GitHub CLI để kiểm tra trạng thái CI thật trên GitHub Actions.
- python demo_05_mainp.py --fix     : Chạy kịch bản sau khi áp dụng mã an toàn đã khắc phục (Exit code 0).
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

    # 2. Khởi chạy tiến trình CI mô phỏng cho thành viên 'mainp':
    # - Bước 1: Policy Guard kiểm tra tiêu đề PR "[mainp] feat(comments)..." & Conventional Commits.
    # - Bước 2: Semgrep & SonarQube quét:
    #           + 4 Lỗ hổng an ninh mã nguồn (INSERT/DELETE SQLi, XSS link injection, Stacked SQLi)
    #           + 1 Lỗi chất lượng mã nguồn SonarQube (Web:InputWithoutLabelCheck - Web Usability Bug)
    # - Bước 3: Đánh giá Dual Security & Quality Gate -> kích hoạt BREAK-THE-BUILD, ngắt CI với code 1.
    real = "--real" in sys.argv or "--live" in sys.argv
    cloud = "--cloud" in sys.argv

    exit_code = run_member_demo("mainp", remediate=remediate, fast=fast, real=real, cloud=cloud)

    # 3. Kịch bản tương tác tại buổi báo cáo:
    if not remediate and not fast and not cloud and sys.stdin.isatty():
        try:
            prompt = input("\n💡 Bạn có muốn demo kịch bản KHẮC PHỤC (Remediation) để CI thông qua không? (y/N): ").strip().lower()
            if prompt in ("y", "yes"):
                # Quét lại sau khi khắc phục cả lỗ hổng và lỗi chất lượng mã nguồn
                run_member_demo("mainp", remediate=True, fast=False, real=real)
        except (KeyboardInterrupt, EOFError):
            pass

    # 4. Trả về mã thoát (exit code 1 khi bị chặn, code 0 khi pass)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
