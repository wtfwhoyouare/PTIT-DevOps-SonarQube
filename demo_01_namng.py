"""Kịch bản Demo CI/CD Pipeline & Chốt chặn Bảo mật & Chất lượng cho Trưởng nhóm Nguyễn Giang Nam (namng).

========================================================================================
THÔNG TIN THÀNH VIÊN VÀ PHÂN HỆ PHỤ TRÁCH:
- Kỹ sư thực hiện: Nguyễn Giang Nam (Mã nhánh: namng)
- Vai trò trong dự án: Trưởng nhóm — Kiến trúc sư DevSecOps (Lead Architect)
- Phân hệ phụ trách: Cổng thông tin công cộng, Quản lý quy chuẩn phân nhánh & Tra cứu cảng biển
- Nhánh phát triển: feature/namng-ports-public ➔ Hợp nhất vào nhánh: dev

A. DANH MỤC 4 LỖ HỔNG AN NINH MÃ NGUỒN (SAST VULNERABILITIES):
1. In-band UNION SQL Injection          [CWE-89] tại InlaneWeb/web/src/pages/ports.php:38
2. Reflected Cross-Site Scripting (XSS) [CWE-79] tại InlaneWeb/web/src/pages/ports.php:26
3. Numeric UNION SQL Injection          [CWE-89] tại InlaneWeb/web/src/pages/news.php:17
4. Hardcoded Database Root Password     [CWE-798] tại InlaneWeb/docker-compose.yml:17

B. DANH MỤC 01 LỖI CHẤT LƯỢNG MÃ NGUỒN SONARQUBE (CODE QUALITY ISSUE):
5. Input Control Missing Label & ID     [BUG | MAJOR] Rule: Web:InputWithoutLabelCheck tại ports.php:26
   (Ô tìm kiếm cảng biển thiếu ID và thẻ label gắn kết, vi phạm tiêu chuẩn trợ năng WCAG 2.1)

CÁC CHẾ ĐỘ THỰC THI (COMMAND LINE ARGUMENTS):
- python demo_01_namng.py           : Chạy mô phỏng có hiệu ứng trễ, phát hiện lỗi và CHẶN ĐỨNG (Exit code 1).
- python demo_01_namng.py --fast    : Chạy nhanh không chờ độ trễ hiệu ứng terminal.
- python demo_01_namng.py --fix     : Chạy kịch bản sau khi áp dụng mã an toàn đã khắc phục (Exit code 0).
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
    # 1. Phân tích các cờ điều khiển dòng lệnh
    # --fix / --remediate: Chế độ demo mã nguồn đã được sửa an toàn
    remediate = "--fix" in sys.argv or "--remediate" in sys.argv
    # --fast: Bỏ qua thời gian chờ hiệu ứng để chạy kết quả ngay lập tức
    fast = "--fast" in sys.argv

    # 2. Khởi chạy tiến trình CI mô phỏng cho trưởng nhóm 'namng':
    # - Bước 1: Policy Guard xác thực phân quyền RACI, format PR `[namng] feat(ports): ...` & Conventional Commits.
    # - Bước 2: Semgrep Taint Engine & SonarQube phân tích:
    #           + 4 Lỗ hổng an ninh mã nguồn (SQLi, XSS, Hardcoded Password)
    #           + 1 Lỗi chất lượng mã nguồn SonarQube (Web:InputWithoutLabelCheck)
    # - Bước 3: Đánh giá Dual Security & Quality Gate -> kích hoạt BREAK-THE-BUILD, ngắt CI với code 1.
    exit_code = run_member_demo("namng", remediate=remediate, fast=fast)

    # 3. Kịch bản tương tác tại buổi báo cáo:
    # Cho phép người báo cáo bấm phím 'y' để trình diễn kết quả sau khi vá lỗi ngay tại chỗ mà không cần gõ lại lệnh.
    if not remediate and not fast and sys.stdin.isatty():
        try:
            prompt = input("\n💡 Bạn có muốn demo kịch bản KHẮC PHỤC (Remediation) để CI thông qua không? (y/N): ").strip().lower()
            if prompt in ("y", "yes"):
                # Quét lại sau khi khắc phục cả lỗ hổng và lỗi chất lượng mã nguồn
                run_member_demo("namng", remediate=True, fast=False)
        except (KeyboardInterrupt, EOFError):
            pass

    # 4. Trả về mã thoát (exit code 1 khi bị chặn, code 0 khi pass)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
