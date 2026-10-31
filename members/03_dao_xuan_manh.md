# BÁO CÁO PHÂN TÍCH LỖ HỔNG AN TOÀN BẢO MẬT
**Thành viên thực hiện:** Đào Xuân Mạnh  
**Vai trò trong dự án:** Kỹ sư Kiểm định Chất lượng & Bảo mật (QA / DevSecOps Engineer)  
**Phạm vi phụ trách:** Kiểm soát Quality Gate, Module Cẩm nang Hàng hải & Hệ thống Kết xuất Báo cáo  
**Đề tài:** Hệ thống DevSecOps CI/CD kiểm định an ninh tự động cho InlaneWeb Logistics Portal  

---

## PHẦN A: TỔNG HỢP DANH MỤC 4 LỖ HỔNG AN TOÀN BẢO MẬT (SAST - SEMGREP / OWASP / CWE)

| STT | Tên Lỗ hổng | Loại lỗi | Mã CWE | Tệp tin & Vị trí vi phạm | Mức độ cảnh báo | Động cơ phát hiện |
| :---: | :--- | :---: | :---: | :--- | :---: | :---: |
| 1 | **Local File Inclusion (Path Traversal)** | Code | CWE-22 | `InlaneWeb/web/src/pages/guide.php:54` | 🟡 WARNING | Semgrep (`tainted-filename`) |
| 2 | **PHP Stream Wrapper Inclusion** | Code | CWE-98 | `InlaneWeb/web/src/pages/guide.php:56` | 🔴 High / ERROR | Semgrep (`ci.php-dynamic-file-inclusion`) & SonarQube |
| 3 | **Arbitrary File Read via `LOAD_FILE`** | Code | CWE-89 / CWE-22 | `InlaneWeb/web/src/pages/report_download.php:36` | 🔴 High / ERROR | Semgrep Taint Engine |
| 4 | **DDL SQL Injection (Báo cáo Quản trị)** | Code | CWE-89 | `InlaneWeb/web/src/pages/admin_report_export.php:27` | 🔴 High / ERROR | Semgrep Taint Engine |

---

## CHI TIẾT TỪNG LỖ HỔNG BẢO MẬT

