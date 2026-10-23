# TIÊU CHUẨN KIỂM SOÁT AN NINH VÀ ĐẢM BẢO CHẤT LƯỢNG MÃ NGUỒN
**HỆ THỐNG CỔNG THÔNG TIN VẬN TẢI INLANEWEB**

---

| Thuộc tính | Chi tiết |
| :--- | :--- |
| **Mã tài liệu:** | STD-APPSEC-03 |
| **Dự án:** | InlaneWeb Logistics Portal |
| **Phân loại:** | Tiêu chuẩn kỹ thuật nội bộ (Internal Technical Specification & Governance SOP) |
| **Phiên bản:** | 1.0.0 |
| **Ngày cập nhật:** | 23/10/2026 |
| **Trạng thái:** | Đã phê duyệt |

---

## 1. MỤC ĐÍCH VÀ PHẠM VI ÁP DỤNG

### 1.1. Mục đích
Tài liệu này xác lập khung tiêu chuẩn thống nhất cho toàn bộ hoạt động kiểm thử an ninh tĩnh (Static Application Security Testing - SAST), nguyên tắc xây dựng các mẫu nhận diện lỗ hổng nghiệp vụ, và cơ chế tự động hóa kiểm soát chất lượng phần mềm trong đường ống tích hợp liên tục (CI/CD Pipeline).

Mục tiêu trọng tâm:
* **Dịch chuyển an ninh về phía trước (Shift-Left Security):** Ngăn chặn 100% các lỗ hổng an ninh nghiêm trọng (Critical/High), các điểm rò rỉ thông tin bí mật (Secrets Leakage), và lỗi kiến trúc ngay tại tầng phát triển (Dev Gate).
* **Chuẩn hóa quy trình kỹ thuật phát triển bộ phát hiện:** Thiết lập quy định chặt chẽ về cú pháp, siêu dữ liệu (Metadata), ngưỡng lỗi và phương pháp luận truy vết luồng dữ liệu (Dataflow / Taint Analysis) nhằm duy trì độ chính xác cao, triệt tiêu tỷ lệ cảnh báo giả (False Positive).
* **Đảm bảo tính thực thi tuyệt đối qua mã nguồn (Policy as Code):** Chuyển hóa toàn bộ tiêu chuẩn an ninh và tiêu chí chất lượng thành các rào chắn tự động trong pipeline, loại bỏ hoàn toàn các quyết định phê duyệt cảm tính hoặc thiếu căn cứ kỹ thuật.

### 1.2. Phạm vi áp dụng
* Áp dụng đối với toàn bộ kỹ sư phát triển phần mềm (Software Engineers), kỹ sư an toàn thông tin (Security Engineers / SecOps), và kỹ sư hạ tầng (DevOps Engineers) tham gia vào dự án InlaneWeb.
* Áp dụng trên toàn bộ các thành phần mã nguồn ứng dụng (PHP 8.2), cơ sở dữ liệu (MariaDB SQL Scripts), tệp tin cấu hình container (Docker Compose, Dockerfile), và mã kịch bản tự động hóa CI/CD trong kho chứa `PTIT-DevOps-SonarQube`.

---

## 2. KHUNG KIỂM SOÁT AN NINH PHẦN MỀM ĐA TẦNG

Để bảo vệ toàn diện hệ thống thông tin, quy trình kiểm soát mã nguồn áp dụng mô hình phòng thủ theo chiều sâu (Defense-in-Depth) với 3 công cụ nòng cốt:

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 │           MÔ HÌNH KIỂM SOÁT BẢO MẬT VÀ CHẤT LƯỢNG MÃ NGUỒN             │
 └────────────────────────────────────────────────────────────────────────┘

     MÃ NGUỒN ĐÓNG GÓP (PR VÀO NHÁNH DEV)
        │
        ├─────────────────────────────────────────────────────────────────┐
        ▼                                                                 ▼
 ┌───────────────────────────────┐               ┌────────────────────────────────┐
 │ 1. SEMGREP SECURITY ENGINE    │               │ 2. SONARQUBE COMMUNITY GATE    │
 ├───────────────────────────────┤               ├────────────────────────────────┤
 │ • Quét chuyên sâu ngữ nghĩa   │               │ • Đánh giá chuẩn chất lượng    │
 │ • Taint Analysis Source->Sink │               │ • Xếp hạng Security Rating (A) │
 │ • Nhận diện lỗ hổng OWASP/CWE │               │ • Đo lường độ tin cậy (Bugs)   │
 │ • Khối quy tắc cục bộ dự án   │               │ • Đo lường trùng lặp và Smells │
 └──────────────┬────────────────┘               └───────────────┬────────────────┘
                │                                                │
                └───────────────────────┬────────────────────────┘
                                        │
                                        ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │ 3. BÁO CÁO TỰ ĐỘNG & BẢO VỆ DỮ LIỆU NHẠY CẢM (SECURE STEP SUMMARY)     │
 │    - Tự động che giấu mật khẩu / token (Token Redaction)               │
 │    - Xuất dữ liệu Source-Sink trực quan phục vụ Developer Fix lỗi      │
 │    - Cưỡng chế chặn sáp nhập nếu không đạt ngưỡng Quality Gate         │
 └────────────────────────────────────────────────────────────────────────┘
