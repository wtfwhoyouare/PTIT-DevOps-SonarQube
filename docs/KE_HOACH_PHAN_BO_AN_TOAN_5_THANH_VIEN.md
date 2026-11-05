# KẾ HOẠCH PHÂN BỔ NHIỆM VỤ AN TOÀN ỨNG DỤNG CHO 5 THÀNH VIÊN NHÓM
**Đề tài:** Xây dựng đường ống DevSecOps tự động hóa kiểm định an ninh và triển khai ứng dụng InlaneWeb Logistics  
**Học viện:** Học viện Công nghệ Bưu chính Viễn thông (PTIT)

---

## 1. MỤC TIÊU VÀ YÊU CẦU CỦA GIẢNG VIÊN

Theo yêu cầu của giảng viên hướng dẫn, mỗi thành viên trong nhóm 5 người cần hoàn thành trọn vẹn một chuyên đề an ninh độc lập với các tiêu chí bắt buộc:
1. **Chỉ ra 1 vấn đề an toàn cụ thể** liên quan trực tiếp đến ứng dụng InlaneWeb hoặc hạ tầng triển khai.
2. **Cách thức phát hiện:** Nêu rõ công cụ, phương pháp (SAST, SCA, Config Validation, Taint Analysis, Log SIEM).
3. **Cách thức xử lý:** Biện pháp khắc phục kỹ thuật, code fix, cấu hình hardening.
4. **Vi phạm chính sách pháp lý:** Đối chiếu chính xác theo **Nghị định 13/2023/NĐ-CP** (Bảo vệ dữ liệu cá nhân) hoặc **GDPR** (Châu Âu).
5. **Xác định pha DevSecOps:** Phân bổ rõ ràng vấn đề rơi vào pha nào trong chu trình DevSecOps (Plan, Code, Build, Test, Release, Deploy, Operate, Monitor).
6. **Thể hiện bài toán Policy-as-Code (PaC) hoặc Security-as-Code (SaC):** Có đoạn mã quy tắc/chính sách tự động hóa minh chứng.
7. **Cân đối nhóm lỗi:** Nhóm bắt buộc có tối thiểu 2 nhóm lỗi: **Nhóm lỗi Code** và **Nhóm lỗi Triển khai / Vận hành**.

---

## 2. MA TRẬN PHÂN BỔ TỔNG THỂ 5 THÀNH VIÊN

| STT | Thành viên nhóm | Chức danh chuyên môn | Vấn đề an toàn chủ trì | Nhóm lỗi | Pha DevSecOps | Bài toán Kỹ thuật | Vi phạm Chính sách Pháp lý |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **1** | **Nguyễn Giang Nam**<br>*(Trưởng nhóm)* | Kiến trúc sư DevSecOps | **Bypass kiểm soát phân nhánh & Đưa mã nguồn chưa kiểm duyệt lên nhánh sản xuất** | **Triển khai & Vận hành** | **Pha Code / Commit**<br>*(Stage 1)* | **Policy-as-Code (PaC)**<br>*(Python Branch Harness)* | **NĐ 13/2023:** Đ.13 K.1<br>**GDPR:** Art. 25 (By Design) |
| **2** | **Nguyễn Đình Hải** | Kỹ sư An ninh Phần mềm | **Lỗ hổng SQL Injection (CWE-89) gây rò rỉ dữ liệu cá nhân và vận đơn** | **Mã nguồn (Code)** | **Pha Test / SAST**<br>*(Stage 2)* | **Security-as-Code (SaC)**<br>*(Semgrep Taint Rules & Sonar)* | **NĐ 13/2023:** Đ.9 K.2, Đ.26<br>**GDPR:** Art. 32 (Security) |
| **3** | **Đào Xuân Mạnh** | Kỹ sư Kiểm định Chất lượng | **Lỗ hổng Local File Inclusion (CWE-22) & Reflected XSS (CWE-79)** | **Mã nguồn (Code)** | **Pha Build / Gate**<br>*(Stage 2)* | **Security-as-Code (SaC)**<br>*(SonarQube Gate Rating A)* | **NĐ 13/2023:** Đ.13 K.2<br>**GDPR:** Art. 5(1)(f) (Confidentiality) |
| **4** | **Lê Đức Anh** | Kỹ sư Tự động hóa Hạ tầng | **Lộ cổng dịch vụ CSDL (3306) & Cấu hình Docker không cô lập mạng** | **Triển khai & Vận hành** | **Pha Release / Deploy**<br>*(Stage 3 & 4)* | **Policy-as-Code (PaC)**<br>*(IaC Config Validator 21/21)* | **NĐ 13/2023:** Đ.13 K.1, Đ.26<br>**GDPR:** Art. 32 (Resilience) |
| **5** | **Nguyễn Phương Mai** | Kỹ sư Giám sát & Vận hành | **Thiếu hụt hệ thống log kiểm toán & Nguy cơ vi phạm thời hạn báo cáo sự cố 72h** | **Triển khai & Vận hành** | **Pha Monitor / Audit**<br>*(Stage 4 & Ops)* | **Observability-as-Code**<br>*(Promtail, Loki & LogQL Panels)* | **NĐ 13/2023:** Đ.13 K.3, Đ.17<br>**GDPR:** Art. 33 (72h Notice) |

