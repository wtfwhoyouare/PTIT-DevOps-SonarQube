"""Kịch bản Demo CI/CD Pipeline & Chốt chặn Bảo mật & Chất lượng cho Kỹ sư Lê Đức Anh (anhld).

========================================================================================
THÔNG TIN THÀNH VIÊN VÀ PHÂN HỆ PHỤ TRÁCH:
- Kỹ sư thực hiện: Lê Đức Anh (Mã nhánh: anhld)
- Vai trò trong dự án: Kỹ sư Tự động hóa Hạ tầng & Cấu hình An toàn (Platform Security Engineer)
- Phân hệ phụ trách: Quản lý Tài khoản & Hồ sơ Đối tác, Theo dõi Vận tải & An toàn Cấu hình IaC
- Nhánh phát triển: feature/anhld-account-iac ➔ Hợp nhất vào nhánh: dev

A. DANH MỤC 4 LỖ HỔNG AN NINH MÃ NGUỒN (SAST VULNERABILITIES):
1. Order-By Clause SQL Injection              [CWE-89] tại InlaneWeb/web/src/pages/account.php:41
2. UPDATE Statement SQL Injection             [CWE-89] tại InlaneWeb/web/src/pages/account_update.php:20
3. Numeric Shipment Detail SQL Injection       [CWE-89] tại InlaneWeb/web/src/pages/shipment_detail.php:15
4. Hardcoded Root Password trong Prod Compose [CWE-798] tại InlaneWeb/docker-compose.prod.yml:15

B. DANH MỤC 01 LỖI CHẤT LƯỢNG MÃ NGUỒN SONARQUBE (CODE QUALITY ISSUE):
5. Label Not Associated With Input Control    [CODE_SMELL | MAJOR] Rule: Web:S6853 tại account.php:28
   (Thẻ label không có thuộc tính for gắn kết trực tiếp với id của input, vi phạm ISO/IEC 40500)

CÁC CHẾ ĐỘ THỰC THI (COMMAND LINE ARGUMENTS):
- python demo_04_anhld.py           : Chạy mô phỏng có hiệu ứng trễ, phát hiện lỗi và CHẶN ĐỨNG (Exit code 1).
- python demo_04_anhld.py --fast    : Chạy nhanh không chờ độ trễ hiệu ứng terminal.
- python demo_04_anhld.py --fix     : Chạy kịch bản sau khi áp dụng mã an toàn đã khắc phục (Exit code 0).
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

    # 2. Khởi chạy tiến trình CI mô phỏng cho thành viên 'anhld':
    # - Bước 1: Policy Guard kiểm tra tiêu đề PR "[anhld] feat(account)..." & Conventional Commits.
    # - Bước 2: Semgrep & SonarQube quét:
    #           + 4 Lỗ hổng an ninh mã nguồn (Order-by SQLi, Update SQLi, Shipment SQLi, Hardcoded Prod Pass)
    #           + 1 Lỗi chất lượng mã nguồn SonarQube (Web:S6853 - Accessibility Code Smell)
    # - Bước 3: Đánh giá Dual Security & Quality Gate -> kích hoạt BREAK-THE-BUILD, ngắt CI với code 1.
    exit_code = run_member_demo("anhld", remediate=remediate, fast=fast)

    # 3. Kịch bản tương tác tại buổi báo cáo:
    if not remediate and not fast and sys.stdin.isatty():
        try:
            prompt = input("\n💡 Bạn có muốn demo kịch bản KHẮC PHỤC (Remediation) để CI thông qua không? (y/N): ").strip().lower()
            if prompt in ("y", "yes"):
                # Quét lại sau khi khắc phục cả lỗ hổng và lỗi chất lượng mã nguồn
                run_member_demo("anhld", remediate=True, fast=False)
        except (KeyboardInterrupt, EOFError):
            pass

    # 4. Trả về mã thoát (exit code 1 khi bị chặn, code 0 khi pass)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