```

1. **Semgrep SAST Engine:** Công cụ phân tích cú pháp trừu tượng (Abstract Syntax Tree - AST) đa ngôn ngữ, chịu trách nhiệm rà soát các mẫu lỗi an ninh chuyên biệt, truy vết dòng dữ liệu không an toàn (Untrusted Taint Flow) từ điểm nhập liệu người dùng (Source) tới điểm thực thi hệ thống (Sink).
2. **SonarQube Quality Gate:** Nền tảng phân tích mã nguồn toàn diện, chịu trách nhiệm thiết lập tiêu chuẩn kỹ thuật (Quality Profiles), đo lường độ phức tạp, rà soát điểm nóng an ninh (Security Hotspots), và kiểm soát độ trùng lặp mã nguồn (Code Duplication).
3. **Cơ chế giám sát thực thi tự động (Automation Harness):** Hệ thống script Python tiêu chuẩn (`ci/policy_guard.py`, `ci/sonarqube.py`, `ci/semgrep_report.py`) vận hành trong Runner của GitHub Actions nhằm cô lập dữ liệu bí mật và điều phối quá trình kiểm định.

---

## 3. TIÊU CHUẨN KỸ THUẬT XÂY DỰNG MẪU NHẬN DIỆN LỖ HỔNG

Tất cả các quy tắc nhận diện an ninh tùy biến phục vụ dự án bắt buộc phải lưu trữ tập trung tại tệp tin `ci/semgrep-local-rules.yml`. Việc xây dựng và bổ sung mẫu kiểm tra mới phải tuân thủ nghiêm ngặt các yêu cầu kỹ thuật dưới đây.

### 3.1. Cấu trúc đặc tả quy tắc (Specification Schema)
Mỗi quy tắc định nghĩa bằng định dạng YAML phải chứa đầy đủ các trường thông tin tiêu chuẩn:

```yaml
rules:
  - id: <chuẩn_đặt_tên_duy_nhất>
    languages: [<danh_sách_ngôn_ngữ>]
    severity: <ERROR | WARNING | INFO>
    message: "<Thông điệp mô tả ngắn gọn lỗi và hướng dẫn khắc phục>"
    patterns:
      - <mẫu_nhận_diện_cú_pháp>
    metadata:
      cwe: "<Mã định danh CWE và tên chuẩn>"
      owasp: "<Hạng mục OWASP Top 10 tương ứng>"
      presentation: "<Phân loại: configuration | vulnerability | audit>"