---

## 3. NỘI DUNG CHI TIẾT TỪNG THÀNH VIÊN

### THÀNH VIÊN 1: NGUYỄN GIANG NAM (TRƯỞNG NHÓM)
* **Vai trò:** Kiến trúc sư DevSecOps (Lead Architect)
* **Vấn đề an toàn:** **Kiểm soát phân nhánh lỏng lẻo — Nguy cơ đưa mã độc hoặc backdoor trực tiếp lên nhánh sản xuất (`main`) do bỏ qua quy trình rà soát mã (Code Review).**
* **Phân loại nhóm lỗi:** **Nhóm lỗi Triển khai & Vận hành (Deployment & Operations)**.
* **Pha trong DevSecOps:** **Pha Code / Commit (Stage 1 trong Pipeline)**.
* **Cách thức phát hiện:**
  * Sử dụng Git Hook (`commit-msg`) cục bộ trên máy trạm kết hợp công cụ kiểm soát chính sách phân nhánh tự động `ci/policy_guard.py` tại Stage 1 của GitHub Actions.
  * Phân tích đối tượng sự kiện `github.event_name` và `github.ref`. Tự động từ chối nếu có thao tác `git push` trực tiếp lên `main` hoặc `dev`, hoặc tiêu đề Pull Request sai định dạng.
* **Cách thức xử lý:**
  * Kích hoạt Branch Protection Rules trên GitHub: Khóa cứng nhánh `main`, bắt buộc 100% thay đổi phải tạo PR từ nhánh `dev`.
  * Cài đặt tự động hook máy trạm: `git config core.hooksPath .githooks` bảo đảm lập trình viên không thể bỏ qua quy chuẩn.
* **Căn cứ vi phạm chính sách pháp lý:**
  * **Nghị định 13/2023/NĐ-CP (Điều 13, Khoản 1):** Vi phạm quy định về *biện pháp quản lý và kỹ thuật bảo vệ dữ liệu cá nhân ngay từ khâu thiết kế hệ thống*.
  * **GDPR (Article 25 — Data Protection by Design and by Default):** Hệ thống thiếu cơ chế mặc định bảo vệ luồng tích hợp mã nguồn khỏi các can thiệp trái phép.
* **Bài toán Policy-as-Code (PaC):**
  * Chính sách quản lý phân nhánh được mã hóa trực tiếp thành kịch bản kiểm tra `ci/policy_guard.py` chạy tự động tại Stage 1.
```python
# Minh chứng PaC tại Stage 1 (ci/policy_guard.py):
if event_name == "push" and target_branch == "main":
    sys.exit("[POLICY ERROR] Nghiêm cấm push trực tiếp lên main! Mọi thay đổi phải qua Pull Request.")
```

---

