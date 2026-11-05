# -*- coding: utf-8 -*-
"""
Wrapper điều hướng gọi scripts/simulate_telemetry.py
Cho phép người dùng chạy trực tiếp từ thư mục gốc dự án:
    python simulate_telemetry.py --mem namng
"""
import os
import sys

script_path = os.path.join(os.path.dirname(__file__), "scripts", "simulate_telemetry.py")
if not os.path.exists(script_path):
    print(f"Lỗi: Không tìm thấy tệp mục tiêu tại {script_path}")
    sys.exit(1)

with open(script_path, "r", encoding="utf-8") as f:
    code = f.read()

# Chạy với context của script
sys.argv[0] = script_path
exec(code, {"__name__": "__main__", "__file__": script_path})