```

### 3.2. Quy chuẩn đặt mã định danh (`id`)
* Cú pháp bắt buộc: `<ngôn_ngữ/thành_phần>-<phạm_vi>-<tên_lỗ_hổng_kỹ_thuật>`.
* Quy tắc dùng chữ thường, phân cách bằng dấu gạch ngang (`-`), không sử dụng ký tự đặc biệt hoặc chữ hoa.
* Ví dụ hợp lệ:
  * `php-hardcoded-db-password-fallback` (Kiểm tra giá trị mật khẩu tĩnh trong mã PHP).
  * `compose-hardcoded-mysql-root-password` (Kiểm tra mật khẩu root cố định trong Docker Compose).
  * `php-sqli-unquoted-concatenation` (Kiểm tra nối chuỗi truy vấn cơ sở dữ liệu không qua parameterized query).

### 3.3. Phương pháp luận phân tích luồng dữ liệu (Taint Analysis)
Đối với các lỗ hổng liên quan đến injection (SQL Injection, Command Injection, XSS), quy tắc phải định nghĩa rõ hai thành phần:

1. **Điểm đón dữ liệu (Source):** Nơi dữ liệu từ người dùng hoặc đối tác bên ngoài đi vào ứng dụng mà chưa được xác thực độ tin cậy.
   * Biến toàn cục trong PHP: `$_GET`, `$_POST`, `$_REQUEST`, `$_COOKIE`, `$_SERVER['HTTP_*']`, `file_get_contents('php://input')`.
2. **Điểm thực thi nhạy cảm (Sink):** Các hàm xử lý hoặc giao diện lập trình có nguy cơ gây mất an toàn nếu nhận dữ liệu độc hại.
   * Truy vấn CSDL: `mysqli_query()`, `PDO::query()`, `PDO::exec()`, `mysql_query()`.
   * Thực thi lệnh: `system()`, `exec()`, `passthru()`, `shell_exec()`, `popen()`.
   * Xuất dữ liệu: `echo`, `print`, `printf` không qua mã hóa HTML.

Trường hợp sử dụng kiểm tra dạng mẫu cố định (AST Pattern Matching), phải áp dụng biểu thức chính quy mở rộng (`metavariable-regex`) để loại trừ các biến môi trường hợp lệ dạng `${ENV_VAR}` nhằm ngăn chặn cảnh báo giả.

### 3.4. Phân cấp mức độ nghiêm trọng và Thời hạn xử lý (Remediation SLA)

| Mức độ (`severity`) | Định nghĩa kỹ thuật | Ảnh hưởng tới CI/CD Gate | Thời hạn khắc phục (SLA) |
| :--- | :--- | :---: | :---: |
| **ERROR (Critical/High)** | Các lỗ hổng cho phép thực thi mã từ xa, tiêm mã SQL, lộ lọt thông tin bí mật (Hardcoded Credentials), hoặc vượt qua cơ chế xác thực. | **Chặn ngay lập tức** (Break-the-Build). Không cho phép merge. | Tối đa 04 giờ làm việc kể từ khi phát hiện |
| **WARNING (Medium)** | Các điểm vi phạm an toàn cấu hình, thuật toán mã hóa lỗi thời, thiếu cờ bảo mật cookie, hoặc vi phạm kiến trúc mã nguồn. | Cảnh báo chi tiết trên Step Summary và Báo cáo kiểm định. | Tối đa 24 giờ làm việc |
| **INFO (Low/Best Practice)** | Các gợi ý tối ưu mã nguồn, chuẩn phong cách lập trình an toàn, hoặc phát hiện đoạn mã rác không sử dụng. | Ghi nhận trong danh mục cải tiến kỹ thuật. | Đưa vào backlog xử lý theo sprint |

### 3.5. Vòng đời phát triển và thẩm định một quy tắc mới (Rule Engineering Lifecycle)
Quy trình ban hành một quy tắc nhận diện mới gồm 4 giai đoạn bắt buộc:

```text
  [1. Phân tích lỗ hổng] ──► [2. Soạn thảo Rule] ──► [3. Kiểm thử Test Case] ──► [4. Phê duyệt & Đóng gói]