### THÀNH VIÊN 2: NGUYỄN ĐÌNH HẢI
* **Vai trò:** Kỹ sư An ninh Phần mềm (Security Engineer)
* **Vấn đề an toàn:** **Lỗ hổng SQL Injection (CWE-89) gây rò rỉ dữ liệu cá nhân khách hàng, thông tin vận đơn và vượt qua cơ chế xác thực.**
* **Phân loại nhóm lỗi:** **Nhóm lỗi Mã nguồn (Code Vulnerability)**.
* **Pha trong DevSecOps:** **Pha Test / Static Security Testing (Stage 2 trong Pipeline)**.
* **Cách thức phát hiện:**
  * Kết hợp bộ quét mã tĩnh **SonarQube Quality Gate** (Rule `php:S2077`) và **Semgrep SAST** với tập luật tùy biến địa phương `ci/semgrep-local-rules.yml`.
  * *Cơ chế:* Ứng dụng kỹ thuật phân tích luồng dữ liệu ô nhiễm (**Taint Analysis**), theo dõi dữ liệu người dùng nhập từ nguồn (`$_GET`, `$_POST`) chảy vào điểm chìm (`mysqli_query`, `query()`) mà không được xử lý an toàn.
* **Cách thức xử lý:**
  * Tái cấu trúc toàn bộ mã nguồn truy vấn sang **Prepared Statements với tham số hóa (PDO Parameterized Queries)**, triệt tiêu khả năng mã SQL bị diễn giải sai lệch.
* **Căn cứ vi phạm chính sách pháp lý:**
  * **Nghị định 13/2023/NĐ-CP (Điều 9, Khoản 2 & Điều 26):** Vi phạm nghiêm trọng nghĩa vụ *áp dụng các biện pháp an ninh mạng để ngăn chặn việc chiếm đoạt, lộ lọt dữ liệu cá nhân*.
  * **GDPR (Article 32 — Security of Processing):** Không đảm bảo tính bảo mật và toàn vẹn của dữ liệu trong quá trình xử lý.
* **Bài toán Security-as-Code (SaC):**
  * Luật an ninh được mã hóa thành các tệp YAML/JSON trong kho mã (`ci/semgrep-local-rules.yml`), tự động kích hoạt kiểm tra trên runner và chặn đứng mã lỗi trước khi merge.
```yaml
# Minh chứng SaC tại Stage 2 (ci/semgrep-local-rules.yml):
rules:
  - id: php-sqli-taint-concat
    languages: [php]
    severity: ERROR
    mode: taint
    pattern-sources: [pattern: $_GET, pattern: $_POST]
    pattern-sinks: [pattern: query($SQL)]
    message: "Phát hiện SQL Injection (CWE-89)! Nghiêm cấm nối chuỗi trực tiếp vào truy vấn CSDL."
```

---

### THÀNH VIÊN 3: ĐÀO XUÂN MẠNH
* **Vai trò:** Kỹ sư Kiểm định Chất lượng (QA / DevSecOps Engineer)
* **Vấn đề an toàn:** **Lỗ hổng Local File Inclusion (LFI / CWE-22) trong cẩm nang quy chuẩn và Reflected XSS (CWE-79) trong ô tìm kiếm InlaneWeb.**
* **Phân loại nhóm lỗi:** **Nhóm lỗi Mã nguồn (Code Vulnerability)**.
* **Pha trong DevSecOps:** **Pha Build & Code Review / Gate (Stage 2 trong Pipeline)**.
* **Cách thức phát hiện:**
  * **SonarQube SAST:** Phát hiện quy tắc `php:S2083` (Path Traversal / File Inclusion) và `php:S5131` (Reflected Cross-Site Scripting).
  * **Semgrep SAST:** Bộ luật bắt các cấu trúc `include $doc` và `echo $q` thiếu mã hóa thực thể HTML.
  * **Kiểm thử động DAST / Script:** Tự động gửi payload traversal (`../../../../etc/passwd`) và payload XSS (`<script>alert(1)</script>`) để xác minh phản hồi.
