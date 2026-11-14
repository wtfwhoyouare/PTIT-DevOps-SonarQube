# HƯỚNG DẪN CÁC CÂU LỆNH CHẠY DEMO — PHÂN HỆ NGUYỄN GIANG NAM (NAMNG)

> **Mã định danh:** `NAMNG`  
> **Họ và tên:** Nguyễn Giang Nam  
> **Mã sinh viên:** `B26CHAT030`  
> **Vai trò:** Trưởng nhóm — Kiến trúc sư DevSecOps & Security Lead (Lead Architect)  
> **Phạm vi phân hệ phụ trách:** Cổng thông tin công cộng, Quản lý quy chuẩn phân nhánh & Tra cứu cảng biển (`ports.php`, `news.php`, `docker-compose.yml`, `index.php`, `home.php`)  
> **Hệ thống chốt chặn:** Stage 1 Policy Guard, Stage 2 Semgrep SAST & SonarQube Code Quality  

---

## 1. Demo Trực Quan & Giám Sát Luồng CI Thật trên GitHub Actions (`demo/demo_live_ci.py`)

Kịch bản điều khiển quy trình DevSecOps CI/CD thực tế 100% trên nền tảng GitHub Actions Cloud thông qua GitHub CLI (`gh`).

> [!TIP]
> **Lưu ý trên Windows:** Luôn sử dụng cờ `-X utf8` (`python -X utf8 ...`) để đảm bảo hiển thị đúng bảng Unicode, màu sắc ANSI và tiếng Việt có dấu.

### 1.1. Xem trực tiếp 7 lỗi vi phạm kèm ngữ cảnh dòng code thực tế
Trích xuất chi tiết 4 lỗi an ninh SAST + 3 lỗi chất lượng mã nguồn SonarQube của phân hệ `namng`:
```powershell
python -X utf8 demo/demo_live_ci.py -m namng
# hoặc dùng số thứ tự thành viên:
python -X utf8 demo/demo_live_ci.py -m 1
```
* **Nội dung kết xuất:**
  * Bảng tổng hợp mã lỗi, quy tắc, vị trí tệp và dòng code.
  * Phân tích luồng dữ liệu ô nhiễm (*Taint Source* ➔ *Taint Sink*).
  * Viện dẫn căn cứ pháp lý: **Nghị định 13/2023/NĐ-CP** (Điều 9, 13, 26), **GDPR Article 32**, **OWASP Top 10:2021 A03**.
  * Trích xuất trực tiếp khối mã nguồn vi phạm trên đĩa kèm con trỏ màu đỏ `➔`.

### 1.2. Kích hoạt luồng CI thật mới trên GitHub Actions với nhánh `namng`
Bắn sự kiện `workflow_dispatch` lên GitHub Cloud và stream tiến trình trực tiếp:
```powershell
python -X utf8 demo/demo_live_ci.py --trigger --branch namng
```
* **Cơ chế chứng minh:**
  * Cấp Run ID mới từ GitHub Actions API.
  * Live Dashboard polling mỗi 3 giây cập nhật trạng thái 4 Stage.
  * Kích hoạt còi báo động **`🛑 [CI CHẶN ĐỨNG - BREAK-THE-BUILD]`** tại Stage 2, chứng minh hủy bỏ triệt để (SKIPPED) Stage 3 & 4.

### 1.3. Kích hoạt CI mới + Tự động in bảng lỗi vi phạm của `namng` khi CI ngắt
```powershell
python -X utf8 demo/demo_live_ci.py --trigger --branch namng -m 1
```

### 1.4. Theo dõi lần chạy CI gần nhất hoặc theo Run ID cụ thể
```powershell
# Theo dõi lần chạy mới nhất:
python -X utf8 demo/demo_live_ci.py --latest

# Theo dõi một Run ID cụ thể:
python -X utf8 demo/demo_live_ci.py --watch <Run_ID>
```

### 1.5. Mở Menu tương tác bằng phím số (không cần nhớ cờ lệnh)
```powershell
python -X utf8 demo/demo_live_ci.py
```

---

## 2. Demo Mô Phỏng Chốt Chặn DevSecOps Cục Bộ & Khắc Phục Lỗi (`ci/demo_runner.py`)

Động cơ demo quy trình kiểm định an ninh 3 tầng, phân tích RACI và kịch bản khắc phục mã nguồn ngay tại máy cục bộ.

### 2.1. Demo cơ chế Chặn đứng (Break-the-Build Gate)
Mô phỏng phát hiện lỗi tại Stage 2 và khóa hoàn toàn nút Merge:
```powershell
python -X utf8 ci/demo_runner.py -m namng --fast
```

### 2.2. Chạy trực tiếp các engine thật ở môi trường Local (Real Execution)
Kích hoạt trực tiếp các script `policy_guard.py`, `semgrep_gate.py` và validator IaC:
```powershell
python -X utf8 ci/demo_runner.py -m namng --real --fast
```

### 2.3. Demo kịch bản khắc phục mã nguồn an toàn (Remediation Mode — CI Pass)
Mô phỏng kết quả sau khi đã áp dụng code chuẩn (Prepared Statements, `htmlspecialchars`):
```powershell
python -X utf8 ci/demo_runner.py -m namng --remediate --fast
```
* Toàn bộ 4 Stage đều xanh (`PASSED`), chứng minh luồng CI được mở khóa thành công.

---