```

1. **Phân tích lỗ hổng (Vulnerability Research):** Xác định hành vi mã nguồn không an toàn, lập danh mục các cách thức lập trình viên thường viết mã (variants), và xác định các hàm thay thế an toàn (safe remediations).
2. **Soạn thảo quy tắc (Rule Authoring):** Viết định nghĩa theo chuẩn YAML, áp dụng `pattern-inside`, `pattern-not`, hoặc `metavariable-regex` để ràng buộc ngữ cảnh.
3. **Kiểm thử độc lập (Regression & Benchmarking):**
   * *True Positive Test:* Thử nghiệm với các đoạn mã độc hại mẫu để đảm bảo rule phát hiện chính xác 100%.
   * *False Positive Test:* Thử nghiệm với các đoạn mã đã sử dụng kỹ thuật an toàn (Prepared Statements, Filter, Hashing) để đảm bảo rule không bắt nhầm.
4. **Phê duyệt và Tích hợp:** Mở Pull Request vào nhánh `dev`, được xem xét độc lập bởi Kỹ sư trưởng An toàn thông tin (SecOps Lead) trước khi sáp nhập vào kho chứa.

---

## 4. QUẢN TRỊ BỘ TIÊU CHUẨN CHẤT LƯỢNG SONARQUBE

### 4.1. Cấu hình hồ sơ chất lượng (Quality Profiles)
Hệ thống sử dụng bộ quy chuẩn **Sonar way** chính thức cho các ngôn ngữ trong dự án, bao gồm:
* **PHP:** Bộ quy chuẩn kiểm soát bảo mật, lỗi cú pháp, tính tin cậy và cấu trúc mã hướng đối tượng PHP 8.2.
* **SQL / XML / YAML:** Kiểm soát chuẩn cấu hình cơ sở dữ liệu và kịch bản triển khai container.

### 4.2. Điều kiện chặn nghiêm ngặt (Hard Quality Gate Thresholds)
Để bảo đảm mã nguồn đưa vào vận hành đạt tiêu chuẩn độ bền vững cao nhất, hệ thống áp đặt chính sách Quality Gate tùy chỉnh (`DevOps-Draft overall code` tại `ci/sonarqube-quality-gate.json`) với các tiêu chí định lượng:

| Chỉ số kỹ thuật (Metric) | Toán tử | Ngưỡng vi phạm | Diễn giải tiêu chuẩn |
| :--- | :---: | :---: | :--- |
| **Security Rating** (`security_rating`) | `GT` (Lớn hơn) | **1 (Hạng A)** | Tuyệt đối không chấp nhận bất kỳ lỗ hổng bảo mật nào (Vulnerabilities = 0). |
| **Reliability Rating** (`reliability_rating`) | `GT` (Lớn hơn) | **1 (Hạng A)** | Tuyệt đối không chấp nhận bất kỳ lỗi phần mềm tiềm ẩn nào (Bugs = 0). |
| **Maintainability Rating** (`sqale_rating`) | `GT` (Lớn hơn) | **1 (Hạng A)** | Tỷ lệ nợ kỹ thuật (Technical Debt Ratio) phải duy trì ở mức xuất sắc. |
| **Security Hotspots Reviewed** (`security_hotspots_reviewed`) | `LT` (Nhỏ hơn) | **100%** | Toàn bộ 100% các điểm nóng an ninh được SonarQube chỉ định phải được rà soát và đánh giá thủ công. |
| **Duplicated Lines Density** (`duplicated_lines_density`) | `GT` (Lớn hơn) | **10.0%** | Mức độ trùng lặp mã nguồn không được vượt quá 10% tổng số dòng mã nguồn thực thi. |

### 4.3. Quy trình thẩm định ngoại lệ và Cảnh báo giả (False Positive Handling Protocol)
Trường hợp một phát hiện từ SonarQube hoặc Semgrep được xác định là cảnh báo giả hoặc rủi ro đã được kiểm soát bởi cơ chế phòng thủ khác (Compensating Controls):
1. Kỹ sư phát triển lập tài liệu kỹ thuật giải trình (Justification Form) bao gồm:
   * Đường dẫn tệp tin và số dòng phát hiện lỗi.
   * Bằng chứng chứng minh luồng thực thi không thể bị khai thác.
   * Cơ chế phòng vệ bổ sung ở tầng Web Application Firewall (WAF) hoặc Network Policy.
2. SecOps Lead trực tiếp xác minh lại trên môi trường lab.
3. Khi được phê duyệt, ngoại lệ sẽ được xử lý:
   * Với SonarQube: Đánh dấu trạng thái `Won't Fix` hoặc `False Positive` có ghi kèm mã ticket phê duyệt.
   * Với Semgrep: Bổ sung inline annotation `// nosemgrep: <rule-id>` kèm lý do và ngày phê duyệt, hoặc cập nhật trường `pattern-not` trong bộ quy tắc chung.

---

## 5. CƠ CHẾ THẨM ĐỊNH TỰ ĐỘNG TRONG ĐƯỜNG ỐNG CI/CD

