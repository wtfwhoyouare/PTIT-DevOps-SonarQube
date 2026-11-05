# BÁO CÁO PHÂN TÍCH LỖ HỔNG AN TOÀN BẢO MẬT
**Thành viên thực hiện:** Nguyễn Đình Hải  
**Vai trò trong dự án:** Kỹ sư An ninh Phần mềm (Application Security Engineer)  
**Phạm vi phụ trách:** Kiểm định Taint Analysis, Module Xác thực người dùng & Theo dõi Vận đơn  
**Đề tài:** Hệ thống DevSecOps CI/CD kiểm định an ninh tự động cho InlaneWeb Logistics Portal  

---

## PHẦN A: TỔNG HỢP DANH MỤC 4 LỖ HỔNG AN TOÀN BẢO MẬT (SAST - SEMGREP / OWASP / CWE)

| STT | Tên Lỗ hổng | Loại lỗi | Mã CWE | Tệp tin & Vị trí vi phạm | Mức độ cảnh báo | Động cơ phát hiện |
| :---: | :--- | :---: | :---: | :--- | :---: | :---: |
| 1 | **Authentication Bypass SQL Injection** | Code | CWE-89 | `InlaneWeb/web/src/pages/login.php:19` | 🔴 High / ERROR | Semgrep Taint Engine |
| 2 | **XPath Error-based SQL Injection** | Code | CWE-89 | `InlaneWeb/web/src/pages/port_detail.php:19` | 🔴 High / ERROR | Semgrep Taint Engine |
| 3 | **Time-based Blind SQL Injection** | Code | CWE-89 | `InlaneWeb/web/src/pages/track_api.php:18` | 🔴 High / ERROR | Semgrep Taint Engine |
| 4 | **Hardcoded DB Password Fallback** | Code | CWE-798 | `InlaneWeb/web/src/lib/db.php:19` | 🔴 High / ERROR | Semgrep Local Rule |

---

## CHI TIẾT TỪNG LỖ HỔNG BẢO MẬT

