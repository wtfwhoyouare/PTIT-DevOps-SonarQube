"""Bảng điều khiển tổng hợp Master DevSecOps CI/CD Demo CLI.

Script này đóng vai trò bộ điều hướng trung tâm (Hub) phục vụ buổi báo cáo đề tài:
- Cho phép người thuyết trình chọn demo riêng lẻ từng thành viên (từ 1 đến 5).
- Cho phép chạy toàn bộ (Showcase All 5 Members) theo thứ tự thuyết trình.
- Hỗ trợ các cờ dòng lệnh linh hoạt để chạy trực tiếp từ terminal.

CÁC CÚ PHÁP SỬ DỤNG:
  python demo_ci.py                     # Mở menu lựa chọn tương tác
  python demo_ci.py --member 1          # Demo Nguyễn Giang Nam (hoặc --member namng)
  python demo_ci.py --member 2          # Demo Nguyễn Đình Hải (hoặc --member haind)
  python demo_ci.py --member 3          # Demo Đào Xuân Mạnh (hoặc --member manhdx)
  python demo_ci.py --member 4          # Demo Lê Đức Anh (hoặc --member anhld)
  python demo_ci.py --member 5          # Demo Nguyễn Phương Mai (hoặc --member mainp)
  python demo_ci.py --all               # Demo lần lượt toàn bộ 5 thành viên
  python demo_ci.py --member 1 --fix    # Demo kịch bản đã khắc phục (CI Pass)
  python demo_ci.py --member 2 --fast   # Chạy nhanh bỏ qua thời gian trễ hiệu ứng
"""

from __future__ import annotations

import os
from pathlib import Path
import sys

# Đảm bảo thư mục gốc nằm trong sys.path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Gọi hàm main từ ci/demo_runner.py để xử lý menu tương tác và phân tích tham số CLI
from ci.demo_runner import main

if __name__ == "__main__":
    main()
