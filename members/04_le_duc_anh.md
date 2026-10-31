# BÁO CÁO PHÂN TÍCH LỖ HỔNG AN TOÀN BẢO MẬT
**Thành viên thực hiện:** Lê Đức Anh  
**Vai trò trong dự án:** Kỹ sư Tự động hóa Hạ tầng & Cấu hình An toàn (Infrastructure Automation & Platform Security Engineer)  
**Phạm vi phụ trách:** Quản lý Tài khoản & Hồ sơ Đối tác, Theo dõi Chi tiết Vận tải & An toàn Cấu hình Triển khai  
**Đề tài:** Hệ thống DevSecOps CI/CD kiểm định an ninh tự động cho InlaneWeb Logistics Portal  

---

## PHẦN A: TỔNG HỢP DANH MỤC 4 LỖ HỔNG AN TOÀN BẢO MẬT (SAST - SEMGREP / OWASP / CWE)

| STT | Tên Lỗ hổng | Phân loại | Mã CWE | Tệp tin & Vị trí vi phạm | Mức độ cảnh báo | Động cơ phát hiện |
| :---: | :--- | :---: | :---: | :--- | :---: | :---: |
| 1 | **Order-By Clause SQL Injection** | Code | CWE-89 | `InlaneWeb/web/src/pages/account.php:41` | 🔴 High / ERROR | Semgrep Taint Engine |
| 2 | **UPDATE Statement SQL Injection** | Code | CWE-89 | `InlaneWeb/web/src/pages/account_update.php:20` | 🔴 High / ERROR | Semgrep Taint Engine |
| 3 | **Numeric Shipment Detail SQL Injection** | Code | CWE-89 | `InlaneWeb/web/src/pages/shipment_detail.php:15` | 🔴 High / ERROR | Semgrep Taint Engine |
| 4 | **Hardcoded Root Password trong Production Compose** | Triển khai / IaC | CWE-798 | `InlaneWeb/docker-compose.prod.yml:15` | 🔴 High / ERROR | Semgrep Secrets & PaC |

---

## CHI TIẾT TỪNG LỖ HỔNG BẢO MẬT

