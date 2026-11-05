# BÁO CÁO PHÂN TÍCH LỖ HỔNG AN TOÀN BẢO MẬT
**Thành viên thực hiện:** Nguyễn Phương Mai  
**Vai trò trong dự án:** Kỹ sư Quản trị Rủi ro & An ninh Dữ liệu (Security Governance & Privacy Specialist)  
**Phạm vi phụ trách:** Hệ thống Bình luận Tương tác Đối tác, Phân hệ Quản trị Admin & Tuân thủ Bảo vệ Dữ liệu  
**Đề tài:** Hệ thống DevSecOps CI/CD kiểm định an ninh tự động cho InlaneWeb Logistics Portal  

---

## PHẦN A: TỔNG HỢP DANH MỤC 4 LỖ HỔNG AN TOÀN BẢO MẬT (SAST - SEMGREP / OWASP / CWE)

| STT | Tên Lỗ hổng | Phân loại | Mã CWE | Tệp tin & Vị trí vi phạm | Mức độ cảnh báo | Động cơ phát hiện |
| :---: | :--- | :---: | :---: | :--- | :---: | :---: |
| 1 | **INSERT Statement SQL Injection** | Code | CWE-89 | `InlaneWeb/web/src/pages/comment_add.php:19` | 🔴 High / ERROR | Semgrep Taint Engine |
| 2 | **DELETE Statement SQL Injection** | Code | CWE-89 | `InlaneWeb/web/src/pages/comment_delete.php:18` | 🔴 High / ERROR | Semgrep Taint Engine |
| 3 | **Reflected Cross-Site Scripting (Link Injection)** | Code | CWE-79 | `InlaneWeb/web/src/pages/comment_add.php:29` | 🔴 High / ERROR | Semgrep (`echoed-request`) |
| 4 | **Admin Console Multi-Statement (Stacked) SQLi** | Code / Vận hành | CWE-89 | `InlaneWeb/web/src/pages/admin_console.php:33` | 🔴 High / ERROR | Semgrep Taint Engine |

---

## CHI TIẾT TỪNG LỖ HỔNG BẢO MẬT