* **Cách thức xử lý:**
  * **LFI:** Sử dụng hàm `basename()` và **Whitelist kiểm tra danh mục tài liệu hợp lệ**, cấm triệt để wrapper `php://`:
    ```php
    $allowed = ['incoterms2020.html', 'bill_of_lading.html', 'customs_procedure.html'];
    $doc = basename($_GET['doc'] ?? 'incoterms2020.html');
    if (!in_array($doc, $allowed)) { die("Tài liệu không hợp lệ!"); }
    ```
  * **XSS:** Sử dụng hàm `htmlspecialchars($q, ENT_QUOTES, 'UTF-8')` trước khi render dữ liệu tìm kiếm ra trình duyệt.
* **Căn cứ vi phạm chính sách pháp lý:**
  * **Nghị định 13/2023/NĐ-CP (Điều 13, Khoản 2):** Vi phạm quy định bảo vệ bí mật dữ liệu cá nhân, để rò rỉ mã nguồn cấu hình CSDL và tệp hệ thống nội bộ.
  * **GDPR (Article 5(1)(f) — Integrity and Confidentiality):** Xử lý dữ liệu không đảm bảo tính bảo mật thích hợp, gây nguy cơ chiếm đoạt phiên làm việc và mã độc phía client.
* **Bài toán Security-as-Code (SaC):**
  * Tích hợp tiêu chuẩn chặn **SonarQube Quality Gate Rating A** (`ci/sonarqube-quality-gate.json`). Nếu tồn tại bất kỳ lỗ hổng mức Blocker/Critical, Stage 2 lập tức dừng và từ chối đóng gói Docker image.

---

### THÀNH VIÊN 4: LÊ ĐỨC ANH
* **Vai trò:** Kỹ sư Tự động hóa Hạ tầng (Infrastructure Automation Engineer)
* **Vấn đề an toàn:** **Mất an toàn cấu hình triển khai hạ tầng — Nguy cơ lộ cổng CSDL MariaDB (3306) ra Internet và thiếu cô lập mạng Docker.**
* **Phân loại nhóm lỗi:** **Nhóm lỗi Triển khai & Vận hành (Deployment & Operations)**.
* **Pha trong DevSecOps:** **Pha Release / Deploy (Stage 3 & 4 trong Pipeline)**.
* **Cách thức phát hiện:**
  * Bộ công cụ kiểm thử cấu hình tự động `ci/validate_configs.py` thực thi 21 test case tự động trước khi đóng gói và triển khai.
  * Phân tích tệp khai báo hạ tầng `docker-compose.prod.yml`, kiểm tra danh sách `ports` của dịch vụ `db`. Nếu phát hiện cổng 3306 mở ra máy chủ ngoài mạng cô lập `inlaneweb_net`, pipeline sẽ bị hủy.
* **Cách thức xử lý:**
  * Xóa bỏ chỉ thị ánh xạ `ports: - "3306:3306"` trên môi trường sản xuất.
  * Chỉ mở kết nối CSDL nội bộ thông qua mạng cầu riêng biệt `inlaneweb_net`, bảo đảm chỉ có container `ilfreight_web` mới có quyền giao tiếp với MariaDB.
* **Căn cứ vi phạm chính sách pháp lý:**
  * **Nghị định 13/2023/NĐ-CP (Điều 13, Khoản 1 & Điều 26):** Vi phạm quy định áp dụng biện pháp kỹ thuật an toàn thông tin cơ bản, để lộ giao diện lưu trữ dữ liệu nhạy cảm ra ngoài biên giới kiểm soát.
  * **GDPR (Article 32 — Security of Processing):** Không bảo đảm khả năng chống chịu, khả năng bảo vệ ranh giới mạng và phân vùng an toàn cho hệ thống xử lý dữ liệu.
* **Bài toán Policy-as-Code (PaC):**
  * Các tiêu chuẩn an toàn hạ tầng máy chủ được định nghĩa thành các kịch bản kiểm thử tĩnh (IaC Validation Testing) chạy tự động ở Stage 3:
```python
# Minh chứng PaC tại Stage 3 (ci/validate_configs.py):
def test_db_port_not_exposed(compose_data):
    db_ports = compose_data.get('services', {}).get('db', {}).get('ports', [])
    assert len(db_ports) == 0, "[POLICY VIOLATION] Cổng MariaDB 3306 không được phép ánh xạ ra Internet!"
```

---

### THÀNH VIÊN 5: NGUYỄN PHƯƠNG MAI
* **Vai trò:** Kỹ sư Giám sát & Vận hành (Monitoring & SecOps Engineer)
* **Vấn đề an toàn:** **Thiếu hụt hệ thống ghi nhận log kiểm toán tập trung — Nguy cơ không thể điều tra và vi phạm thời hạn báo cáo sự cố 72 giờ theo luật định.**
* **Phân loại nhóm lỗi:** **Nhóm lỗi Triển khai & Vận hành (Deployment & Operations)**.
* **Pha trong DevSecOps:** **Pha Monitor / Audit (Stage 4 & Vận hành sản xuất 24/7)**.
* **Cách thức phát hiện:**
  * Kiểm toán cấu hình ghi log web server Apache trong `000-default.conf`. Nếu ghi dạng text thô phân tán trên container, log sẽ mất khi container bị recreate.
  * Kiểm tra tính sẵn sàng của cụm thu thập log tập trung **Promtail + Loki 3.0 + Grafana**.
* **Cách thức xử lý:**
  * Cấu hình Apache ghi log lưu lượng dưới dạng **JSON có cấu trúc**: ghi nhận đầy đủ `client_ip`, `uri`, `query` (chứa attack vector), `status`, `duration_us`, `user_agent`.
  * Triển khai cụm Promtail đẩy log tập trung về Loki; cấu hình **8 Panel SIEM trên Grafana** với các bộ lọc LogQL nhận diện cuộc tấn công tức thời (SQLi, LFI, XSS, OS Command).
* **Căn cứ vi phạm chính sách pháp lý:**
  * **Nghị định 13/2023/NĐ-CP (Điều 13 Khoản 3 & Điều 17):** Quy định bắt buộc phải thông báo vi phạm dữ liệu cá nhân cho Bộ Công an (Cục An ninh mạng A05) trong vòng **72 giờ** kể từ khi phát hiện. Nếu không có log kiểm toán tập trung, tổ chức sẽ không thể lập hồ sơ chứng minh và xử lý vi phạm.
  * **GDPR (Article 33 — Notification of a personal data breach to the supervisory authority):** Chế tài phạt tối đa tới 20 triệu EUR hoặc 4% doanh thu toàn cầu nếu không thông báo sự cố trong thời hạn **72 giờ**.
* **Bài toán Observability-as-Code (SaC):**
  * Toàn bộ cấu hình thu thập log, định dạng JSON và câu truy vấn LogQL cảnh báo an ninh được code hóa trong tệp `InlaneWeb/docker-compose.monitoring.yml`.
```logql
# Minh chứng Observability-as-Code (LogQL trên Grafana Panel 3):
{job="apache_json"} | json | uri =~ "/guide" and query =~ "(?i)(\\.\\./|/etc/passwd|php://filter)"
```

---

## 4. KẾ HOẠCH HÀNH ĐỘNG TRIỂN KHAI (ACTION ITEMS)

- [x] **Bước 1:** Hoàn thiện và chuẩn hóa bảng phân bổ 5 thành viên theo đúng 5 pha DevSecOps.
- [x] **Bước 2:** Bổ sung các minh chứng mã nguồn thực tế (LFI và Reflected XSS) vừa được tích hợp và kiểm thử thành công trên Docker.
- [ ] **Bước 3:** Cập nhật nội dung này vào **Bảng 0.1** và **Mục 5.1** của tệp báo cáo chính thức `docs/05-Báo cáo bài tập lớn DevSecOps.md`.
- [ ] **Bước 4:** Xuất bản tài liệu Word `.docx` hoàn chỉnh theo định dạng mẫu của Học viện PTIT để nộp cho giảng viên.
