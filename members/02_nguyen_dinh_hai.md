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

Trong mô hình DevSecOps hiện đại, bên cạnh các lỗ hổng an ninh mạng (Security Gate), dự án triển khai quy chuẩn kiểm soát kép **Dual-Gate (Security Gate + Quality Gate)**. Công cụ **SonarQube Scanner** được kích hoạt tại Stage 2 để kiểm tra chuẩn Clean Code và khả năng bảo trì mã nguồn (Maintainability). Bất kỳ vi phạm nghiêm trọng nào thuộc nhóm **Critical Code Smells** trên New Code đều sẽ khiến **SonarQube Quality Gate** bị đánh rớt (**FAILED**) và kích hoạt cơ chế Break-the-Build.

### 1. Tổng quan Lỗi Chất lượng Mã nguồn Phụ trách

| Tiêu chí Thẩm định | Nội dung Chi tiết từ SonarQube Scanner |
| :--- | :--- |
| **Tên vấn đề Code Quality** | **Missing Curly Braces in Nested Control Statement (Clean Code Smell)** |
| **Mã quy tắc vi phạm (Rule Key)** | [`php:S121`](https://rules.sonarsource.com/php/RSPEC-121) |
| **Phân loại vấn đề (Issue Type)** | ♨️ **CODE_SMELL** (Mùi mã nguồn gây rủi ro bảo trì & logic ngầm) |
| **Mức độ nghiêm trọng (Severity)**| 🔴 **CRITICAL** |
| **Tệp tin & Vị trí vi phạm** | [InlaneWeb/web/src/pages/login.php:36](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/pages/login.php#L36) |
| **Phạm vi tiêu chuẩn áp dụng** | **PSR-12 (Coding Style Standard)** & **SonarSource Clean Code Guidelines** |
| **Trạng thái Quality Gate** | ❌ **FAILED** (Vi phạm điều kiện: `No Critical Issues on New Code`) |

### 2. Bằng chứng Mã nguồn Vi phạm (Non-compliant Code)
Tại trang Đăng nhập người dùng (`InlaneWeb/web/src/pages/login.php`), câu lệnh điều khiển `if` hiển thị thông báo lỗi được viết mà không bao bọc bởi cặp dấu ngoặc nhọn `{ }`:

```php
<!-- Dòng 34-37 (InlaneWeb/web/src/pages/login.php) - MÃ NGUỒN VI PHẠM -->
<div class="card" style="max-width:440px;margin:0 auto;">
    <h1>Đăng nhập</h1>
    <?php if ($error) flash($error, 'error'); ?>
    <form action="/login" method="post">
```

### 3. Cơ chế Phân tích của SonarQube PHP Analyzer
* **Động cơ phân tích cú pháp AST:** SonarQube PHP Analyzer phân tích cú pháp trừu tượng của toàn bộ cấu trúc điều khiển (`if`, `else`, `for`, `foreach`, `while`, `do-while`).
* **Nguyên nhân phát hiện vi phạm:** Quy tắc `php:S121` ("Control structures should use curly braces") quy định bắt buộc mọi cấu trúc điều khiển phải dùng cặp dấu ngoặc nhọn `{ }`, ngay cả khi khối lệnh bên trong chỉ có đúng một dòng duy nhất.
* **Hậu quả kỹ thuật:**
  - Vi phạm chuẩn mã nguồn PHP quốc tế **PSR-12**.
  - Tiềm ẩn rủi ro logic nghiêm trọng khi bảo trì mã nguồn trong tương lai (tương tự lỗi bảo mật nổi tiếng `goto fail;` của Apple SSL): Khi một lập trình viên khác thêm dòng mã mới ngay dưới `if` mà không nhận ra nó nằm ngoài khối điều kiện, mã nguồn sẽ thực thi sai hoàn toàn luồng logic mong muốn.

### 4. Tác động tới Quality Gate trong Quy trình CI/CD
* **Chính sách Quality Gate (`ci/sonarqube-quality-gate.json`):**
  - Mức độ vi phạm mới: Không chấp nhận lỗi mới mức **Critical**.
  - Điểm bảo trì mới (New Maintainability Rating): Bắt buộc đạt `A`.
* **Kịch bản gãy vỡ (Break-the-Build):** Vì quy tắc `php:S121` được xếp mức **CRITICAL**, Quality Gate lập tức chuyển trạng thái sang ❌ **FAILED**. Pipeline CI tự động ngắt tại Stage 2 và từ chối cấp quyền Merge Pull Request.

### 5. Phương án Khắc phục Chuẩn hóa (Clean Code Refactoring)
Bổ sung đầy đủ cặp dấu ngoặc nhọn `{ }` bao bọc lệnh `flash()`, đảm bảo khối lệnh rõ ràng, tường minh và tuân thủ tuyệt đối chuẩn PSR-12:

```php
<!-- Dòng 34-41 (InlaneWeb/web/src/pages/login.php) - MÃ NGUỒN ĐÃ KHẮC PHỤC -->
<div class="card" style="max-width:440px;margin:0 auto;">
    <h1>Đăng nhập</h1>
    <?php 
    if ($error) {
        flash($error, 'error'); 
    }
    ?>
    <form action="/login" method="post">
```

### 6. Kết quả Thẩm định Sau Khắc phục (Quality Gate Passed)

| Chỉ số Chất lượng (Metrics) | Trước khi Sửa (Dirty State) | Sau khi Sửa (Clean Code State) | Trạng thái Thẩm định |
| :--- | :---: | :---: | :---: |
| **New Critical Code Smells**| `1` (Critical) | `0` | ✅ Đạt chuẩn (Thỏa mãn = 0) |
| **Maintainability Rating** | `B` | `A` | ✅ Đạt chuẩn Tuyệt đối |
| **SonarQube Quality Gate** | ❌ **FAILED** | 🟢 **PASSED** | ✅ Cho phép Merge Pull Request |

---

## BÀI TOÁN SECURITY-AS-CODE (SaC) TRONG QUY TRÌNH DEVSECOPS

Với vai trò Kỹ sư An ninh Phần mềm, Nguyễn Đình Hải thiết lập các quy tắc **Security-as-Code** nhằm bảo vệ cơ chế xác thực và ngăn chặn bypass:
* **Mã hóa quy tắc kiểm định Taint Analysis:** Viết quy tắc Semgrep tùy biến bắt mọi điểm gọi `mysqli_query` có chứa biến bắt nguồn từ `$_POST['username']` hay `$_GET['no']` mà chưa qua prepared statements.
* **Tích hợp kiểm tra bảo mật tự động:** Đưa quy tắc kiểm tra fallback mật khẩu CSDL `ci.php-hardcoded-db-password-fallback` vào quy trình CI/CD, biến tiêu chuẩn an ninh thành mã kiểm thử thực thi bắt buộc trước khi hợp nhất mã (Pull Request Gate).