### 1. INSERT Statement SQL Injection tại Module Thêm Bình luận Vận đơn
* **Vị trí vi phạm:** [InlaneWeb/web/src/pages/comment_add.php:19](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/pages/comment_add.php#L19)
* **Phân loại lỗi:** Mã nguồn (Application Code) | **Pha DevSecOps:** Pha Test / SAST (Stage 2)
* **Mã định danh điểm yếu:** **CWE-89: SQL Injection** | **OWASP Top 10:2021:** A03:2021 — Injection
* **Quy tắc phát hiện:** Semgrep Rule `php.lang.security.injection.tainted-sql-string.tainted-sql-string`

#### a. Bằng chứng mã nguồn vi phạm (Vulnerable Code):
```php
$shipment_id = intval($_GET['shipment_id'] ?? 0);
$content     = $_POST['content'] ?? '';

// Sink: Nối thẳng chuỗi $content từ người dùng vào mệnh đề VALUES(...)
$sql = "INSERT INTO comments (shipment_id, user_id, content) VALUES "
     . "($shipment_id, " . intval($u['id']) . ", '$content')";

render_header('Thêm bình luận');
echo '<div class="card"><h1>Thêm bình luận</h1>';
echo '<div class="query-box">' . htmlspecialchars($sql) . '</div>';

if (exec_write($sql)) {
    flash('Đã thêm bình luận.', 'success');
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
      - pattern: exec_write("INSERT INTO ... VALUES (..., '$CONTENT')", ...)
```

* **Cơ chế phân tích luồng ô nhiễm (Taint / AST Analysis):**
  - **Tệp tin & hàm xử lý:** Tự động phát hiện trong Stage 2 và trích xuất qua script [`ci/semgrep_report.py`](file:///d:/PTIT-DevOps-SonarQube/ci/semgrep_report.py) bằng hàm `extract_source_and_sink(path_str, line_no)`.
  - **🟡 SOURCE (Nguồn dữ liệu người dùng nhập / Khai báo cấu hình):**
```php
// Dòng 15-16 (InlaneWeb/web/src/pages/comment_add.php):
$shipment_id = intval($_GET['shipment_id'] ?? 0);
$content     = $_POST['content'] ?? '';
```
  - **🔴 SINK (Điểm kích hoạt / Thực thi câu lệnh nguy hiểm):**
```php
// Dòng 19-20, 26 (InlaneWeb/web/src/pages/comment_add.php):
$sql = "INSERT INTO comments (shipment_id, user_id, content) VALUES "
     . "($shipment_id, " . intval($u['id']) . ", '$content')";
if (exec_write($sql)) {
```

#### c. Kịch bản khai thác thực tế (PoC):
Kẻ tấn công đóng sớm mệnh đề `VALUES` để chèn thêm các hàm truy vấn con (Subquery) hoặc hàm kích hoạt lỗi để trích xuất dữ liệu nhạy cảm:
```http
POST /shipments/1/comments
Content-Type: application/x-www-form-urlencoded

content=test', '2026-10-29');-- -
```
Hoặc trích xuất mật khẩu của tài khoản `admin` qua hàm trích xuất XPath Error:
```http
content=test' || (SELECT extractvalue(1, concat(0x7e, (SELECT password FROM users WHERE username='admin')))) || '
```
* **Hậu quả:** Dữ liệu mật khẩu của quản trị viên bị lộ lọt trực tiếp thông qua thông báo lỗi hoặc được lưu trữ trái phép vào cơ sở dữ liệu.

#### d. Cách thức xử lý & Khắc phục (Remediation):
Sử dụng **Prepared Statements tham số hóa**:
```php
$stmt = db()->prepare("INSERT INTO comments (shipment_id, user_id, content) VALUES (?, ?, ?)");
$uid = intval($u['id']);
$stmt->bind_param("iis", $shipment_id, $uid, $content);
$stmt->execute();
```

#### e. Đánh giá Vi phạm Chính sách & Bài toán Security-as-Code (SaC):
* **Pha trong quy trình DevSecOps:** **Pha Test / SAST Gate (Stage 2 trong CI/CD Pipeline)**
  - *Đánh giá rủi ro:* Lỗi nằm tại tính năng thêm bình luận đơn hàng. Việc nối chuỗi cho phép kẻ tấn công đóng sớm mệnh đề VALUES để chèn thêm các truy vấn phụ trích xuất mật khẩu quản trị viên.
* **Căn cứ vi phạm chính sách pháp lý:**
  - **Nghị định 13/2023/NĐ-CP:** Điều 9 Khoản 2 & Điều 13 (Vi phạm quy định bảo vệ an toàn thông tin cá nhân, tạo điều kiện cho kẻ tấn công trích xuất dữ liệu xác thực).
  - **GDPR (Châu Âu):** Article 32 — Security of Processing (Không áp dụng các biện pháp kỹ thuật phù hợp nhằm bảo đảm tính bảo mật của quá trình xử lý dữ liệu).
* **Hiện thực hóa Bài toán Security-as-Code (SaC):**
  - Taint Analysis bắt câu lệnh INSERT chứa nội dung bình luận thô từ người dùng:
```yaml
# Chốt chặn SaC phát hiện INSERT SQL Injection
- id: php.lang.security.injection.tainted-sql-string.tainted-sql-string
  languages: [php]
  severity: ERROR
  pattern: exec_write("INSERT INTO ... VALUES (..., '$CONTENT')", ...)
```

---

### 2. DELETE Statement SQL Injection tại Module Xóa Bình luận
* **Vị trí vi phạm:** [InlaneWeb/web/src/pages/comment_delete.php:18](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/pages/comment_delete.php#L18)
* **Phân loại lỗi:** Mã nguồn (Application Code) | **Pha DevSecOps:** Pha Test / SAST (Stage 2)
* **Mã định danh điểm yếu:** **CWE-89: SQL Injection** | **OWASP Top 10:2021:** A03:2021 — Injection
* **Quy tắc phát hiện:** Semgrep Rule `php.lang.security.injection.tainted-sql-string.tainted-sql-string`

#### a. Bằng chứng mã nguồn vi phạm (Vulnerable Code):
```php
$comment_id = $_GET['comment_id'] ?? '';

// Sink: Nối thẳng chuỗi comment_id vào mệnh đề WHERE trong câu lệnh DELETE
$sql = "DELETE FROM comments WHERE id = $comment_id";

render_header('Xoá bình luận');
echo '<div class="card"><h1>Xoá bình luận</h1>';
echo '<div class="query-box">' . htmlspecialchars($sql) . '</div>';

if (exec_write($sql)) {
    $affected = mysqli_affected_rows(db());
    flash('Đã xoá. Số bản ghi bị xoá: <strong>' . $affected . '</strong>.', 'success');
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
      - pattern: exec_write("DELETE FROM ... WHERE id = $ID", ...)
```

* **Cơ chế phân tích luồng ô nhiễm (Taint / AST Analysis):**
  - **Tệp tin & hàm xử lý:** Tự động phát hiện trong Stage 2 và trích xuất qua script [`ci/semgrep_report.py`](file:///d:/PTIT-DevOps-SonarQube/ci/semgrep_report.py) bằng hàm `extract_source_and_sink(path_str, line_no)`.
  - **🟡 SOURCE (Nguồn dữ liệu người dùng nhập / Khai báo cấu hình):**
```php
// Dòng 15 (InlaneWeb/web/src/pages/comment_delete.php):
$comment_id = $_GET['comment_id'] ?? '';
```
  - **🔴 SINK (Điểm kích hoạt / Thực thi câu lệnh nguy hiểm):**
```php
// Dòng 18, 24 (InlaneWeb/web/src/pages/comment_delete.php):
$sql = "DELETE FROM comments WHERE id = $comment_id";
if (exec_write($sql)) {
```

#### c. Kịch bản khai thác thực tế (PoC):
Kẻ tấn công gửi yêu cầu xóa với biểu thức logic luôn đúng:
```http
GET /comments/1 OR 1=1/delete
```
* **Hậu quả:** Câu lệnh biến thành `DELETE FROM comments WHERE id = 1 OR 1=1`, dẫn tới **xóa sạch toàn bộ dữ liệu bình luận** của toàn bộ khách hàng và đối tác trong hệ thống logistics. Kẻ tấn công phá hủy hoàn toàn tính toàn vẹn và tính khả dụng của dữ liệu.

#### d. Cách thức xử lý & Khắc phục (Remediation):
Kiểm tra và ép kiểu số nguyên chặt chẽ, kết hợp Prepared Statements và kiểm tra quyền sở hữu (Authorization Check):
```php
$comment_id = filter_input(INPUT_GET, 'comment_id', FILTER_VALIDATE_INT);
if ($comment_id === false || $comment_id === null) {
    flash('Mã bình luận không hợp lệ.', 'danger');
    header('Location: /account');
    exit;
}

// Bắt buộc Prepared Statements và chỉ cho phép người dùng xóa bình luận của chính mình
$stmt = db()->prepare("DELETE FROM comments WHERE id = ? AND (user_id = ? OR ? = 'admin')");
$uid = intval($u['id']);
$role = $u['role'];
$stmt->bind_param("iis", $comment_id, $uid, $role);
$stmt->execute();
```

#### e. Đánh giá Vi phạm Chính sách & Bài toán Security-as-Code (SaC):
* **Pha trong quy trình DevSecOps:** **Pha Test / SAST Gate (Stage 2 trong CI/CD Pipeline)**
  - *Đánh giá rủi ro:* Lỗi nằm tại chức năng xóa bình luận. Tham số `$comment_id` không được kiểm tra cho phép kẻ tấn công truyền biểu thức logic `1 OR 1=1` để xóa sạch toàn bộ dữ liệu bình luận trong hệ thống.
* **Căn cứ vi phạm chính sách pháp lý:**
  - **Nghị định 13/2023/NĐ-CP:** Điều 9 Khoản 1 & Khoản 2 (Vi phạm quy định về bảo vệ tính toàn vẹn của dữ liệu cá nhân, để xảy ra tình trạng mất mát, phá hủy dữ liệu của chủ thể dữ liệu).
  - **GDPR (Châu Âu):** Article 5(1)(f) — Integrity and Confidentiality (Không áp dụng các biện pháp kỹ thuật cần thiết để ngăn chặn hành vi xóa dữ liệu trái phép hoặc phá hoại cơ sở dữ liệu).
* **Hiện thực hóa Bài toán Security-as-Code (SaC):**
  - Phân tích AST bắt buộc câu lệnh DELETE phải sử dụng Prepared Statement và kiểm tra phân quyền:
```yaml
# Chốt chặn SaC ngăn chặn DELETE SQL Injection
- id: php.lang.security.injection.tainted-sql-string.tainted-sql-string
  languages: [php]
  severity: ERROR
  pattern: exec_write("DELETE FROM ... WHERE id = $ID", ...)
```

---

### 3. Reflected Cross-Site Scripting (Link Injection / Echoed Request)
* **Vị trí vi phạm:** [InlaneWeb/web/src/pages/comment_add.php:29](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/pages/comment_add.php#L29)
* **Phân loại lỗi:** Mã nguồn (Application Code) | **Pha DevSecOps:** Pha Test / SAST (Stage 2)
* **Mã định danh điểm yếu:** **CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')**
* **Quy tắc phát hiện:** Semgrep Rule `php.lang.security.injection.echoed-request.echoed-request`

#### a. Bằng chứng mã nguồn vi phạm (Vulnerable Code):
```php
// Nối biến bắt nguồn từ URL request vào thuộc tính href của thẻ liên kết HTML
echo '<p class="muted"><a href="/shipments/' . $shipment_id . '">← Về đơn hàng</a></p></div>';
```

#### b. Cơ chế phát hiện & Trích xuất mã nguồn (Detection Mechanism):
* **Quy tắc Semgrep quét phát hiện (Rule Definition Code):**
```yaml
rules:
  - id: php.lang.security.injection.echoed-request.echoed-request
    languages: [php]
    severity: ERROR
    patterns:
      - pattern: echo ... $_GET[...] ...;
      - pattern-not: htmlspecialchars(...)
```

* **Cơ chế phân tích luồng ô nhiễm (Taint / AST Analysis):**
  - **Tệp tin & hàm xử lý:** Tự động phát hiện trong Stage 2 và trích xuất qua script [`ci/semgrep_report.py`](file:///d:/PTIT-DevOps-SonarQube/ci/semgrep_report.py) bằng hàm `extract_source_and_sink(path_str, line_no)`.
  - **🟡 SOURCE (Nguồn dữ liệu người dùng nhập / Khai báo cấu hình):**
```php
// Dòng 15 (InlaneWeb/web/src/pages/comment_add.php):
$shipment_id = intval($_GET['shipment_id'] ?? 0);
```
  - **🔴 SINK (Điểm kích hoạt / Thực thi câu lệnh nguy hiểm):**
```php
// Dòng 29 (InlaneWeb/web/src/pages/comment_add.php):
echo '<p class="muted"><a href="/shipments/' . $shipment_id . '">← Về đơn hàng</a></p></div>';
```

#### c. Kịch bản khai thác thực tế (PoC):
Nếu tham số `shipment_id` nhận giá trị từ chuỗi truy vấn URL chứa ký tự đóng nháy kép và mã JavaScript:
```http
POST /shipments/1"><script>alert(document.cookie)</script>/comments
```
* **Hậu quả:** Trình duyệt nạn nhân tự động thực thi script độc hại khi click vào nút quay lại đơn hàng, dẫn tới nguy cơ đánh cắp phiên làm việc và mã độc phía máy khách.

#### d. Cách thức xử lý & Khắc phục (Remediation):
Áp dụng hàm mã hóa thực thể an toàn với cờ `ENT_QUOTES`:
```php
$safe_shipment_id = htmlspecialchars((string)$shipment_id, ENT_QUOTES, 'UTF-8');
echo '<p class="muted"><a href="/shipments/' . $safe_shipment_id . '">← Về đơn hàng</a></p></div>';
```

#### e. Đánh giá Vi phạm Chính sách & Bài toán Security-as-Code (SaC):
* **Pha trong quy trình DevSecOps:** **Pha Test / SAST Gate (Stage 2 trong CI/CD Pipeline)**
  - *Đánh giá rủi ro:* Lỗi xảy ra khi hiển thị liên kết quay lại đơn hàng. Biến `$shipment_id` được đưa trực tiếp vào thuộc tính `href` tạo nguy cơ chèn mã độc JavaScript thực thi phía client.
* **Căn cứ vi phạm chính sách pháp lý:**
  - **Nghị định 13/2023/NĐ-CP:** Điều 13 Khoản 2 (Vi phạm bảo vệ an toàn thông tin tài khoản và phiên đăng nhập của người dùng).
  - **GDPR (Châu Âu):** Article 5(1)(f) (Xử lý dữ liệu không đảm bảo tính bảo mật thích hợp trước các cuộc tấn công khai thác phía client).
* **Hiện thực hóa Bài toán Security-as-Code (SaC):**
  - Kiểm tra liên kết HTML động bắt buộc phải bọc hàm mã hóa thực thể an toàn:
```yaml
# Bắt buộc mã hóa thực thể HTML cho thuộc tính liên kết
- id: php.lang.security.injection.echoed-request.echoed-request
  languages: [php]
  severity: ERROR
  patterns:
    - pattern: echo ... '<a href="/shipments/' . $ID . '"...'
    - pattern-not: htmlspecialchars(...)
```

---

### 4. Admin Console Multi-Statement (Stacked Queries) SQL Injection
* **Vị trí vi phạm:** [InlaneWeb/web/src/pages/admin_console.php:33](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/pages/admin_console.php#L33)
* **Phân loại lỗi:** Mã nguồn & Vận hành Quản trị (Application Code & Administrative Operations) | **Pha DevSecOps:** Pha Test / SAST & Operations (Stage 2 & Stage 4)
* **Mã định danh điểm yếu:** **CWE-89: SQL Injection (Stacked Queries Context)** | **OWASP Top 10:2021:** A03:2021 — Injection
* **Quy tắc phát hiện:** Semgrep Rule `php.lang.security.injection.tainted-sql-string.tainted-sql-string`

#### a. Bằng chứng mã nguồn vi phạm (Vulnerable Code):
```php
$filter = $_GET['filter'] ?? 'status';

// Nối trực tiếp biến $filter vào tên cột truy vấn
$sql = "SELECT tracking_no, $filter FROM shipments";
echo '<div class="query-box">' . htmlspecialchars($sql) . '</div>';

// Hàm exec_multi sử dụng API nguy hiểm mysqli_multi_query!
$rows = exec_multi($sql);
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
      - pattern: exec_multi("SELECT ... $FILTER FROM ...", ...)
```

* **Cơ chế phân tích luồng ô nhiễm (Taint / AST Analysis):**
  - **Tệp tin & hàm xử lý:** Tự động phát hiện trong Stage 2 và trích xuất qua script [`ci/semgrep_report.py`](file:///d:/PTIT-DevOps-SonarQube/ci/semgrep_report.py) bằng hàm `extract_source_and_sink(path_str, line_no)`.
  - **🟡 SOURCE (Nguồn dữ liệu người dùng nhập / Khai báo cấu hình):**
```php
// Dòng 24 (InlaneWeb/web/src/pages/admin_console.php):
$filter = $_GET['filter'] ?? 'status';
```
  - **🔴 SINK (Điểm kích hoạt / Thực thi câu lệnh nguy hiểm):**
```php
// Dòng 33, 36 (InlaneWeb/web/src/pages/admin_console.php):
$sql = "SELECT tracking_no, $filter FROM shipments";
$rows = exec_multi($sql);
```

#### c. Kịch bản khai thác thực tế (PoC):
Kẻ tấn công chèn thêm một tài khoản quản trị viên mới vào hệ thống:
```http
GET /admin/console?filter=status;+INSERT+INTO+users(username,password,role)+VALUES('backdoor_admin','Admin@123','admin');-- -
```
Hoặc xóa vĩnh viễn bảng dữ liệu vận chuyển hàng hải:
```http
GET /admin/console?filter=status;+DROP+TABLE+shipments;-- -
```
* **Hậu quả:** Chiếm quyền kiểm soát máy chủ CSDL ở cấp độ cao nhất, tạo cửa sau (backdoor) hoặc phá hoại hoàn toàn dữ liệu nghiệp vụ của công ty logistics.

#### d. Cách thức xử lý & Khắc phục (Remediation):
1. **Loại bỏ hoàn toàn API `mysqli_multi_query`** trong các nghiệp vụ có nhận input từ người dùng.
2. Áp dụng **Whitelist nghiêm ngặt** cho tên cột cần lọc:
```php
$allowed_filters = [
    'status'      => 'status',
    'port_code'   => 'port_code',
    'created_at'  => 'created_at',
    'customer_id' => 'customer_id'
];

$filter_param = $_GET['filter'] ?? 'status';
$safe_column = $allowed_filters[$filter_param] ?? 'status';

$stmt = db()->prepare("SELECT tracking_no, `" . $safe_column . "` FROM shipments");
$stmt->execute();
$rows = $stmt->get_result()->fetch_all(MYSQLI_ASSOC);
```

#### e. Đánh giá Vi phạm Chính sách & Bài toán Observability-as-Code (SaC):
* **Pha trong quy trình DevSecOps:** **Pha Test & Monitor / Observability (Stage 2 & Stage 4)**
  - *Đánh giá rủi ro:* Lỗi xảy ra tại giao diện quản trị viên khi sử dụng hàm `mysqli_multi_query`. Kẻ tấn công có thể chèn dấu chấm phẩy `;` để thực thi nhiều câu lệnh độc hại liên tiếp (tạo backdoor admin, drop table).
* **Căn cứ vi phạm chính sách pháp lý:**
  - **Nghị định 13/2023/NĐ-CP:** Điều 9, 13, 17, 26 (Vi phạm bảo vệ an toàn CSDL cốt lõi và nghĩa vụ phát hiện, báo cáo sự cố an ninh mạng trong vòng 72 giờ).
  - **GDPR (Châu Âu):** Article 32 & 33 (Vi phạm nghĩa vụ bảo đảm an ninh kỹ thuật và chế tài thông báo vi phạm dữ liệu trong 72 giờ).
* **Hiện thực hóa Bài toán Observability-as-Code (SaC):**
  - Giám sát và cảnh báo thời gian thực các cuộc tấn công Stacked SQLi thông qua bộ lọc LogQL trên cụm Loki + Grafana:
```logql
# InlaneWeb/monitoring/loki/rules/fake/alert-rules.yml (Observability-as-Code)
{job="apache_json"} | json | uri =~ "(/admin/console|/comments)" and query =~ "(?i)(;|union|insert|drop|extractvalue)"
```

---

## PHẦN B: KIỂM ĐỊNH CHẤT LƯỢNG MÃ NGUỒN (SONARQUBE CODE QUALITY)

Trong mô hình DevSecOps hiện đại, bên cạnh các lỗ hổng an ninh mạng (Security Gate), dự án triển khai quy chuẩn kiểm soát kép **Dual-Gate (Security Gate + Quality Gate)**. Công cụ **SonarQube Scanner** được kích hoạt tại Stage 2 để kiểm tra tiêu chuẩn trợ năng giao diện Admin, chuẩn Clean Code PSR-1 và quy cách định dạng tệp PSR-12.

Bất kỳ lỗi thuộc nhóm **New Bugs** hoặc vi phạm chuẩn mã nguồn nào xuất hiện trên nhánh tính năng (`feature/*`) đều sẽ trực tiếp đánh rớt Quality Gate (**FAILED**) và kích hoạt cơ chế ngắt tiến trình (Break-the-Build).

Phân hệ phụ trách của Nguyễn Phương Mai gồm **03 lỗi chất lượng mã nguồn thực tế** được SonarQube ghi nhận trong `reports/sonarqube_ci/issues.json`:

### 1. Bảng Tổng hợp 03 Lỗi Code Quality Phụ trách

| Mã | Tên Vấn đề Code Quality | Tệp & Vị trí Vi phạm | Quy tắc SonarQube | Phân loại | Mức độ | Tiêu chuẩn Vi phạm |
| :---: | :--- | :--- | :--- | :---: | :---: | :--- |
| **CQ-01** | Admin Filter Input Without Associated Label | [admin_dashboard.php:26](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/pages/admin_dashboard.php#L26) | `Web:InputWithoutLabelCheck` | 🐞 BUG | 🟠 MAJOR | WCAG 2.1 Level A (Criteria 1.3.1, 4.1.2) |
| **CQ-02** | Missing Trailing Newline at End of File | [admin_console.php:55](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/pages/admin_console.php#L55) | `php:S113` | 🧹 CODE_SMELL | 🟡 MINOR | PSR-12 File Formatting Standard |
| **CQ-03** | Template Helper Function Naming Violates camelCase | [layout.php:13](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/lib/layout.php#L13) | `php:S100` | 🧹 CODE_SMELL | 🟡 MINOR | PSR-1 Basic Coding Standard |

---

### 2. Chi tiết Từng Lỗi Chất lượng Mã nguồn & Kịch bản Khắc phục

#### CQ-01: Admin Log Filter Input Without Associated Label (Accessibility Bug)
* **Vị trí vi phạm:** [InlaneWeb/web/src/pages/admin_dashboard.php:26](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/pages/admin_dashboard.php#L26)
* **Quy tắc SonarQube:** [`Web:InputWithoutLabelCheck`](https://rules.sonarsource.com/html/RSPEC-InputWithoutLabelCheck) (Major Bug)
* **Bằng chứng mã nguồn vi phạm (Non-compliant Code):**
```html
<!-- Dòng 25-27 (InlaneWeb/web/src/pages/admin_dashboard.php) - MÃ NGUỒN VI PHẠM -->
<form method="get" action="/admin">
    <input type="text" name="filter" value="<?= htmlspecialchars($filter) ?>" placeholder="Lọc theo hành động hoặc username...">
    <button class="btn" type="submit">Lọc nhật ký</button>
```
* **Cơ chế phân tích của SonarQube:** Ô nhập liệu lọc dữ liệu quản trị thiếu hoàn toàn thuộc tính `id` và nhãn `<label>` trợ năng, vi phạm nguyên tắc trợ năng WCAG 2.1.
* **Phương án khắc phục chuẩn hóa (Clean Code Refactoring):**
```html
<!-- Dòng 25-28 (InlaneWeb/web/src/pages/admin_dashboard.php) - MÃ NGUỒN ĐÃ KHẮC PHỤC -->
<form method="get" action="/admin">
    <label for="admin-filter-log" class="form-label sr-only">Lọc nhật ký quản trị:</label>
    <input id="admin-filter-log" type="text" name="filter" value="<?= htmlspecialchars($filter) ?>" placeholder="Lọc theo hành động hoặc username...">
    <button class="btn" type="submit">Lọc nhật ký</button>
```

---

#### CQ-02: Missing Trailing Newline at End of Admin Console File (PSR-12 Code Smell)
* **Vị trí vi phạm:** [InlaneWeb/web/src/pages/admin_console.php:55](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/pages/admin_console.php#L55)
* **Quy tắc SonarQube:** [`php:S113`](https://rules.sonarsource.com/php/RSPEC-113) (Minor Code Smell)
* **Bằng chứng mã nguồn vi phạm (Non-compliant Code):**
```php
// Dòng 54-55 (InlaneWeb/web/src/pages/admin_console.php) - MÃ NGUỒN VI PHẠM
echo '<p class="muted"><a href="/admin">← Về dashboard</a></p></div>';
render_footer(); // <--- Tệp kết thúc ngay tại đây, thiếu ký tự xuống dòng EOF
```
* **Cơ chế phân tích của SonarQube:** Bộ phân tích cú pháp phát hiện tệp mã nguồn không kết thúc bằng một dòng trống mới (`
`). Tiêu chuẩn PSR-12 Mục 2.2 và quy chuẩn POSIX bắt buộc tất cả tệp mã nguồn phải kết thúc bằng ký tự newline, tránh cảnh báo `\ No newline at end of file` trên Git diff.
* **Phương án khắc phục chuẩn hóa (Clean Code Refactoring):**
```php
// Dòng 54-56 (InlaneWeb/web/src/pages/admin_console.php) - MÃ NGUỒN ĐÃ KHẮC PHỤC
echo '<p class="muted"><a href="/admin">← Về dashboard</a></p></div>';
render_footer();

```

---

#### CQ-03: Template Helper Function Naming Violates PSR-1 camelCase (Clean Code Smell)
* **Vị trí vi phạm:** [InlaneWeb/web/src/lib/layout.php:13](file:///d:/PTIT-DevOps-SonarQube/InlaneWeb/web/src/lib/layout.php#L13)
* **Quy tắc SonarQube:** [`php:S100`](https://rules.sonarsource.com/php/RSPEC-100) (Minor Code Smell)
* **Bằng chứng mã nguồn vi phạm (Non-compliant Code):**
```php
// Dòng 12-14 (InlaneWeb/web/src/lib/layout.php) - MÃ NGUỒN VI PHẠM
function render_header(string $title = 'IlFreight Logistics'): void
{
    $u = current_user();
```
* **Cơ chế phân tích của SonarQube:** Hàm `render_header` sử dụng quy ước snake_case vi phạm biểu thức chính quy ^[a-z][a-zA-Z0-9]*$. Tiêu chuẩn Clean Code PSR-1 khuyến nghị mọi hàm tiện ích kết xuất giao diện phải được đặt tên theo quy ước camelCase (`renderHeader`).
* **Phương án khắc phục chuẩn hóa (Clean Code Refactoring):**
```php
// Dòng 12-14 (InlaneWeb/web/src/lib/layout.php) - MÃ NGUỒN ĐÃ KHẮC PHỤC
function renderHeader(string $title = 'IlFreight Logistics'): void
{
    $u = current_user();
```

---

### 3. Kết quả Thẩm định Chất lượng SonarQube Trước & Sau Khắc phục

| Chỉ số Chất lượng (Metrics) | Trước khi Sửa (Dirty State) | Sau khi Sửa (Clean Code State) | Trạng thái Thẩm định |
| :--- | :---: | :---: | :---: |
| **New Bugs** | `1` (Major) | `0` | ✅ Đạt chuẩn (Thỏa mãn = 0) |
| **Code Smells** | `2` (Minor PSR) | `0` | ✅ Đạt chuẩn Tuyệt đối |
| **Reliability Rating** | `C` | `A` | ✅ Đạt chuẩn Tuyệt đối |
| **SonarQube Quality Gate** | ❌ **FAILED** | 🟢 **PASSED** | ✅ Cho phép Merge Pull Request |

---
## BÀI TOÁN OBSERVABILITY-AS-CODE (SaC) & GIÁM SÁT SỰ CỐ AN NINH (DEVSECOPS)

Để đáp ứng quy định khắt khe của **Nghị định 13/2023/NĐ-CP (Điều 13 Khoản 3 & Điều 17)** và **GDPR (Article 33)** về nghĩa vụ phát hiện và **báo cáo sự cố rò rỉ dữ liệu trong vòng 72 giờ**, nhóm đã xây dựng hệ thống **Observability-as-Code** tại **Stage 4 (Monitor & Audit)**:

### 1. Chuẩn hóa Audit Log có cấu trúc (JSON Format)
Toàn bộ log truy cập web server Apache được định dạng JSON chuẩn trong `000-default.conf`:
```apache
LogFormat "{\"time\":\"%{%Y-%m-%dT%H:%M:%S%z}t\",\"client_ip\":\"%a\",\"uri\":\"%U\",\"query\":\"%q\",\"status\":\"%>s\",\"user_agent\":\"%{User-Agent}i\"}" apache_json
```

### 2. Truy vấn phát hiện xâm nhập thời gian thực với LogQL (Grafana + Loki)
Các kịch bản tấn công SQL Injection và XSS được giám sát tự động 24/7 thông qua bộ lọc LogQL:
```logql
# Phát hiện truy vấn tấn công SQL Injection vào trang bình luận và bảng điều khiển:
{job="apache_json"} | json | uri =~ "(/comments|/admin/console)" and query =~ "(?i)(union|select|insert|drop|extractvalue)"
```
* **Ý nghĩa:** Khi phát hiện tần suất tấn công vượt ngưỡng cảnh báo, hệ thống lập tức bắn thông báo cảnh báo đến kênh quản trị an ninh (Telegram / Email), giúp đội ngũ SecOps kịp thời kích hoạt quy trình ứng phó sự cố (Incident Response) và đảm bảo báo cáo cơ quan thẩm quyền đúng thời hạn luật định.