### 1. Authentication Bypass SQL Injection tại trang Đăng nhập
* **Vị trí vi phạm:** [InlaneWeb/web/src/pages/login.php:19](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/pages/login.php#L19)
* **Phân loại lỗi:** Mã nguồn (Application Code) | **Pha DevSecOps:** Pha Test / SAST (Stage 2)
* **Mã định danh điểm yếu:** **CWE-89: SQL Injection** | **OWASP Top 10:2021:** A03:2021 — Injection
* **Quy tắc phát hiện:** Semgrep Rule `php.lang.security.injection.tainted-sql-string.tainted-sql-string`

#### a. Bằng chứng mã nguồn vi phạm (Vulnerable Code):
```php
// Nguồn dữ liệu nhận trực tiếp từ form POST
$username = $_POST['username'] ?? '';
$password = $_POST['password'] ?? '';

// Điểm chìm: Nối chuỗi vào truy vấn xác thực
$sql = "SELECT id, username, role FROM users WHERE username = '$username' AND password = '$password'";
$row = query_one($sql);
if ($row) {
    $_SESSION['uid'] = $row['id'];
    header('Location: /account');
    exit;
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
      - pattern: query_one("... WHERE username = '$U' AND password = '$P'", ...)
```

* **Cơ chế phân tích luồng ô nhiễm (Taint / AST Analysis):**
  - **Tệp tin & hàm xử lý:** Tự động phát hiện trong Stage 2 và trích xuất qua script [`ci/semgrep_report.py`](file:///d:/PTIT-DevOps-SonarQube/ci/semgrep_report.py) bằng hàm `extract_source_and_sink(path_str, line_no)`.
  - **🟡 SOURCE (Nguồn dữ liệu người dùng nhập / Khai báo cấu hình):**
```php
// Dòng 15-16 (InlaneWeb/web/src/pages/login.php):
$username = $_POST['username'] ?? '';
$password = $_POST['password'] ?? '';
```
  - **🔴 SINK (Điểm kích hoạt / Thực thi câu lệnh nguy hiểm):**
```php
// Dòng 19-20 (InlaneWeb/web/src/pages/login.php):
$sql = "SELECT id, username, role FROM users WHERE username = '$username' AND password = '$password'";
$row = query_one($sql);
```

#### c. Cách thức xử lý & Khắc phục (Remediation):
Tách biệt hoàn toàn việc kiểm tra người dùng và băm mật khẩu bảo mật:
```php
// 1. Dùng Prepared Statement tìm tài khoản
$stmt = db()->prepare("SELECT id, username, password, role FROM users WHERE username = ?");
$stmt->bind_param("s", $username);
$stmt->execute();
$user = $stmt->get_result()->fetch_assoc();

// 2. So khớp mật khẩu bằng hàm băm an toàn Bcrypt/Argon2
if ($user && password_verify($password, $user['password'])) {
    session_regenerate_id(true); // Chống Session Fixation
    $_SESSION['uid'] = $user['id'];
    header('Location: /account');
    exit;
}
```

#### e. Đánh giá Vi phạm Chính sách & Bài toán Security-as-Code (SaC):
* **Pha trong quy trình DevSecOps:** **Pha Test / SAST Gate (Stage 2 trong CI/CD Pipeline)**
  - *Đánh giá rủi ro:* Lỗi nằm tại phân hệ xác thực đăng nhập người dùng. Việc cho phép chèn cú pháp SQL cho phép kẻ tấn công bỏ qua bước kiểm tra mật khẩu, chiếm đoạt tài khoản quản trị mà không cần thông tin đăng nhập hợp lệ.
* **Căn cứ vi phạm chính sách pháp lý:**
  - **Nghị định 13/2023/NĐ-CP:** Điều 9 Khoản 2 & Điều 17 (Vi phạm nghiêm trọng nghĩa vụ bảo đảm an ninh hệ thống xác thực người dùng, gây nguy cơ chiếm đoạt quyền quản trị).
  - **GDPR (Châu Âu):** Article 32 — Security of Processing (Không đảm bảo khả năng duy trì tính bí mật và tính xác thực của hệ thống xử lý dữ liệu).
* **Hiện thực hóa Bài toán Security-as-Code (SaC):**
  - Quy tắc kiểm tra cú pháp truy vấn đăng nhập bắt buộc phải sử dụng Prepared Statement:
```yaml
# Kiểm định SaC bắt buộc tham số hóa câu truy vấn xác thực
- id: php.lang.security.injection.tainted-sql-string.tainted-sql-string
  languages: [php]
  severity: ERROR
  mode: taint
  pattern-sources: [pattern: $_POST['username']]
  pattern-sinks: [pattern: query_one("... WHERE username = '$U' AND password = '$P'", ...)]
```

---

### 2. XPath Error-based SQL Injection tại trang Chi tiết Cảng biển
* **Vị trí vi phạm:** [InlaneWeb/web/src/pages/port_detail.php:19](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/pages/port_detail.php#L19)
* **Phân loại lỗi:** Mã nguồn (Application Code) | **Pha DevSecOps:** Pha Test / SAST (Stage 2)
* **Mã định danh điểm yếu:** **CWE-89: SQL Injection**
* **Quy tắc phát hiện:** Semgrep Rule `php.lang.security.injection.tainted-sql-string.tainted-sql-string`

#### a. Bằng chứng mã nguồn vi phạm (Vulnerable Code):
```php
$code = $_GET['code'] ?? '';
// Nối chuỗi code vào câu truy vấn
$sql = "SELECT code, city, country, volume FROM ports WHERE code = '$code'";
echo '<div class="query-box">' . htmlspecialchars($sql) . '</div>';
$row = query_one($sql);
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
      - pattern: query_one("... WHERE code = '$CODE'", ...)
```

* **Cơ chế phân tích luồng ô nhiễm (Taint / AST Analysis):**
  - **Tệp tin & hàm xử lý:** Tự động phát hiện trong Stage 2 và trích xuất qua script [`ci/semgrep_report.py`](file:///d:/PTIT-DevOps-SonarQube/ci/semgrep_report.py) bằng hàm `extract_source_and_sink(path_str, line_no)`.
  - **🟡 SOURCE (Nguồn dữ liệu người dùng nhập / Khai báo cấu hình):**
```php
// Dòng 13 (InlaneWeb/web/src/pages/port_detail.php):
$code = $_GET['code'] ?? '';
```
  - **🔴 SINK (Điểm kích hoạt / Thực thi câu lệnh nguy hiểm):**
```php
// Dòng 19-21 (InlaneWeb/web/src/pages/port_detail.php):
$sql = "SELECT code, city, country, volume FROM ports WHERE code = '$code'";
$p = query_one($sql);
```

#### c. Cách thức xử lý & Khắc phục (Remediation):
```php
$stmt = db()->prepare("SELECT code, city, country, volume FROM ports WHERE code = ?");
$stmt->bind_param("s", $code);
$stmt->execute();
$row = $stmt->get_result()->fetch_assoc();
// Tắt in chi tiết lỗi SQL ra giao diện, chỉ ghi log nội bộ
```

#### e. Đánh giá Vi phạm Chính sách & Bài toán Security-as-Code (SaC):
* **Pha trong quy trình DevSecOps:** **Pha Test / SAST Gate (Stage 2 trong CI/CD Pipeline)**
  - *Đánh giá rủi ro:* Lỗi nằm ở module hiển thị chi tiết cảng biển. Khi kẻ tấn công chèn cú pháp XPath Error, cơ sở dữ liệu trả về thông báo lỗi chứa dữ liệu nội bộ trực tiếp ra màn hình, làm lộ cấu trúc hệ thống.
* **Căn cứ vi phạm chính sách pháp lý:**
  - **Nghị định 13/2023/NĐ-CP:** Điều 13 Khoản 2 (Vi phạm quy định bảo mật thông tin nội bộ hệ thống, để lộ lọt mã băm mật khẩu và cấu trúc CSDL ra ngoài).
  - **GDPR (Châu Âu):** Article 32 (Không áp dụng biện pháp kỹ thuật ngăn chặn rò rỉ thông tin qua kênh thông báo lỗi hệ thống).
* **Hiện thực hóa Bài toán Security-as-Code (SaC):**
  - Tự động phát hiện việc truyền tham số GET ô nhiễm vào câu truy vấn và kiểm soát lỗi SQL:
```yaml
# Taint tracking phát hiện điểm ghép chuỗi và cảnh báo Error-based SQLi
- id: php.lang.security.injection.tainted-sql-string.tainted-sql-string
  languages: [php]
  severity: ERROR
  mode: taint
  pattern-sources: [pattern: $_GET['code']]
  pattern-sinks: [pattern: query_one("... WHERE code = '$CODE'", ...)]
```

---

### 3. Time-based Blind SQL Injection tại API Tra cứu Vận đơn
* **Vị trí vi phạm:** [InlaneWeb/web/src/pages/track_api.php:18](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/pages/track_api.php#L18)
* **Phân loại lỗi:** Mã nguồn (Application Code) | **Pha DevSecOps:** Pha Test / SAST (Stage 2)
* **Mã định danh điểm yếu:** **CWE-89: SQL Injection**
* **Quy tắc phát hiện:** Semgrep Rule `php.lang.security.injection.tainted-sql-string.tainted-sql-string`

#### a. Bằng chứng mã nguồn vi phạm (Vulnerable Code):
```php
$tracking = $_GET['tracking'] ?? '';
// Điểm inject mù theo thời gian (Blind Time-based)
$sql = "SELECT tracking_no, port_code, status FROM shipments WHERE tracking_no = '$tracking'";
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
      - pattern: query("... WHERE tracking_no = '$TRACKING'", ...)
```

* **Cơ chế phân tích luồng ô nhiễm (Taint / AST Analysis):**
  - **Tệp tin & hàm xử lý:** Tự động phát hiện trong Stage 2 và trích xuất qua script [`ci/semgrep_report.py`](file:///d:/PTIT-DevOps-SonarQube/ci/semgrep_report.py) bằng hàm `extract_source_and_sink(path_str, line_no)`.
  - **🟡 SOURCE (Nguồn dữ liệu người dùng nhập / Khai báo cấu hình):**
```php
// Dòng 15 (InlaneWeb/web/src/pages/track_api.php):
$tracking = $_GET['tracking'] ?? '';
```
  - **🔴 SINK (Điểm kích hoạt / Thực thi câu lệnh nguy hiểm):**
```php
// Dòng 18-19 (InlaneWeb/web/src/pages/track_api.php):
$sql = "SELECT tracking_no, port_code, status FROM shipments WHERE tracking_no = '$tracking'";
$res = query($sql);
```

#### c. Cách thức xử lý & Khắc phục (Remediation):
```php
$stmt = db()->prepare("SELECT tracking_no, port_code, status FROM shipments WHERE tracking_no = ?");
$stmt->bind_param("s", $tracking);
$stmt->execute();
$res = $stmt->get_result();
```

---

### 4. Hardcoded Database Password Fallback trong Kết nối CSDL
* **Vị trí vi phạm:** [InlaneWeb/web/src/lib/db.php:19](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/lib/db.php#L19)
* **Phân loại lỗi:** Quản lý thông tin bí mật (Secrets Management) | **Pha DevSecOps:** Pha Code (Stage 2)
* **Mã định danh điểm yếu:** **CWE-798: Use of Hard-coded Credentials**
* **Quy tắc phát hiện:** Semgrep Rule `ci.php-hardcoded-db-password-fallback`

#### a. Bằng chứng mã nguồn vi phạm:
```php
$host = getenv('DB_HOST') ?: 'db';
$user = getenv('DB_USER') ?: 'root';
$pass = getenv('DB_PASS') ?: 'password'; // Nguy cơ fallback mật khẩu cố định
$name = getenv('DB_NAME') ?: 'ilfreight';
```

#### b. Cơ chế phát hiện & Trích xuất mã nguồn (Detection Mechanism):
* **Quy tắc Semgrep quét phát hiện (Rule Definition Code):**
```yaml
rules:
  - id: php-hardcoded-db-password-fallback
    languages: [php]
    severity: ERROR
    message: A database password has a hardcoded fallback. Require a secret from the environment instead.
    patterns:
      - pattern: "getenv('DB_PASS') ?: $FALLBACK"
      - metavariable-regex:
          metavariable: $FALLBACK
          regex: ^['"].+['"]$
```

* **Cơ chế phân tích luồng ô nhiễm (Taint / AST Analysis):**
  - **Tệp tin & hàm xử lý:** Tự động phát hiện trong Stage 2 và trích xuất qua script [`ci/semgrep_report.py`](file:///d:/PTIT-DevOps-SonarQube/ci/semgrep_report.py) bằng hàm `extract_source_and_sink(path_str, line_no)`.
  - **🟡 SOURCE (Nguồn dữ liệu người dùng nhập / Khai báo cấu hình):**
```php
// InlaneWeb/web/src/lib/db.php: Thiết lập thông tin kết nối CSDL
```
  - **🔴 SINK (Điểm kích hoạt / Thực thi câu lệnh nguy hiểm):**
```php
// Dòng 19 (InlaneWeb/web/src/lib/db.php):
$pass = getenv('DB_PASS') ?: 'password';
```

#### c. Cách thức xử lý & Khắc phục (Remediation):
```php
$pass = getenv('DB_PASS');
if ($pass === false || $pass === '') {
    throw new RuntimeException("LỖI BẢO MẬT: Biến môi trường DB_PASS chưa được thiết lập!");
}
```

#### e. Đánh giá Vi phạm Chính sách & Bài toán Policy-as-Code (PaC):
* **Pha trong quy trình DevSecOps:** **Pha Plan / Code (Stage 1) & Secret Scan (Stage 2)**
  - *Đánh giá rủi ro:* Lỗi nằm ở thư viện kết nối database cốt lõi. Việc tự động fallback về mật khẩu mặc định khi thiếu biến môi trường tạo nguy cơ hệ thống hoạt động với thông tin xác thực yếu trên môi trường staging hoặc production.
* **Căn cứ vi phạm chính sách pháp lý:**
  - **Nghị định 13/2023/NĐ-CP:** Điều 13 Khoản 1 (Không áp dụng biện pháp bảo vệ dữ liệu xác thực ngay từ khâu thiết kế hệ thống).
  - **GDPR (Châu Âu):** Article 5(1)(f) & Article 25 (Vi phạm nguyên tắc bảo mật và quản lý thông tin xác thực an toàn theo thiết kế).
* **Hiện thực hóa Bài toán Policy-as-Code (PaC):**
  - Quy tắc kiểm tra cấu hình mã nguồn chặn triệt để cú pháp gán mật khẩu dự phòng tĩnh:
```yaml
# ci/semgrep-local-rules.yml: Chặn fallback mật khẩu CSDL tĩnh
- id: php-hardcoded-db-password-fallback
  languages: [php]
  severity: ERROR
  patterns:
    - pattern: "getenv('DB_PASS') ?: $FALLBACK"
    - metavariable-regex:
        metavariable: $FALLBACK
        regex: ^['"].+['"]$
```

---

## PHẦN B: KIỂM ĐỊNH CHẤT LƯỢNG MÃ NGUỒN (SONARQUBE CODE QUALITY)

Trong mô hình DevSecOps hiện đại, bên cạnh các lỗ hổng an ninh mạng (Security Gate), dự án triển khai quy chuẩn kiểm soát kép **Dual-Gate (Security Gate + Quality Gate)**. Công cụ **SonarQube Scanner** được kích hoạt tại Stage 2 để kiểm tra toàn diện chuẩn Clean Code PSR, độ tin cậy và khả năng bảo trì mã nguồn (Maintainability).

Bất kỳ vi phạm nghiêm trọng nào thuộc nhóm **Critical Code Smells** hoặc **New Bugs** trên New Code đều sẽ khiến **SonarQube Quality Gate** bị đánh rớt (**FAILED**) và kích hoạt cơ chế ngắt tiến trình (Break-the-Build).

Phân hệ phụ trách của Nguyễn Đình Hải gồm **03 lỗi chất lượng mã nguồn thực tế** được SonarQube ghi nhận trong `reports/sonarqube_ci/issues.json`:

### 1. Bảng Tổng hợp 03 Lỗi Code Quality Phụ trách

| Mã | Tên Vấn đề Code Quality | Tệp & Vị trí Vi phạm | Quy tắc SonarQube | Phân loại | Mức độ | Tiêu chuẩn Vi phạm |
| :---: | :--- | :--- | :--- | :---: | :---: | :--- |
| **CQ-01** | Missing Curly Braces in Nested Statement | [login.php:36](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/pages/login.php#L36) | `php:S121` | 🧹 CODE_SMELL | 🔴 CRITICAL | PSR-12 Control Structures Standard |
| **CQ-02** | Login Form Username Input Missing ID & Label | [login.php:40](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/pages/login.php#L40) | `Web:InputWithoutLabelCheck` | 🐞 BUG | 🟠 MAJOR | WCAG 2.1 Level A (Criteria 1.3.1) |
| **CQ-03** | Database Function Naming Violates camelCase | [db.php:55](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/lib/db.php#L55) | `php:S100` | 🧹 CODE_SMELL | 🟡 MINOR | PSR-1 / PSR-12 Method Naming |

---

### 2. Chi tiết Từng Lỗi Chất lượng Mã nguồn & Kịch bản Khắc phục

#### CQ-01: Missing Curly Braces in Nested Statement (Clean Code Smell)
* **Vị trí vi phạm:** [InlaneWeb/web/src/pages/login.php:36](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/pages/login.php#L36)
* **Quy tắc SonarQube:** [`php:S121`](https://rules.sonarsource.com/php/RSPEC-121) (Critical Code Smell)
* **Bằng chứng mã nguồn vi phạm (Non-compliant Code):**
```php
// Dòng 35-37 (InlaneWeb/web/src/pages/login.php) - MÃ NGUỒN VI PHẠM
<h1>Đăng nhập</h1>
<?php if ($error) flash($error, 'error'); ?>
<form action="/login" method="post">
```
* **Cơ chế phân tích của SonarQube:** Khối lệnh `if` lồng nhau không sử dụng cặp dấu ngoặc nhọn `{ }` để bao bọc phạm vi thực thi. Quy chuẩn mã nguồn sạch PSR-12 và SonarQube Clean Code yêu cầu tất cả các khối điều khiển rẽ nhánh phải có dấu ngoặc bảo vệ, tránh các lỗi logic ngầm nguy hiểm khi lập trình viên khác bổ sung câu lệnh vào nhánh điều kiện.
* **Phương án khắc phục chuẩn hóa (Clean Code Refactoring):**
```php
// Dòng 35-39 (InlaneWeb/web/src/pages/login.php) - MÃ NGUỒN ĐÃ KHẮC PHỤC
<h1>Đăng nhập</h1>
<?php if ($error) {
    flash($error, 'error');
} ?>
<form action="/login" method="post">
```

---

#### CQ-02: Login Form Username Input Missing ID & Label Association (Web Accessibility Bug)
* **Vị trí vi phạm:** [InlaneWeb/web/src/pages/login.php:40](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/pages/login.php#L40)
* **Quy tắc SonarQube:** [`Web:InputWithoutLabelCheck`](https://rules.sonarsource.com/html/RSPEC-InputWithoutLabelCheck) (Major Bug)
* **Bằng chứng mã nguồn vi phạm (Non-compliant Code):**
```html
<!-- Dòng 38-41 (InlaneWeb/web/src/pages/login.php) - MÃ NGUỒN VI PHẠM -->
<div class="form-row">
    <label>Tên đăng nhập</label>
    <input type="text" name="username" autofocus>
</div>
```
* **Cơ chế phân tích của SonarQube:** Thẻ `<label>` đứng độc lập không có thuộc tính `for` và trường `<input>` thiếu thuộc tính `id`. Theo WCAG 2.1 Criteria 1.3.1 (Info and Relationships), phần tử nhãn không liên kết ngữ nghĩa với phần tử điều khiển, gây lỗi giao diện trợ năng trên các trình duyệt hiện đại.
* **Phương án khắc phục chuẩn hóa (Clean Code Refactoring):**
```html
<!-- Dòng 38-41 (InlaneWeb/web/src/pages/login.php) - MÃ NGUỒN ĐÃ KHẮC PHỤC -->
<div class="form-row">
    <label for="login-username">Tên đăng nhập</label>
    <input id="login-username" type="text" name="username" autofocus>
</div>
```

---

#### CQ-03: Database Helper Function Naming Violates PSR-1 camelCase (Clean Code Smell)
* **Vị trí vi phạm:** [InlaneWeb/web/src/lib/db.php:55](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/lib/db.php#L55)
* **Quy tắc SonarQube:** [`php:S100`](https://rules.sonarsource.com/php/RSPEC-100) (Minor Code Smell)
* **Bằng chứng mã nguồn vi phạm (Non-compliant Code):**
```php
// Dòng 54-56 (InlaneWeb/web/src/lib/db.php) - MÃ NGUỒN VI PHẠM
/** exec_write() — chay INSERT/UPDATE/DELETE/CREATE (khong tra row). */
function exec_write(string $sql): bool
{
```
* **Cơ chế phân tích của SonarQube:** Tên hàm `exec_write` chứa ký tự gạch dưới (snake_case), vi phạm biểu thức chính quy chuẩn của SonarQube `^[a-z][a-zA-Z0-9]*$` và quy chuẩn PSR-1 (Basic Coding Standard) quy định phương thức/hàm tiện ích phải được đặt tên theo quy ước camelCase.
* **Phương án khắc phục chuẩn hóa (Clean Code Refactoring):**
```php
// Dòng 54-56 (InlaneWeb/web/src/lib/db.php) - MÃ NGUỒN ĐÃ KHẮC PHỤC
/** execWrite() — chạy INSERT/UPDATE/DELETE/CREATE (không trả row). */
function execWrite(string $sql): bool
{
```

---

### 3. Kết quả Thẩm định Chất lượng SonarQube Trước & Sau Khắc phục

| Chỉ số Chất lượng (Metrics) | Trước khi Sửa (Dirty State) | Sau khi Sửa (Clean Code State) | Trạng thái Thẩm định |
| :--- | :---: | :---: | :---: |
| **New Critical Code Smells**| `1` (php:S121) | `0` | ✅ Đạt chuẩn (Thỏa mãn = 0) |
| **New Bugs** | `1` (Major) | `0` | ✅ Đạt chuẩn (Thỏa mãn = 0) |
| **Maintainability Rating** | `B` | `A` | ✅ Đạt chuẩn Tuyệt đối |
| **SonarQube Quality Gate** | ❌ **FAILED** | 🟢 **PASSED** | ✅ Cho phép Merge Pull Request |

---
## BÀI TOÁN SECURITY-AS-CODE (SaC) TRONG QUY TRÌNH DEVSECOPS

Với vai trò Kỹ sư An ninh Phần mềm, Nguyễn Đình Hải thiết lập các quy tắc **Security-as-Code** nhằm bảo vệ cơ chế xác thực và ngăn chặn bypass:
* **Mã hóa quy tắc kiểm định Taint Analysis:** Viết quy tắc Semgrep tùy biến bắt mọi điểm gọi `mysqli_query` có chứa biến bắt nguồn từ `$_POST['username']` hay `$_GET['no']` mà chưa qua prepared statements.
* **Tích hợp kiểm tra bảo mật tự động:** Đưa quy tắc kiểm tra fallback mật khẩu CSDL `ci.php-hardcoded-db-password-fallback` vào quy trình CI/CD, biến tiêu chuẩn an ninh thành mã kiểm thử thực thi bắt buộc trước khi hợp nhất mã (Pull Request Gate).