### 1. Order-By Clause SQL Injection tại trang Quản lý Hồ sơ & Vận đơn
* **Vị trí vi phạm:** [InlaneWeb/web/src/pages/account.php:41](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/pages/account.php#L41)
* **Phân loại lỗi:** Mã nguồn (Application Code) | **Pha DevSecOps:** Pha Test / SAST (Stage 2)
* **Mã định danh điểm yếu:** **CWE-89: SQL Injection** | **OWASP Top 10:2021:** A03:2021 — Injection
* **Quy tắc phát hiện:** Semgrep Rule `php.lang.security.injection.tainted-sql-string.tainted-sql-string`

#### a. Bằng chứng mã nguồn vi phạm (Vulnerable Code):
```php
// Source: Tham số ?order= được người dùng kiểm soát trên URL
$order = $_GET['order'] ?? 'id';

// Sink: Nối trực tiếp chuỗi vào mệnh đề ORDER BY mà không qua kiểm tra danh sách trắng
$sql = "SELECT tracking_no, port_code, status FROM shipments WHERE customer_id = "
     . intval($u['id']) . " ORDER BY $order";
echo '<div class="query-box">' . htmlspecialchars($sql) . '</div>';

$res = query($sql);
```

#### b. Cơ chế phát hiện & Trích xuất mã nguồn (Detection Mechanism):
* **Quy tắc Semgrep quét phát hiện (Rule Definition Code):**
```yaml
rules:
  - id: php.lang.security.injection.tainted-sql-string.tainted-sql-string
    languages: [php]
    severity: ERROR
    mode: taint
    pattern-sources:
      - pattern: $_GET[...]
    pattern-sinks:
      - pattern: query("... ORDER BY $ORDER", ...)
```

* **Cơ chế phân tích luồng ô nhiễm (Taint / AST Analysis):**
  - **Tệp tin & hàm xử lý:** Tự động phát hiện trong Stage 2 và trích xuất qua script [`ci/semgrep_report.py`](file:///d:/PTIT-DevOps-SonarQube/ci/semgrep_report.py) bằng hàm `extract_source_and_sink(path_str, line_no)`.
  - **🟡 SOURCE (Nguồn dữ liệu người dùng nhập / Khai báo cấu hình):**
```php
// Dòng 39 (InlaneWeb/web/src/pages/account.php):
$order = $_GET['order'] ?? 'id';
```
  - **🔴 SINK (Điểm kích hoạt / Thực thi câu lệnh nguy hiểm):**
```php
// Dòng 41-45 (InlaneWeb/web/src/pages/account.php):
$sql = "SELECT tracking_no, port_code, status FROM shipments WHERE customer_id = "
     . intval($u['id']) . " ORDER BY $order";
$res = query($sql);
```

#### c. Kịch bản khai thác thực tế (PoC):
Do mệnh đề `ORDER BY` trong SQL không hỗ trợ dùng dấu tham số `?` (Prepared Statements) cho tên cột hay biểu thức sắp xếp, kẻ tấn công khai thác kỹ thuật **Boolean Blind** hoặc **Error-based SQLi** thông qua biểu thức điều kiện:
```http
GET /account?order=(CASE+WHEN+(SELECT+SUBSTR(password,1,1)+FROM+users+WHERE+username='admin')='a'+THEN+id+ELSE+port_code+END)
```
Hoặc kích hoạt lỗi để trích xuất dữ liệu qua hàm `extractvalue()`:
```http
GET /account?order=extractvalue(1,concat(0x7e,(SELECT+user())))
```
* **Hậu quả:** Kẻ tấn công đoán từng ký tự mật khẩu băm của quản trị viên hệ thống hoặc trích xuất thông tin CSDL nội bộ.

#### d. Cách thức xử lý & Khắc phục (Remediation):
Vì Prepared Statements không thể áp dụng cho tên cột trong mệnh đề `ORDER BY`, giải pháp chuẩn mực là áp dụng **Whitelist Validation (Danh sách trắng)** nghiêm ngặt kết hợp Prepared Statements cho tham số `customer_id`:
```php
// Whitelist các cột cho phép sắp xếp
$allowed_columns = ['id', 'tracking_no', 'port_code', 'status'];
$order_param = $_GET['order'] ?? 'id';
$order = in_array($order_param, $allowed_columns, true) ? $order_param : 'id';

$stmt = db()->prepare("SELECT tracking_no, port_code, status FROM shipments WHERE customer_id = ? ORDER BY " . $order);
$cid = intval($u['id']);
$stmt->bind_param("i", $cid);
$stmt->execute();
$res = $stmt->get_result();
```

#### e. Đánh giá Vi phạm Chính sách & Bài toán Security-as-Code (SaC):
* **Pha trong quy trình DevSecOps:** **Pha Test / SAST Gate (Stage 2 trong CI/CD Pipeline)**
  - *Đánh giá rủi ro:* Lỗi xảy ra trong chức năng sắp xếp vận đơn. Mệnh đề ORDER BY không thể dùng tham số hóa thông thường nên nếu thiếu Whitelist, kẻ tấn công có thể trích xuất dữ liệu qua kỹ thuật Boolean Blind SQLi.
* **Căn cứ vi phạm chính sách pháp lý:**
  - **Nghị định 13/2023/NĐ-CP:** Điều 9 Khoản 2 & Điều 26 (Vi phạm quy định bảo đảm an toàn dữ liệu, để lộ thông tin vận tải của khách hàng).
  - **GDPR (Châu Âu):** Article 32 (Không duy trì biện pháp kỹ thuật kiểm soát luồng truy vấn an toàn để bảo mật thông tin đối tác).
* **Hiện thực hóa Bài toán Security-as-Code (SaC):**
  - Quy tắc Taint Analysis phát hiện biến `$_GET['order']` đi vào mệnh đề sắp xếp SQL:
```yaml
# Bắt buộc kiểm tra danh sách trắng cho mệnh đề ORDER BY
- id: php.lang.security.injection.tainted-sql-string.tainted-sql-string
  languages: [php]
  severity: ERROR
  pattern: query("... ORDER BY $ORDER", ...)
```

---

### 2. UPDATE Statement SQL Injection tại trang Cập nhật Hồ sơ Người dùng
* **Vị trí vi phạm:** [InlaneWeb/web/src/pages/account_update.php:20](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/pages/account_update.php#L20)
* **Phân loại lỗi:** Mã nguồn (Application Code) | **Pha DevSecOps:** Pha Test / SAST (Stage 2)
* **Mã định danh điểm yếu:** **CWE-89: SQL Injection** | **OWASP Top 10:2021:** A03:2021 — Injection
* **Quy tắc phát hiện:** Semgrep Rule `php.lang.security.injection.tainted-sql-string.tainted-sql-string`

#### a. Bằng chứng mã nguồn vi phạm (Vulnerable Code):
```php
$email = $_POST['email'] ?? '';

// Sink: Nối thẳng chuỗi $email vào mệnh đề SET trong câu lệnh UPDATE
$sql = "UPDATE users SET email = '$email' WHERE id = " . intval($u['id']);

render_header('Cập nhật hồ sơ');
echo '<div class="card"><h1>Cập nhật hồ sơ</h1>';
echo '<div class="query-box">' . htmlspecialchars($sql) . '</div>';

if (exec_write($sql)) {
    $affected = mysqli_affected_rows(db());
    flash('Đã cập nhật hồ sơ...', 'success');
}
```

#### b. Cơ chế phát hiện & Trích xuất mã nguồn (Detection Mechanism):
* **Quy tắc Semgrep quét phát hiện (Rule Definition Code):**
```yaml
rules:
  - id: php.lang.security.injection.tainted-sql-string.tainted-sql-string
    languages: [php]
    severity: ERROR
    mode: taint
    pattern-sources:
      - pattern: $_POST[...]
    pattern-sinks:
      - pattern: exec_write("UPDATE ... SET ... = '$VAL' ...", ...)
```

* **Cơ chế phân tích luồng ô nhiễm (Taint / AST Analysis):**
  - **Tệp tin & hàm xử lý:** Tự động phát hiện trong Stage 2 và trích xuất qua script [`ci/semgrep_report.py`](file:///d:/PTIT-DevOps-SonarQube/ci/semgrep_report.py) bằng hàm `extract_source_and_sink(path_str, line_no)`.
  - **🟡 SOURCE (Nguồn dữ liệu người dùng nhập / Khai báo cấu hình):**
```php
// Dòng 17 (InlaneWeb/web/src/pages/account_update.php):
$email = $_POST['email'] ?? '';
```
  - **🔴 SINK (Điểm kích hoạt / Thực thi câu lệnh nguy hiểm):**
```php
// Dòng 20-26 (InlaneWeb/web/src/pages/account_update.php):
$sql = "UPDATE users SET email = '$email' WHERE id = " . intval($u['id']);
if (exec_write($sql)) {
```

#### c. Kịch bản khai thác thực tế (PoC):
Kẻ tấn công đóng chuỗi nháy đơn `'` và thay đổi phạm vi cập nhật sang tài khoản quản trị viên, hoặc **tự nâng quyền thành admin (Privilege Escalation)**:
```http
POST /account/update
Content-Type: application/x-www-form-urlencoded

email=attacker@hacker.io', role='admin' WHERE id=2-- -
```
Hoặc đổi toàn bộ email của tài khoản `admin` để chiếm đoạt tài khoản thông qua chức năng phục hồi mật khẩu:
```http
email=pwned@inlane.ptit' WHERE username='admin'-- -
```
* **Hậu quả:** Kẻ tấn công phá vỡ cấu trúc phân quyền (RBAC), tự cấp quyền Admin tối cao hoặc ghi đè dữ liệu của mọi người dùng trong hệ thống.

#### d. Cách thức xử lý & Khắc phục (Remediation):
Sử dụng **Prepared Statements tham số hóa** và hàm kiểm định định dạng email chuẩn `filter_var`:
```php
$email = filter_input(INPUT_POST, 'email', FILTER_VALIDATE_EMAIL);
if (!$email) {
    flash('Định dạng email không hợp lệ!', 'danger');
    header('Location: /account');
    exit;
}

$stmt = db()->prepare("UPDATE users SET email = ? WHERE id = ?");
$user_id = intval($u['id']);
$stmt->bind_param("si", $email, $user_id);
$stmt->execute();
```

#### e. Đánh giá Vi phạm Chính sách & Bài toán Security-as-Code (SaC):
* **Pha trong quy trình DevSecOps:** **Pha Test / SAST Gate (Stage 2 trong CI/CD Pipeline)**
  - *Đánh giá rủi ro:* Lỗi nằm tại chức năng cập nhật hồ sơ cá nhân. Việc nối chuỗi vào mệnh đề SET UPDATE cho phép kẻ tấn công sửa đổi hồ sơ người khác hoặc tự nâng quyền thành quản trị viên (Privilege Escalation).
* **Căn cứ vi phạm chính sách pháp lý:**
  - **Nghị định 13/2023/NĐ-CP:** Điều 9 Khoản 2 & Điều 13 Khoản 1 (Vi phạm nguyên tắc bảo đảm tính chính xác và an toàn của dữ liệu cá nhân, để kẻ xấu sửa đổi trái phép hồ sơ người dùng khác).
  - **GDPR (Châu Âu):** Article 5(1)(d) — Accuracy & Article 32 (Không đảm bảo tính chính xác và tính toàn vẹn của dữ liệu trong quá trình lưu trữ và cập nhật).
* **Hiện thực hóa Bài toán Security-as-Code (SaC):**
  - Bắt buộc chuyển đổi câu lệnh UPDATE sang Prepared Statements có tham số hóa:
```yaml
# Chốt chặn SaC bắt buộc tham số hóa câu lệnh UPDATE
- id: php.lang.security.injection.tainted-sql-string.tainted-sql-string
  languages: [php]
  severity: ERROR
  pattern: exec_write("UPDATE ... SET ... = '$VAL' ...", ...)
```

---

### 3. Numeric In-band SQL Injection tại trang Chi tiết Vận đơn
* **Vị trí vi phạm:** [InlaneWeb/web/src/pages/shipment_detail.php:15](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/pages/shipment_detail.php#L15)
* **Phân loại lỗi:** Mã nguồn (Application Code) | **Pha DevSecOps:** Pha Test / SAST (Stage 2)
* **Mã định danh điểm yếu:** **CWE-89: SQL Injection** | **OWASP Top 10:2021:** A03:2021 — Injection
* **Quy tắc phát hiện:** Semgrep Rule `php.lang.security.injection.tainted-sql-string.tainted-sql-string`

#### a. Bằng chứng mã nguồn vi phạm (Vulnerable Code):
```php
$id = $_GET['id'] ?? '';

render_header('Chi tiết đơn hàng');

// SELECT don hang (id noi chuoi -> injectable, kieu so)
$sql = "SELECT id, tracking_no, port_code, status FROM shipments WHERE id = $id";
echo '<div class="card"><h1>Đơn hàng #' . htmlspecialchars($id) . '</h1>';
echo '<div class="query-box">' . htmlspecialchars($sql) . '</div>';
$sh = query_one($sql);
```

#### b. Cơ chế phát hiện & Trích xuất mã nguồn (Detection Mechanism):
* **Quy tắc Semgrep quét phát hiện (Rule Definition Code):**
```yaml
rules:
  - id: php.lang.security.injection.tainted-sql-string.tainted-sql-string
    languages: [php]
    severity: ERROR
    mode: taint
    pattern-sources:
      - pattern: $_GET[...]
    pattern-sinks:
      - pattern: query_one("SELECT ... WHERE id = $ID", ...)
```

* **Cơ chế phân tích luồng ô nhiễm (Taint / AST Analysis):**
  - **Tệp tin & hàm xử lý:** Tự động phát hiện trong Stage 2 và trích xuất qua script [`ci/semgrep_report.py`](file:///d:/PTIT-DevOps-SonarQube/ci/semgrep_report.py) bằng hàm `extract_source_and_sink(path_str, line_no)`.
  - **🟡 SOURCE (Nguồn dữ liệu người dùng nhập / Khai báo cấu hình):**
```php
// Dòng 10 (InlaneWeb/web/src/pages/shipment_detail.php):
$id = $_GET['id'] ?? '';
```
  - **🔴 SINK (Điểm kích hoạt / Thực thi câu lệnh nguy hiểm):**
```php
// Dòng 15-18 (InlaneWeb/web/src/pages/shipment_detail.php):
$sql = "SELECT id, tracking_no, port_code, status FROM shipments WHERE id = $id";
$sh = query_one($sql);
```

#### c. Cách thức xử lý & Khắc phục (Remediation):
Áp dụng ép kiểu số nguyên chặt chẽ và chuyển sang Prepared Statements:
```php
$id = filter_input(INPUT_GET, 'id', FILTER_VALIDATE_INT);
if ($id === false || $id === null) {
    flash('Mã đơn hàng không hợp lệ.', 'danger');
    header('Location: /account');
    exit;
}

$stmt = db()->prepare("SELECT id, tracking_no, port_code, status FROM shipments WHERE id = ?");
$stmt->bind_param("i", $id);
$stmt->execute();
$res = $stmt->get_result();
$sh = $res->fetch_assoc();
```

#### e. Đánh giá Vi phạm Chính sách & Bài toán Security-as-Code (SaC):
* **Pha trong quy trình DevSecOps:** **Pha Test / SAST Gate (Stage 2 trong CI/CD Pipeline)**
  - *Đánh giá rủi ro:* Lỗi nằm tại trang chi tiết đơn hàng. Tham số `$id` dạng số không được bọc nháy và không ép kiểu cho phép kẻ tấn công trích xuất dữ liệu qua câu lệnh UNION SELECT.
* **Căn cứ vi phạm chính sách pháp lý:**
  - **Nghị định 13/2023/NĐ-CP:** Điều 9 Khoản 2 (Vi phạm nghĩa vụ ngăn chặn các hành vi thu thập và tiếp cận dữ liệu cá nhân trái phép).
  - **GDPR (Châu Âu):** Article 32 (Không đảm bảo tính bảo mật của dữ liệu vận tải và danh tính khách hàng trong hệ thống logistics).
* **Hiện thực hóa Bài toán Security-as-Code (SaC):**
  - Taint tracking phát hiện biến số nguyên đi vào câu lệnh truy vấn chi tiết:
```yaml
# Tự động bắt lỗi Numeric SQL Injection
- id: php.lang.security.injection.tainted-sql-string.tainted-sql-string
  languages: [php]
  severity: ERROR
  pattern: query_one("SELECT ... WHERE id = $ID", ...)
```

---

### 4. Hardcoded Root Password trong Tệp Cấu hình Triển khai Môi trường Sản xuất (Production Compose)
* **Vị trí vi phạm:** [InlaneWeb/docker-compose.prod.yml:15](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/docker-compose.prod.yml#L15)
* **Phân loại lỗi:** Triển khai & Cấu hình Vận hành (Deployment & Operations / IaC) | **Pha DevSecOps:** Pha Release / Deploy (Stage 3 & 4)
* **Mã định danh điểm yếu:** **CWE-798: Use of Hard-coded Credentials** | **OWASP Top 10:2021:** A07:2021 — Identification and Authentication Failures
* **Quy tắc phát hiện:** Semgrep Rule `ci.compose-hardcoded-mysql-root-password` & Pipeline Test Case `ci/validate_configs.py` (Policy-as-Code)

#### a. Bằng chứng cấu hình vi phạm:
```yaml
# InlaneWeb/docker-compose.prod.yml
services:
  db:
    image: ${INLANEWEB_DB_IMAGE:-ghcr.io/wtfwhoyouare/inlaneweb-db:latest}
    container_name: ilfreight_db
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: password   # NGUY CƠ: Mật khẩu root cố định trên môi trường Production!
      MYSQL_ROOT_HOST: "%"
```

#### b. Cơ chế phát hiện & Trích xuất mã nguồn (Detection Mechanism):
* **Quy tắc Semgrep quét phát hiện (Rule Definition Code):**
```yaml
rules:
  - id: compose-hardcoded-mysql-root-password
    languages: [yaml]
    severity: ERROR
    message: MYSQL_ROOT_PASSWORD is hardcoded in Compose. Supply it from a secret instead.
    patterns:
      - pattern: |
          MYSQL_ROOT_PASSWORD: $PASSWORD
      - metavariable-regex:
          metavariable: $PASSWORD
          regex: '^(?!["']?\${)[A-Za-z0-9_!@#.$-]+$'
    paths:
      include:
        - "**/docker-compose*.yml"
```

* **Cơ chế phân tích luồng ô nhiễm (Taint / AST Analysis):**
  - **Tệp tin & hàm xử lý:** Tự động phát hiện trong Stage 2 và trích xuất qua script [`ci/semgrep_report.py`](file:///d:/PTIT-DevOps-SonarQube/ci/semgrep_report.py) bằng hàm `extract_source_and_sink(path_str, line_no)`.
  - **🟡 SOURCE (Nguồn dữ liệu người dùng nhập / Khai báo cấu hình):**
```yaml
# InlaneWeb/docker-compose.prod.yml: Cấu hình container MariaDB Production
```
  - **🔴 SINK (Điểm kích hoạt / Thực thi câu lệnh nguy hiểm):**
```yaml
# Dòng 15 (InlaneWeb/docker-compose.prod.yml):
MYSQL_ROOT_PASSWORD: password
```

#### c. Cách thức xử lý & Khắc phục (Remediation):
1. **Loại bỏ mật khẩu dạng rõ (Cleartext):** Sử dụng biến môi trường nạp từ GitHub Secrets hoặc Docker Secrets.
2. **Triển khai tệp cấu hình an toàn:**
```yaml
services:
  db:
    image: ${INLANEWEB_DB_IMAGE:-ghcr.io/wtfwhoyouare/inlaneweb-db:latest}
    container_name: ilfreight_db
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD_FILE: /run/secrets/db_root_password
      MYSQL_ROOT_HOST: "localhost"
    secrets:
      - db_root_password

secrets:
  db_root_password:
    external: true
```

#### e. Đánh giá Vi phạm Chính sách & Bài toán Policy-as-Code (PaC):
* **Pha trong quy trình DevSecOps:** **Pha Release / Deploy (Stage 3 & 4 trong CI/CD Pipeline)**
  - *Đánh giá rủi ro:* Lỗi cấu hình hạ tầng môi trường sản xuất. Mật khẩu cố định `password` trên production compose tạo nguy cơ máy chủ CSDL bị chiếm đoạt toàn quyền kiểm soát ngay khi triển khai lên máy chủ VPS.
* **Căn cứ vi phạm chính sách pháp lý:**
  - **Nghị định 13/2023/NĐ-CP:** Điều 13 Khoản 1 & Điều 26 (Vi phạm nguyên tắc bảo vệ dữ liệu cá nhân ngay từ khâu thiết kế - Privacy by Design và thiếu biện pháp bảo vệ thông tin xác thực an ninh mạng).
  - **GDPR (Châu Âu):** Article 25 & Article 32 (Sử dụng mật khẩu mặc định trên môi trường sản xuất là hành vi vi phạm nghiêm trọng các quy chuẩn bảo mật kỹ thuật tối thiểu).
* **Hiện thực hóa Bài toán Policy-as-Code (PaC):**
  - Kiểm thử tự động chính sách an toàn hạ tầng IaC tại Stage 3 trước khi triển khai VPS (`ci/validate_configs.py`):
```python
# ci/validate_configs.py: Stage 3 Pre-deployment IaC Validation
def test_production_compose_no_hardcoded_passwords(compose_prod_data):
    db_env = compose_prod_data.get('services', {}).get('db', {}).get('environment', {})
    root_pass = db_env.get('MYSQL_ROOT_PASSWORD', '')
    assert root_pass != 'password', "[PAC VIOLATION] Mật khẩu mặc định trong Production Compose!"
    assert not root_pass or root_pass.startswith('${'), "[PAC VIOLATION] Mật khẩu CSDL phải nạp qua Secret!"
```

---

## PHẦN B: KIỂM ĐỊNH CHẤT LƯỢNG MÃ NGUỒN (SONARQUBE CODE QUALITY)

Trong mô hình DevSecOps hiện đại, bên cạnh các lỗ hổng an ninh mạng (Security Gate), dự án triển khai quy chuẩn kiểm soát kép **Dual-Gate (Security Gate + Quality Gate)**. Công cụ **SonarQube Scanner** được kích hoạt tại Stage 2 để kiểm tra toàn diện chất lượng giao diện người dùng và tiêu chuẩn khả năng tiếp cận (Accessibility - WCAG 2.1). Bất kỳ vi phạm nào thuộc nhóm **Major Code Smells** trên New Code đều sẽ làm tụt hạng khả năng bảo trì và đánh rớt **SonarQube Quality Gate** (**FAILED**).

### 1. Tổng quan Lỗi Chất lượng Mã nguồn Phụ trách

| Tiêu chí Thẩm định | Nội dung Chi tiết từ SonarQube Scanner |
| :--- | :--- |
| **Tên vấn đề Code Quality** | **Form Label Not Associated With Input Control (Accessibility Code Smell)** |
| **Mã quy tắc vi phạm (Rule Key)** | [`Web:S6853`](https://rules.sonarsource.com/html/RSPEC-6853) / `Web:LabelWithoutControlCheck` |
| **Phân loại vấn đề (Issue Type)** | ♨️ **CODE_SMELL** (Mùi mã nguồn trợ năng giao diện Web) |
| **Mức độ nghiêm trọng (Severity)**| 🟠 **MAJOR** |
| **Tệp tin & Vị trí vi phạm** | [InlaneWeb/web/src/pages/account.php:28](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/pages/account.php#L28) |
| **Phạm vi tiêu chuẩn áp dụng** | **WCAG 2.1 Success Criterion 1.3.1 (Info and Relationships), 4.1.2** & **ISO/IEC 40500** |
| **Trạng thái Quality Gate** | ❌ **FAILED** (Vi phạm điều kiện: `Maintainability Rating must be A on New Code`) |

### 2. Bằng chứng Mã nguồn Vi phạm (Non-compliant Code)
Tại trang Hồ sơ & Tài khoản người dùng (`InlaneWeb/web/src/pages/account.php`), thẻ `<label>` hiển thị nhãn Email không chứa thuộc tính `for` liên kết tới định danh `id` của thẻ `<input>`:

```html
<!-- Dòng 26-31 (InlaneWeb/web/src/pages/account.php) - MÃ NGUỒN VI PHẠM -->
<form action="/account/update" method="post">
    <div class="form-row">
        <label>Email</label>
        <input type="text" name="email" value="<?= htmlspecialchars($u['email']) ?>">
    </div>
    <button class="btn" type="submit">Lưu thay đổi</button>
</form>
```

### 3. Cơ chế Phân tích của SonarQube Web Analyzer
* **Động cơ phân tích DOM Tree:** Bộ phân tích `sonar-html-plugin` quét toàn bộ cấu trúc biểu mẫu (Forms) trong mã nguồn giao diện.
* **Nguyên nhân phát hiện vi phạm:** Quy tắc `Web:S6853` yêu cầu mọi phần tử nhãn `<label>` phải được gắn kết tường minh với điều khiển nhập liệu tương ứng bằng thuộc tính `for="control_id"`, hoặc phần tử điều khiển phải được đặt lồng bên trong thẻ `<label>`.
* **Hậu quả kỹ thuật:**
  - Người dùng khiếm thị sử dụng Screen Reader không được thông báo ngữ cảnh khi con trỏ di chuyển vào ô nhập Email.
  - Người dùng phổ thông không thể click vào nhãn để tự động kích hoạt (focus) ô nhập liệu, làm suy giảm tính tiện dụng (Usability) của giao diện Web Portal.

### 4. Tác động tới Quality Gate trong Quy trình CI/CD
* **Chính sách Quality Gate (`ci/sonarqube-quality-gate.json`):**
  - Tỷ lệ nợ kỹ thuật (Technical Debt Ratio) trên mã mới: Yêu cầu `<= 5%`.
  - Mức độ bảo trì mã mới (New Maintainability Rating): Bắt buộc đạt `A`.
* **Kịch bản gãy vỡ (Break-the-Build):** Sự xuất hiện của lỗi Major Code Smell làm gia tăng nợ kỹ thuật trên New Code, khiến chỉ số Maintainability Rating bị hạ xuống mức `B`, kích hoạt trạng thái ❌ **FAILED** của Quality Gate và chặn việc tự động hợp nhất Pull Request.

### 5. Phương án Khắc phục Chuẩn hóa (Clean Code Refactoring)
Thiết lập thuộc tính `id="account-email-input"` trên thẻ `<input>`, đồng thời bổ sung thuộc tính `for="account-email-input"` trên thẻ `<label>` tương ứng:

```html
<!-- Dòng 26-31 (InlaneWeb/web/src/pages/account.php) - MÃ NGUỒN ĐÃ KHẮC PHỤC -->
<form action="/account/update" method="post">
    <div class="form-row">
        <label for="account-email-input">Địa chỉ Email:</label>
        <input id="account-email-input" type="email" name="email" value="<?= htmlspecialchars($u['email'], ENT_QUOTES, 'UTF-8') ?>">
    </div>
    <button class="btn" type="submit">Lưu thay đổi</button>
</form>
```

### 6. Kết quả Thẩm định Sau Khắc phục (Quality Gate Passed)

| Chỉ số Chất lượng (Metrics) | Trước khi Sửa (Dirty State) | Sau khi Sửa (Clean Code State) | Trạng thái Thẩm định |
| :--- | :---: | :---: | :---: |
| **New Major Code Smells** | `1` (Major) | `0` | ✅ Đạt chuẩn (Thỏa mãn = 0) |
| **Maintainability Rating** | `B` | `A` | ✅ Đạt chuẩn Tuyệt đối |
| **SonarQube Quality Gate** | ❌ **FAILED** | 🟢 **PASSED** | ✅ Cho phép Merge Pull Request |

---

## BÀI TOÁN POLICY-AS-CODE (PaC) TRONG QUY TRÌNH DEVSECOPS

Nhằm ngăn chặn các lỗi cấu hình hạ tầng và bí mật cứng (Hardcoded Secrets) lặp lại trên môi trường sản xuất, nhóm đã triển khai giải pháp **Policy-as-Code** tự động hóa tại **Stage 3 (Pre-deployment Validation)** trong tệp `ci/validate_configs.py`:

```python
# ci/validate_configs.py - Thực thi kiểm tra chính sách an toàn IaC tự động:
def test_production_compose_no_hardcoded_passwords(compose_prod_data):
    """Bắt buộc mọi mật khẩu Production phải được truyền qua biến môi trường hoặc Secret."""
    db_env = compose_prod_data.get('services', {}).get('db', {}).get('environment', {})
    root_pass = db_env.get('MYSQL_ROOT_PASSWORD', '')
    
    assert root_pass != 'password', \
        "[POLICY VIOLATION] Phát hiện mật khẩu mặc định 'password' trong cấu hình Production Compose!"
    assert not root_pass or root_pass.startswith('${'), \
        "[POLICY VIOLATION] Mật khẩu CSDL phải được bảo vệ qua biến môi trường bí mật!"
```
* **Ý nghĩa:** Nếu kỹ sư vô tình cấu hình mật khẩu dạng rõ hoặc mở cổng CSDL ra ngoài, GitHub Actions Runner sẽ lập tức đánh rớt Stage 3 và từ chối kích hoạt lệnh CD triển khai lên máy chủ VPS.