### 1. Local File Inclusion (Path Traversal) tại Cẩm nang Quy chuẩn
* **Vị trí vi phạm:** [InlaneWeb/web/src/pages/guide.php:54](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/pages/guide.php#L54)
* **Phân loại lỗi:** Mã nguồn (Application Code) | **Pha DevSecOps:** Pha Build / Gate (Stage 2)
* **Mã định danh điểm yếu:** **CWE-22: Improper Limitation of a Pathname to a Restricted Directory**
* **Quy tắc phát hiện:** Semgrep Rule `php.lang.security.injection.tainted-filename.tainted-filename`

#### a. Bằng chứng mã nguồn vi phạm (Vulnerable Code):
```php
$doc = $_GET['doc'] ?? 'incoterms2020.html';

// Đường dẫn tệp phụ thuộc trực tiếp vào tham số đầu vào doc
if (str_starts_with($doc, 'php://') || str_starts_with($doc, 'data://') || str_starts_with($doc, '/')) {
    $target_file = $doc;
} else {
    $target_file = __DIR__ . '/../guides/' . $doc;
}

// Điểm chìm kích hoạt nạp tệp:
if (@file_exists($target_file) || str_contains($doc, '..')) {
    include $target_file; // Thực thi nạp tệp
}
```

#### b. Cơ chế phát hiện & Trích xuất mã nguồn (Detection Mechanism):
* **Quy tắc Semgrep quét phát hiện (Rule Definition Code):**
```yaml
rules:
  - id: php.lang.security.injection.tainted-filename.tainted-filename
    languages: [php]
    severity: WARNING
    mode: taint
    pattern-sources:
      - pattern: $_GET[...]
    pattern-sinks:
      - pattern: file_exists($PATH)
      - pattern: is_file($PATH)
```

* **Cơ chế phân tích luồng ô nhiễm (Taint / AST Analysis):**
  - **Tệp tin & hàm xử lý:** Tự động phát hiện trong Stage 2 và trích xuất qua script [`ci/semgrep_report.py`](file:///d:/PTIT-DevOps-SonarQube/ci/semgrep_report.py) bằng hàm `extract_source_and_sink(path_str, line_no)`.
  - **🟡 SOURCE (Nguồn dữ liệu người dùng nhập / Khai báo cấu hình):**
```php
// Dòng 22 (InlaneWeb/web/src/pages/guide.php):
$doc = $_GET['doc'] ?? 'incoterms2020.html';
```
  - **🔴 SINK (Điểm kích hoạt / Thực thi câu lệnh nguy hiểm):**
```php
// Dòng 54 (InlaneWeb/web/src/pages/guide.php):
if (@file_exists($target_file) || str_contains($doc, '..') || str_starts_with($doc, 'php://') || str_starts_with($doc, 'data://')) {
```

#### c. Cách thức xử lý & Khắc phục (Remediation):
Sử dụng hàm lọc tên tệp `basename()` kết hợp với cơ chế **Whitelist danh mục tài liệu cho phép**:
```php
$allowed_docs = [
    'incoterms2020.html',
    'bill_of_lading.html',
    'customs_procedure.html',
    'dangerous_goods.html'
];

$doc = basename($_GET['doc'] ?? 'incoterms2020.html');
if (!in_array($doc, $allowed_docs, true)) {
    die('<div class="sql-error">LỖI: Tài liệu không nằm trong danh mục cho phép!</div>');
}
include __DIR__ . '/../guides/' . $doc;
```

#### e. Đánh giá Vi phạm Chính sách & Bài toán Security-as-Code (SaC):
* **Pha trong quy trình DevSecOps:** **Pha Build & Quality Gate (Stage 2 trong CI/CD Pipeline)**
  - *Đánh giá rủi ro:* Lỗi nằm ở module cẩm nang quy chuẩn. Việc cho phép tham số đường dẫn chứa ký tự điều hướng thư mục (`..`) tạo nguy cơ kẻ tấn công đọc trộm các tệp cấu hình hệ thống nhạy cảm như `/etc/passwd` hoặc mã nguồn PHP.
* **Căn cứ vi phạm chính sách pháp lý:**
  - **Nghị định 13/2023/NĐ-CP:** Điều 13 Khoản 2 (Vi phạm quy định bảo vệ bí mật thông tin hệ thống và dữ liệu cá nhân lưu trữ trên máy chủ).
  - **GDPR (Châu Âu):** Article 32 — Security of Processing (Không bảo đảm khả năng cô lập dữ liệu và hạn chế truy cập tệp tin ngoài phạm vi cho phép).
* **Hiện thực hóa Bài toán Security-as-Code (SaC):**
  - Tích hợp ngưỡng chặn tự động SonarQube Quality Gate và quy tắc Semgrep Taint Filename:
```json
// ci/sonarqube-quality-gate.json: Chặn đứng khi phát hiện lỗ hổng mức Blocker/Critical
{
  "conditions": [
    {"metric": "new_blocker_violations", "op": "GT", "error": "0"},
    {"metric": "new_critical_violations", "op": "GT", "error": "0"}
  ]
}
```

---

### 2. PHP Stream Wrapper Arbitrary Source Code Disclosure
* **Vị trí vi phạm:** [InlaneWeb/web/src/pages/guide.php:56](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/pages/guide.php#L56)
* **Phân loại lỗi:** Mã nguồn (Application Code) | **Pha DevSecOps:** Pha Build / Gate (Stage 2)
* **Mã định danh điểm yếu:** **CWE-98: Improper Control of Generation of Code ('PHP Remote File Inclusion')**
* **Quy tắc phát hiện:** Semgrep Custom Rule `ci.php-dynamic-file-inclusion` (Blocking ERROR) & SonarQube Rule `php:S2003`

#### a. Bằng chứng mã nguồn vi phạm:
Ứng dụng cho phép các giao thức giả lập dòng dữ liệu (`php://filter`, `data://`) đi vào hàm `include`, bypass hoàn toàn việc thực thi mã PHP để trả về mã nguồn dạng Base64:
```php
include $target_file; // Khi target_file là wrapper php://filter/convert.base64-encode/resource=...
```

#### b. Cơ chế phát hiện & Trích xuất mã nguồn (Detection Mechanism):
* **Quy tắc Semgrep quét phát hiện (Rule Definition Code):**
```yaml
rules:
  - id: php-dynamic-file-inclusion
    languages: [php]
    severity: ERROR
    message: Dynamic file inclusion via user-controllable variable. This creates potential Local File Inclusion (LFI) or PHP Stream Wrapper (CWE-98) vulnerabilities.
    patterns:
      - pattern-either:
          - pattern: include $VAR;
          - pattern: include_once $VAR;
          - pattern: require $VAR;
          - pattern: require_once $VAR;
      - pattern-not: require __DIR__ . $EXPR;
      - pattern-not: include __DIR__ . $EXPR;
```

* **Cơ chế phân tích luồng ô nhiễm (Taint / AST Analysis):**
  - **Tệp tin & hàm xử lý:** Tự động phát hiện trong Stage 2 và trích xuất qua script [`ci/semgrep_report.py`](file:///d:/PTIT-DevOps-SonarQube/ci/semgrep_report.py) bằng hàm `extract_source_and_sink(path_str, line_no)`.
  - **🟡 SOURCE (Nguồn dữ liệu người dùng nhập / Khai báo cấu hình):**
```php
// Dòng 22 (InlaneWeb/web/src/pages/guide.php):
$doc = $_GET['doc'] ?? 'incoterms2020.html';
```
  - **🔴 SINK (Điểm kích hoạt / Thực thi câu lệnh nguy hiểm):**
```php
// Dòng 56 (InlaneWeb/web/src/pages/guide.php):
include $target_file;
```

#### c. Cách thức xử lý & Khắc phục (Remediation):
Nghiêm cấm hoàn toàn các giao thức wrapper trong tham số tệp:
```php
if (str_contains($doc, '://') || str_contains($doc, '..')) {
    http_response_code(400);
    die('Yêu cầu không hợp lệ.');
}
```

---

### 3. Arbitrary File Read & Out-of-band Exfiltration qua hàm `LOAD_FILE`
* **Vị trí vi phạm:** [InlaneWeb/web/src/pages/report_download.php:36](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/pages/report_download.php#L36)
* **Phân loại lỗi:** Mã nguồn (Application Code) | **Pha DevSecOps:** Pha Test / SAST (Stage 2)
* **Mã định danh điểm yếu:** **CWE-89: SQL Injection / CWE-22: Path Traversal**
* **Quy tắc phát hiện:** Semgrep Rule `php.lang.security.injection.tainted-sql-string.tainted-sql-string`

#### a. Bằng chứng mã nguồn vi phạm:
```php
$ref = $_GET['ref'] ?? '';
// Nối chuỗi trực tiếp vào hàm đọc tệp của MariaDB LOAD_FILE
$sql = "SELECT LOAD_FILE(CONCAT('/var/lib/mysql-files/', '$ref')) AS doc";
echo '<div class="query-box">' . htmlspecialchars($sql) . '</div>';
$res = mysqli_query($conn, $sql);
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
      - pattern: query("... LOAD_FILE(...) ...", ...)
```

* **Cơ chế phân tích luồng ô nhiễm (Taint / AST Analysis):**
  - **Tệp tin & hàm xử lý:** Tự động phát hiện trong Stage 2 và trích xuất qua script [`ci/semgrep_report.py`](file:///d:/PTIT-DevOps-SonarQube/ci/semgrep_report.py) bằng hàm `extract_source_and_sink(path_str, line_no)`.
  - **🟡 SOURCE (Nguồn dữ liệu người dùng nhập / Khai báo cấu hình):**
```php
// Dòng 27 (InlaneWeb/web/src/pages/report_download.php):
$ref = $_GET['ref'] ?? '';
```
  - **🔴 SINK (Điểm kích hoạt / Thực thi câu lệnh nguy hiểm):**
```php
// Dòng 36-38 (InlaneWeb/web/src/pages/report_download.php):
$sql = "SELECT LOAD_FILE(CONCAT('/var/lib/mysql-files/', '$ref')) AS doc";
$res = query($sql);
```

#### c. Cách thức xử lý & Khắc phục (Remediation):
* Sử dụng Prepared Statement và kiểm tra nghiêm ngặt mã tham chiếu `ref`:
```php
if (!preg_match('/^[A-Z0-9_-]+$/', $ref)) {
    die('Mã báo cáo không đúng định dạng.');
}
// Thu hồi quyền FILE của tài khoản database để ngăn chặn LOAD_FILE / INTO OUTFILE
```

---

### 4. DDL SQL Injection trong tính năng Xuất Báo cáo Quản trị
* **Vị trí vi phạm:** [InlaneWeb/web/src/pages/admin_report_export.php:27](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/pages/admin_report_export.php#L27)
* **Phân loại lỗi:** Mã nguồn (Application Code) | **Pha DevSecOps:** Pha Test / SAST (Stage 2)
* **Mã định danh điểm yếu:** **CWE-89: SQL Injection (DDL Context)**
* **Quy tắc phát hiện:** Semgrep Rule `php.lang.security.injection.tainted-sql-string.tainted-sql-string`

#### a. Bằng chứng mã nguồn vi phạm:
```php
$name = $_POST['report_name'] ?? '';
// Nối tên báo cáo vào lệnh định nghĩa dữ liệu CREATE TABLE
$sql = "CREATE TABLE report_$name AS SELECT tracking_no, status FROM shipments";
exec_write($sql);
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
      - pattern: exec_write("CREATE TABLE ... $NAME ...", ...)
```

* **Cơ chế phân tích luồng ô nhiễm (Taint / AST Analysis):**
  - **Tệp tin & hàm xử lý:** Tự động phát hiện trong Stage 2 và trích xuất qua script [`ci/semgrep_report.py`](file:///d:/PTIT-DevOps-SonarQube/ci/semgrep_report.py) bằng hàm `extract_source_and_sink(path_str, line_no)`.
  - **🟡 SOURCE (Nguồn dữ liệu người dùng nhập / Khai báo cấu hình):**
```php
// Dòng 25 (InlaneWeb/web/src/pages/admin_report_export.php):
$name = $_POST['report_name'] ?? '';
```
  - **🔴 SINK (Điểm kích hoạt / Thực thi câu lệnh nguy hiểm):**
```php
// Dòng 27-30 (InlaneWeb/web/src/pages/admin_report_export.php):
$sql = "CREATE TABLE report_$name AS SELECT tracking_no, status FROM shipments";
if (exec_write($sql)) {
```

#### c. Cách thức xử lý & Khắc phục (Remediation):
Kiểm tra tên bảng bằng biểu thức chính quy chữ cái an toàn:
```php
if (!preg_match('/^[a-zA-Z0-9_]{3,30}$/', $name)) {
    die('Tên bảng báo cáo không hợp lệ.');
}
$safe_name = preg_replace('/[^a-zA-Z0-9_]/', '', $name);
$sql = "CREATE TABLE `report_" . $safe_name . "` AS SELECT tracking_no, status FROM shipments";
```

#### e. Đánh giá Vi phạm Chính sách & Bài toán Security-as-Code (SaC):
* **Pha trong quy trình DevSecOps:** **Pha Test / SAST Gate (Stage 2 trong CI/CD Pipeline)**
  - *Đánh giá rủi ro:* Lỗi nằm tại chức năng kết xuất báo cáo quản trị. Việc nối chuỗi tên bảng vào câu lệnh DDL `CREATE TABLE` cho phép kẻ tấn công chèn các câu lệnh phá hủy bảng dữ liệu.
* **Căn cứ vi phạm chính sách pháp lý:**
  - **Nghị định 13/2023/NĐ-CP:** Điều 9 Khoản 1 & Điều 13 (Vi phạm quy định bảo vệ tính toàn vẹn của dữ liệu cá nhân, để kẻ xấu chèn lệnh phá hủy dữ liệu).
  - **GDPR (Châu Âu):** Article 32 (Không áp dụng biện pháp kỹ thuật ngăn chặn việc thao túng cấu trúc CSDL).
* **Hiện thực hóa Bài toán Security-as-Code (SaC):**
  - Phân tích AST bắt lệnh định nghĩa dữ liệu DDL chứa biến người dùng không qua Whitelist:
```yaml
# Chốt chặn SaC ngăn chặn DDL SQL Injection
- id: php.lang.security.injection.tainted-sql-string.tainted-sql-string
  languages: [php]
  severity: ERROR
  pattern: exec_write("CREATE TABLE ... $NAME ...", ...)
```

---

## PHẦN B: KIỂM ĐỊNH CHẤT LƯỢNG MÃ NGUỒN (SONARQUBE CODE QUALITY)

Trong mô hình DevSecOps hiện đại, bên cạnh các lỗ hổng an ninh mạng (Security Gate), dự án triển khai quy chuẩn kiểm soát kép **Dual-Gate (Security Gate + Quality Gate)**. Công cụ **SonarQube Scanner** được kích hoạt tại Stage 2 để kiểm soát độ tin cậy vận hành (Reliability) và an toàn thực thi mã nguồn. Bất kỳ lỗi thuộc nhóm **Bugs** ảnh hưởng đến sự ổn định của hệ thống đều sẽ khiến **SonarQube Quality Gate** bị đánh rớt (**FAILED**) và kích hoạt cơ chế Break-the-Build.

### 1. Tổng quan Lỗi Chất lượng Mã nguồn Phụ trách

| Tiêu chí Thẩm định | Nội dung Chi tiết từ SonarQube Scanner |
| :--- | :--- |
| **Tên vấn đề Code Quality** | **Use 'include_once' Instead of 'include' (Reliability & Execution Safety Bug)** |
| **Mã quy tắc vi phạm (Rule Key)** | [`php:S2003`](https://rules.sonarsource.com/php/RSPEC-2003) |
| **Phân loại vấn đề (Issue Type)** | 🐞 **BUG** (Lỗi khiếm khuyết độ tin cậy & an toàn thực thi mã nguồn) |
| **Mức độ nghiêm trọng (Severity)**| 🟡 **MINOR** |
| **Tệp tin & Vị trí vi phạm** | [InlaneWeb/web/src/pages/guide.php:56](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/pages/guide.php#L56) |
| **Phạm vi tiêu chuẩn áp dụng** | **SonarQube Reliability Rules** & **PHP Architecture Best Practices** |
| **Trạng thái Quality Gate** | ❌ **FAILED** (Vi phạm điều kiện tiên quyết: `0 New Bugs on New Code`) |

### 2. Bằng chứng Mã nguồn Vi phạm (Non-compliant Code)
Tại trang Cẩm nang Hàng hải (`InlaneWeb/web/src/pages/guide.php`), tệp tài liệu được nạp động bằng lệnh `include` thay vì chỉ thị bảo vệ `include_once`:

```php
// Dòng 53-57 (InlaneWeb/web/src/pages/guide.php) - MÃ NGUỒN VI PHẠM
try {
    if (@file_exists($target_file) || str_contains($doc, '..') || str_starts_with($doc, 'php://') || str_starts_with($doc, 'data://')) {
        // Nạp và hiển thị nội dung tệp
        include $target_file;
    }
```

### 3. Cơ chế Phân tích của SonarQube PHP Analyzer
* **Động cơ phân tích cú pháp AST:** Bộ phân tích `sonar-php-plugin` nhận diện các cấu trúc lệnh nạp tệp trong PHP (`include`, `require`, `include_once`, `require_once`).
* **Nguyên nhân phát hiện vi phạm:** Quy tắc `php:S2003` ("The 'include_once' or 'require_once' statement should be used instead of 'include' or 'require'") khuyến cáo và bắt buộc chuyển đổi sang `include_once` khi nạp các tệp chứa định nghĩa hàm, lớp hoặc cấu hình.
* **Hậu quả kỹ thuật:**
  - Nếu tệp đích chứa khai báo lớp hoặc hàm, việc gọi `include` nhiều lần trong cùng một chu kỳ Request sẽ gây ra lỗi nghiêm trọng không thể phục hồi: `Fatal error: Cannot redeclare function/class ...`.
  - Tiêu tốn bộ nhớ vô ích (Memory Leak) do việc nạp và biên dịch lại cùng một tệp mã nguồn nhiều lần trong Runtime.

### 4. Tác động tới Quality Gate trong Quy trình CI/CD
* **Chính sách Quality Gate (`ci/sonarqube-quality-gate.json`):**
  - Số lượng Lỗi mới (New Bugs): Yêu cầu `= 0`.
  - Mức độ tin cậy mã nguồn (Reliability Rating): Bắt buộc đạt `A`.
* **Kịch bản gãy vỡ (Break-the-Build):** Vì `php:S2003` được phân loại là **BUG**, sự xuất hiện của nó trên New Code làm chỉ số New Bugs tăng lên, kích hoạt điều kiện Fail Quality Gate. Pipeline tự động phong tỏa tiến trình Deploy.

### 5. Phương án Khắc phục Chuẩn hóa (Clean Code Refactoring)
Thay thế lệnh `include` bằng `include_once`, kết hợp với biến đường dẫn đã được kiểm tra tính hợp lệ trong danh sách trắng (Whitelist):

```php
// Dòng 53-57 (InlaneWeb/web/src/pages/guide.php) - MÃ NGUỒN ĐÃ KHẮC PHỤC
try {
    if (@file_exists($target_file) && in_array(basename($target_file), $allowed_guides, true)) {
        // Nạp tệp an toàn đúng 1 lần duy nhất trong chu kỳ thực thi
        include_once $target_file;
    }
```

### 6. Kết quả Thẩm định Sau Khắc phục (Quality Gate Passed)

| Chỉ số Chất lượng (Metrics) | Trước khi Sửa (Dirty State) | Sau khi Sửa (Clean Code State) | Trạng thái Thẩm định |
| :--- | :---: | :---: | :---: |
| **New Bugs** | `1` (Minor) | `0` | ✅ Đạt chuẩn (Thỏa mãn = 0) |
| **Reliability Rating** | `B` | `A` | ✅ Đạt chuẩn Tuyệt đối |
| **SonarQube Quality Gate** | ❌ **FAILED** | 🟢 **PASSED** | ✅ Cho phép Merge Pull Request |

---

## BÀI TOÁN SECURITY-AS-CODE (SaC) TRONG QUY TRÌNH DEVSECOPS

Với vai trò Kỹ sư QA / DevSecOps, Đào Xuân Mạnh thiết lập chốt chặn **SonarQube Quality Gate** và tiêu chuẩn an toàn tự động:
* **Mã hóa ngưỡng chất lượng (Quality Gate as Code):** Cấu hình tệp `ci/sonarqube-quality-gate.json` định nghĩa điều kiện chặn: 0 New Blocker Issues, 0 New Critical Issues, Security Rating A.
* **Cơ chế chốt chặn tự động (Automated Gatekeeper):** Khi mã nguồn vi phạm các quy tắc LFI (`php:S2083`), Stream Wrapper (`php:S2003`), hoặc DDL SQLi, SonarQube Scanner và Semgrep sẽ lập tức kích hoạt trạng thái FAILED trên GitHub Actions Status Check, từ chối cho phép hợp nhất vào nhánh `dev` hoặc `main`.