Toàn bộ quy chuẩn an ninh và chất lượng được tích hợp trực tiếp thành các trạm kiểm soát tự động trong GitHub Actions workflow ([sonarqube.yml](file:///d:/ThS/DevOpsSec/PTIT-DevOps-SonarQube/.github/workflows/sonarqube.yml)).

### 5.1. Ma trận phân bổ trạm kiểm soát theo Stage

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 │           MA TRẬN KIỂM SOÁT AN NINH THEO VÒNG ĐỜI CI/CD                │
 └────────────────────────────────────────────────────────────────────────┘

 [Sự kiện Pull Request vào nhánh dev]
   │
   ├──► STAGE 1: Policy Guard (branch_policy_guard)
   │     • Kiểm tra định dạng commit & tiêu đề PR ([<nhánh>] <type>(<scope>): <desc>)
   │     • Chặn đứng mã nguồn vi phạm quy ước trước khi tiêu tốn tài nguyên quét
   │
   └──► STAGE 2: Dev Security & Quality Gates (Chạy song song)
         ├─► Semgrep Security SAST (semgrep)
         │    • Nạp bộ quy tắc chuẩn quốc tế: OWASP Top 10, CWE Top 25, Security Audit
         │    • Nạp bộ quy tắc nội bộ: ci/semgrep-local-rules.yml
         │    • Trích xuất trực quan Source & Sink code snippet
         │
         └─► SonarQube Ephemeral Analysis (analyze)
              • Tự động dựng phiên bản SonarQube cô lập trong Runner
              • Áp đặt Quality Gate khắt khe (Rating A, 0 Bugs, 0 Vulnerabilities)
              • Xuất báo cáo độc lập (HTML & JSON Artifacts)

 [Sự kiện Push/Merge vào nhánh main]
   │
   ├──► STAGE 3: Production Gate (production_smoke_test)
   │     • Kiểm tra cú pháp cấu hình giám sát (validate_configs.py)
   │     • Build và triển khai kiểm thử môi trường chạy thực tế (Ephemeral Smoke Test)
   │     • Kiểm tra phản hồi HTTP 200 API /health và HTTP 200 Loki /ready
   │
   └──► STAGE 4: Production CD (2 Jobs độc lập)
         ├─► Job 1: Deploy Observability Platform (Loki, Promtail, Grafana, Autoheal)
         └─► Job 2: Deploy Web Workload (Apache Web, MariaDB Database)
```

### 5.2. Môi trường thực thi cô lập (Ephemeral Container Sandbox)
* Toàn bộ quy trình quét SonarQube diễn ra trong một container SonarQube Community tạm thời, khởi tạo và hủy tự động ngay trong GitHub Actions Runner.
* Đảm bảo tính độc lập tuyệt đối giữa các lần chạy, không phụ thuộc vào hạ tầng máy chủ bên ngoài, và không lưu trữ trạng thái tồn dư (Stateless).

### 5.3. Tiêu chuẩn bảo vệ bí mật thông tin (Token & Credential Redaction)
Hệ sinh thái phân tích mã nguồn tuân thủ nghiêm ngặt nguyên tắc Zero-Trust đối với thông tin nhạy cảm:
* Khóa xác thực dịch vụ nội bộ (`SONAR_TOKEN`, `SONAR_ADMIN_PASSWORD`) chỉ tồn tại trong bộ nhớ tiến trình của Job.
* Hàm `redact()` trong [ci/sonarqube.py](file:///d:/ThS/DevOpsSec/PTIT-DevOps-SonarQube/ci/sonarqube.py) tự động quét và thay thế 100% chuỗi token thành `[REDACTED]` trước khi bất kỳ dòng nhật ký nào được ghi ra bảng điều khiển (Console Log) hoặc tệp báo cáo.
* Tuyệt đối không xuất thông tin bí mật ra GitHub Step Summary hay Artifacts công khai.

### 5.4. Cơ chế thông báo và Trực quan hóa kết quả kiểm định
Khi một Pull Request được kích hoạt:
1. **Semgrep Report Engine (`ci/semgrep_report.py`):**
   * Tổng hợp các điểm vi phạm theo từng cấp độ nghiêm trọng.
   * Tự động trích xuất ngữ cảnh mã nguồn xung quanh vị trí lỗi, hiển thị rõ ràng dòng mã đóng vai trò **Source** (Dữ liệu đầu vào) và dòng mã đóng vai trò **Sink** (Thực thi nhạy cảm).
   * Tạo bản tóm tắt markdown đính kèm trực tiếp vào `$GITHUB_STEP_SUMMARY` và lưu trữ tệp tin chi tiết `reports/semgrep/report.html`.
2. **SonarQube Report Engine (`ci/sonarqube.py`):**
   * Tạo báo cáo tóm tắt các chỉ số cốt lõi (Bugs, Vulnerabilities, Hotspots, Rating).
   * Lưu trữ artifact độc lập `reports/sonarqube-report.html` và `reports/sonarqube-quality-gate.json` với thời hạn lưu trữ 30 ngày để phục vụ kiểm toán tuân thủ.

---

## 6. QUY TRÌNH THAY ĐỔI, ĐỆ TRÌNH VÀ BẢO TRÌ BỘ QUY TẮC

Mọi sự thay đổi đối với bộ quy tắc an ninh hoặc tiêu chuẩn chất lượng đều được quản lý như một thay đổi phần mềm chính thức (Rules as Code).

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 │            QUY TRÌNH QUẢN LÝ THAY ĐỔI BỘ QUY TẮC KIỂM SOÁT             │
 └────────────────────────────────────────────────────────────────────────┘

   [Kỹ sư đề xuất]
          │
          ▼  (1) Tạo nhánh từ dev: namng/feat-rule-sqli
   [Cập nhật ci/semgrep-local-rules.yml & bổ sung Test Cases]
          │
          ▼  (2) Mở PR vào nhánh dev
   [Hệ thống CI thực thi kiểm thử tự động Stage 1 & Stage 2]
          │
          ▼  (3) Kiểm tra chéo (Peer Review) bởi SecOps Lead & Tech Lead
   [Đánh giá tính chuẩn hóa, tỷ lệ cảnh báo giả, và tuân thủ SLA]
          │
          ▼  (4) Phê duyệt & Merge vào nhánh dev
   [Phiên bản rule mới có hiệu lực ngay lập tức cho toàn bộ dự án]
```

### 6.1. Trách nhiệm của các vai trò (RACI Matrix)

| Hoạt động | Kỹ sư phần mềm (Dev) | Kỹ sư an ninh (SecOps) | Trưởng nhóm kỹ thuật (Tech Lead) |
| :--- | :---: | :---: | :---: |
| Đề xuất rule kiểm tra lỗi nghiệp vụ mới | **R** (Thực hiện) | **A** (Chịu trách nhiệm) | **C** (Tham vấn) |
| Đánh giá và xác nhận cảnh báo giả (False Positive) | **C** (Cung cấp chứng cứ) | **R / A** (Thẩm định) | **I** (Theo dõi) |
| Cập nhật ngưỡng Quality Gate trong CI | **I** (Tuân thủ) | **R** (Đề xuất) | **A** (Phê duyệt) |
| Định kỳ rà soát độ nhạy của bộ quy tắc | **C** (Phản hồi) | **R / A** (Thực hiện) | **I** (Theo dõi) |

*(Quy ước: **R** - Responsible; **A** - Accountable; **C** - Consulted; **I** - Informed)*

### 6.2. Hoạt động bảo trì và Tinh chỉnh định kỳ
* **Định kỳ hàng quý:** Đội ngũ SecOps thực hiện rà soát tỷ lệ phát hiện và tỷ lệ cảnh báo giả của toàn bộ quy tắc địa phương. Các quy tắc có tỷ lệ cảnh báo giả vượt quá 5% bắt buộc phải được tái cấu trúc cú pháp hoặc thu hẹp phạm vi nhận diện.
* **Cập nhật tri thức an ninh:** Khi xuất hiện các mẫu tấn công mới hoặc các công bố an ninh liên quan đến ngăn xếp công nghệ của dự án (PHP 8.2, Apache, MariaDB, Docker), bộ quy tắc địa phương phải được cập nhật bổ sung trong vòng không quá 72 giờ làm việc.

---

## 7. ĐIỀU KHOẢN THI HÀNH

1. Tiêu chuẩn này có hiệu lực kể từ ngày ký phê duyệt và bắt buộc áp dụng đối với tất cả các kỹ sư, cán bộ phát triển và đối tác tham gia đóng góp mã nguồn cho dự án InlaneWeb.
2. Mọi hành vi cố tình vô hiệu hóa rào chắn an ninh (như tùy tiện gắn thẻ `nosemgrep` không qua phê duyệt, hạ thấp ngưỡng Quality Gate, hoặc bỏ qua kiểm tra tự động) được coi là vi phạm nghiêm trọng quy chuẩn an toàn thông tin của tổ chức và sẽ bị xử lý kỷ luật kỹ thuật theo quy định hiện hành.