## 3. Diễn Tập Tấn Công Thực Nghiệm & Phát Thải Telemetry Gắn Tag `[NAMNG]` (`scripts/simulate_telemetry.py`)

Kịch bản tự động inject định danh thành viên vào Query string, SQL payload, User-Agent và Custom Header (`X-Audit-Member: NAMNG`) để giám sát viên lọc trực tiếp trên Grafana Loki Dashboard.

### 3.1. Chạy toàn bộ 4 kịch bản khai thác của `namng` (V1, V14, V16, V17)
```powershell
python -X utf8 scripts/simulate_telemetry.py --mem namng
```

### 3.2. Bắn 3 vòng lặp để tạo xung nhịp (Spikes) rõ nét trên biểu đồ Grafana
```powershell
python -X utf8 scripts/simulate_telemetry.py --mem namng --repeat 3 --delay 1.0
```

### 3.3. Bắn lẻ từng kịch bản cụ thể để quay video minh chứng
* **Kịch bản V1** — In-band UNION SQL Injection tại `/ports`:
  ```powershell
  python -X utf8 scripts/simulate_telemetry.py --mem namng --cases V1
  ```
  * Payload: `cn' UNION SELECT 1, username, password, email FROM users /* [MEMBER: NAMNG] */-- -`
  * Mục tiêu Grafana: *Panel 2: SQL Injection (SQLi) Attacks in HTTP Traffic*

* **Kịch bản V14** — News Portal UNION Data Extraction tại `/news`:
  ```powershell
  python -X utf8 scripts/simulate_telemetry.py --mem namng --cases V14
  ```
  * Payload: `1' UNION SELECT 1, username, password, email FROM users /* [MEMBER: NAMNG] */-- -`
  * Mục tiêu Grafana: *Panel 2: SQL Injection (SQLi) Attacks in HTTP Traffic*

* **Kịch bản V16** — Reflected Cross-Site Scripting (XSS) tại `/ports`:
  ```powershell
  python -X utf8 scripts/simulate_telemetry.py --mem namng --cases V16
  ```
  * Payload: `<script>/* [MEMBER: NAMNG] */ alert('DevSecOps-NAMNG-Verification')</script>`
  * Mục tiêu Grafana: *Panel 4: Cross-Site Scripting (XSS) in HTTP Traffic*

* **Kịch bản V17** — Dò quét tệp cấu hình bí mật môi trường `/.env`:
  ```powershell
  python -X utf8 scripts/simulate_telemetry.py --mem namng --cases V17
  ```
  * Mục tiêu Grafana: *Panel 6: HTTP Error-Based Response Leaks & 4xx/5xx Server Faults*

### 3.4. Cú pháp truy vấn LogQL trên Grafana Loki (`https://grafana.inlaneweb.io.vn`)
Trong ô tìm kiếm LogQL của Grafana, nhập các truy vấn sau để lọc riêng dữ liệu của `namng`:
```logql
# Lọc theo chuỗi định danh NAMNG trong toàn bộ log container web:
{container="ilfreight_web"} |= "NAMNG"

# Lọc chi tiết theo trường query hoặc user_agent:
{container="ilfreight_web"} |~ "(?i)member.*NAMNG"
```

---

## 4. Bộ Kiểm Thử Tự Động Hóa Nội Bộ (Unit Tests & Syntax Check)

1. **Chạy toàn bộ 24 bài kiểm tra Policy Guard, Semgrep Gate, SonarQube:**
   ```powershell
   python -m pytest tests/
   ```

2. **Kiểm tra cú pháp PHP (Syntax Lint) các tệp thuộc phân hệ:**
   ```powershell
   wsl php -l InlaneWeb/web/src/pages/ports.php
   wsl php -l InlaneWeb/web/src/pages/news.php
   wsl php -l InlaneWeb/web/src/pages/home.php
   wsl php -l InlaneWeb/web/src/index.php
   ```

---

## 5. Bảng Đối Soát 07 Lỗi Vi Phạm Nộp Bài Của Nguyễn Giang Nam

| Mã | Tên lỗi vi phạm | Vị trí (Tệp:Dòng) | Động cơ kiểm định | Phân loại / Quy tắc |
| :---: | :--- | :--- | :---: | :--- |
| **SAST01** | In-band UNION SQL Injection | `InlaneWeb/web/src/pages/ports.php:38` | Semgrep Taint | `CWE-89: SQL Injection` |
| **SAST02** | Reflected Cross-Site Scripting (XSS) | `InlaneWeb/web/src/pages/ports.php:26` | Semgrep / Sonar | `CWE-79: Cross-Site Scripting` |
| **SAST03** | Numeric UNION SQL Injection | `InlaneWeb/web/src/pages/news.php:17` | Semgrep Taint | `CWE-89: SQL Injection` |
| **SAST04** | Hardcoded Database Root Password | `InlaneWeb/docker-compose.yml:17` | Semgrep Secret | `CWE-798: Hardcoded Credentials` |
| **CQ-01** | Input Control Missing ID & Label | `InlaneWeb/web/src/pages/ports.php:26` | SonarQube Bug | `Web:InputWithoutLabelCheck` |
| **CQ-02** | Homepage Search Input Missing Label | `InlaneWeb/web/src/pages/home.php:9` | SonarQube Bug | `Web:InputWithoutLabelCheck` |
| **CQ-03** | Router Navigation Using 'require' | `InlaneWeb/web/src/index.php:44` | SonarQube Bug | `php:S2003` |
