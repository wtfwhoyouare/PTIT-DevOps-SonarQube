#!/usr/bin/env python3
"""Script điều hướng trung tâm kích hoạt và theo dõi luồng CI thật (GitHub Actions Live).

Cú pháp:
  python demo/demo_ci.py --trigger          # Kích hoạt luồng CI thật trên GitHub
  python demo/demo_ci.py --watch            # Theo dõi tiến trình trực tiếp các Stage
  python demo/demo_ci.py -m 1               # Xem lỗi phân hệ của Nguyễn Giang Nam
  python demo/demo_ci.py -m 2               # Xem lỗi phân hệ của Nguyễn Đình Hải
  python demo/demo_ci.py -m 3               # Xem lỗi phân hệ của Đào Xuân Mạnh
  python demo/demo_ci.py -m 4               # Xem lỗi phân hệ của Lê Đức Anh
  python demo/demo_ci.py -m 5               # Xem lỗi phân hệ của Nguyễn Phương Mai
  python demo/demo_ci.py --errors           # Xem bảng tổng hợp toàn bộ 5 thành viên
"""

import sys
from pathlib import Path

# Đảm bảo thư mục hiện tại và root nằm trong sys.path
CUR_DIR = Path(__file__).resolve().parent
ROOT_DIR = CUR_DIR.parent if CUR_DIR.name == "demo" else CUR_DIR

for p in (CUR_DIR, ROOT_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from demo_live_ci import main

if __name__ == "__main__":
    main()
