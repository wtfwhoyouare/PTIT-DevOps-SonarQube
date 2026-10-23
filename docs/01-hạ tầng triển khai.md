# TÀI LIỆU ĐẶC TẢ HẠ TẦNG KỸ THUẬT VÀ GIÁM SÁT HỆ THỐNG
**HỆ THỐNG CỔNG THÔNG TIN VẬN TẢI INLANEWEB**

---

| Thuộc tính | Chi tiết |
| :--- | :--- |
| **Mã tài liệu:** | SPEC-INFRA-01 |
| **Dự án:** | InlaneWeb Logistics Portal |
| **Phân loại:** | Tài liệu kỹ thuật nội bộ (Internal Technical Specification) |
| **Phiên bản:** | 2.1.0 |
| **Ngày cập nhật:** | 23/10/2026 |
| **Trạng thái:** | Đã phê duyệt |

---

## 1. TỔNG QUAN VÀ PHẠM VI HẠ TẦNG

Tài liệu này xác lập tiêu chuẩn hạ tầng, kiến trúc container hóa, cơ chế giám sát tập trung và chính sách tự phục hồi cho hệ thống InlaneWeb Logistics Portal. 

Mục tiêu thiết kế:
* **Tính sẵn sàng cao (High Availability):** Đảm bảo hoạt động liên tục của dịch vụ lõi.
* **Tối ưu chi phí:** Ứng dụng 100% công nghệ mã nguồn mở (Free and Open-Source Software - FOSS), không phát sinh chi phí bản quyền thương mại.
* **Tách biệt vòng đời vận hành (Decoupled Lifecycle):** Đảm bảo tần suất cập nhật thường xuyên của ứng dụng web không gây ảnh hưởng hay gián đoạn hạ tầng giám sát và cảnh báo.

---

## 2. NGUYÊN LÝ PHÂN TÁCH VÒNG ĐỜI (DUAL-TRACK LIFECYCLE)

Để ngăn ngừa hiện tượng gián đoạn hệ thống đo lường khi phát hành mã nguồn ứng dụng, hạ tầng được chia tách thành hai khối độc lập:

```text
 ┌──────────────────────────────────────────────────────────────────┐
 │               MÁY CHỦ VẬN HÀNH (HOST ENVIRONMENT)                │
 ├──────────────────────────────────────────────────────────────────┤
 │                                                                  │
 │  [KHỐI HẠ TẦNG NỀN TẢNG BỀN VỮNG - STANDING OBSERVABILITY]       │
 │   Dịch vụ: Loki, Promtail, Grafana, Autoheal                     │
 │   Quản lý: docker-compose.monitoring.yml                         │
 │   Đặc tính: Uptime 24/7, trạng thái tĩnh, chu kỳ cập nhật thấp   │
 │                                                                  │
 │            ▲                                                     │
 │            │ Thu thập log qua Docker Socket                      │
 │            │ Lắng nghe trạng thái container                      │
 │            │                                                     │
 │  [KHỐI ỨNG DỤNG NGHIỆP VỤ - APPLICATION WORKLOAD]                │
 │   Dịch vụ: Web (Apache + PHP 8.2), Database (MariaDB 10.11)      │
 │   Quản lý: docker-compose.yml                                    │
 │   Đặc tính: Biến động cao, cập nhật theo từng bản phát hành      │
 │                                                                  │
 └──────────────────────────────────────────────────────────────────┘
```

### So sánh đặc tính vận hành hai khối:

| Tiêu chí | Khối ứng dụng nghiệp vụ | Khối hạ tầng giám sát |
| :--- | :--- | :--- |
| **Tệp điều phối** | `InlaneWeb/docker-compose.yml` (Dev/Runner)<br>`InlaneWeb/docker-compose.prod.yml` (Production VPS) | `InlaneWeb/docker-compose.monitoring.yml` |
| **Các dịch vụ** | `ilfreight_web`, `ilfreight_db` | `ilfreight_loki`, `ilfreight_promtail`, `ilfreight_grafana`, `autoheal` |
| **Tần suất cập nhật** | Liên tục theo các Pull Request vào nhánh `main` | Rất thấp (chỉ khi thay đổi quy tắc cảnh báo hoặc nâng cấp phiên bản) |
| **Lệnh triển khai** | **Local/CI:** `docker compose up -d`<br>**Production:** Kéo image từ GHCR và chạy `docker compose -f docker-compose.prod.yml up -d` | `docker compose -f docker-compose.monitoring.yml up -d` |
| **Mục tiêu SLA** | Phục vụ người dùng cuối | Sẵn sàng 24/7, ghi nhận log ngay cả khi web đang khởi động lại |

---

## 3. ĐẶC TẢ CHI TIẾT CÁC THÀNH PHẦN HỆ THỐNG

### 3.1. Khối ứng dụng nghiệp vụ (Application Workload)

#### 1. Máy chủ Web (`ilfreight_web`):
* **Nền tảng:** Apache 2.4 kết hợp PHP 8.2 FPM/Module.
* **Đặc tả cấu hình:** `InlaneWeb/web/Dockerfile`.
* **Cấu hình log PHP:** Thiết lập `log_errors = On` và `error_reporting = E_ALL` tại `InlaneWeb/web/php.ini` nhằm định tuyến toàn bộ lỗi runtime sang luồng `stderr` chuẩn của Apache, phục vụ quá trình bóc tách dữ liệu tự động.
* **Kiểm tra sức khỏe (Healthcheck):** Định kỳ kiểm tra endpoint `/health` thông qua lệnh `curl -f http://localhost/health || exit 1`. Chu kỳ kiểm tra 10 giây, thời gian chờ tối đa 3 giây, ngưỡng lỗi 3 lần.

#### 2. Cơ sở dữ liệu (`ilfreight_db`):
* **Nền tảng:** MariaDB 10.11 LTS.
* **Đặc tả cấu hình:** `InlaneWeb/db/Dockerfile`.
* **Quản trị dữ liệu:** Sử dụng Docker Volume định danh `db_data` gắn vào `/var/lib/mysql` để bảo toàn dữ liệu độc lập với vòng đời của container.
* **Kiểm tra sức khỏe:** Sử dụng script `healthcheck.sh` thực thi truy vấn nội bộ `mariadb-admin ping`.

---

---

### 3.2. Khối giám sát tập trung và thu thập log (Observability Engine)

Hệ thống phân tách kiến trúc nhật ký thành **hai luồng chẩn đoán độc lập (Decoupled Dual-Stream Logging)**:

#### 1. Luồng nhật ký ứng dụng web (Application-Level Exception & Runtime Diagnostics):
* **Cơ chế thu thập:** Thực hiện qua module lõi `InlaneWeb/web/src/lib/logger.php` và đăng ký toàn cục tại `index.php`.
* **Trọng tâm giám sát:** Bắt trọn vẹn mọi nguyên nhân ngoại lệ (*Cause Exceptions*), lỗi cú pháp cơ sở dữ liệu và chuỗi lỗi lồng nhau (*Nested Root Causes*).
* **Các thuộc tính bắt buộc:**
  * `class`: Định danh lớp ngoại lệ (ví dụ: `mysqli_sql_exception`, `TypeError`, `RuntimeException`).
  * `root_cause`: Chuỗi thông điệp mô tả nguyên nhân cốt lõi phát sinh lỗi.
  * `cause_chain`: Danh sách các ngoại lệ tiền nhiệm được liên kết qua phương thức `$e->getPrevious()`.
  * `stack_trace`: Dấu vết ngăn xếp chi tiết hỗ trợ điều tra gỡ lỗi.
  * `file` & `line`: Vị trí chính xác phát sinh ngoại lệ trong mã nguồn.

#### 2. Luồng nhật ký lưu lượng HTTP và an ninh mạng (HTTP Traffic & Attack Diagnostics):
* **Cơ chế thu thập:** Được bàn giao hoàn toàn cho máy chủ web Apache xử lý trực tiếp thông qua cấu hình `CustomLog` định dạng JSON (`apache_json` tại `InlaneWeb/web/apache/000-default.conf`). Giải pháp này giúp giải phóng tải cho ứng dụng PHP InlaneWeb, đảm bảo 100% mọi request được ghi nhận phi tập trung ngay tại tầng proxy/web server.
* **Trọng tâm giám sát:**
  * **Vector tấn công (Attack Vectors):** Ghi nhận đầy đủ Method, Client IP, Request URI, và toàn bộ Query String (`%q`) chứa các vector tấn công phổ biến (SQL Injection như `' OR 1=1`, `UNION SELECT`, `SLEEP()`, `load_file`; Path Traversal `../`; Command Injection `;`; XSS).
  * **Phản hồi lỗi hiển thị (Error-Based Response Leaks):** Giám sát trạng thái phản hồi HTTP (`%>s`) kết hợp các mã lỗi máy chủ (HTTP 4xx, HTTP 5xx) và chuỗi thông báo lỗi cú pháp rò rỉ (`SQL Error:`, `syntax error in your SQL`, `Fatal error:`).

#### 3. Trình thu thập dữ liệu (Promtail 3.0):
* **Vai trò:** Log Shipper thu thập luồng log từ các container đang chạy trên host qua `/var/run/docker.sock`.
* **Phân loại nhãn tự động:**
  * Luồng ứng dụng: Gán nhãn `log_category="app_exception"`, `has_cause_exception="true"`.
  * Luồng tấn công SQLi: Gán nhãn `log_category="http_traffic"`, `traffic_type="attack_vector"`, `vuln_category="sqli"`.
  * Luồng tấn công Traversal/LFI: Gán nhãn `log_category="http_traffic"`, `traffic_type="attack_vector"`, `vuln_category="traversal_lfi"`.
  * Luồng tấn công XSS: Gán nhãn `log_category="http_traffic"`, `traffic_type="attack_vector"`, `vuln_category="xss"`.
  * Luồng tấn công Command Injection: Gán nhãn `log_category="http_traffic"`, `traffic_type="attack_vector"`, `vuln_category="command_injection"`.
  * Luồng HTTP rò rỉ lỗi: Gán nhãn `log_category="http_traffic"`, `traffic_type="error_based_leak"`, `vuln_category="error_based_leak"`.
* **Cấu hình chi tiết:** `InlaneWeb/monitoring/promtail/promtail-config.yml`.

#### 4. Máy chủ lưu trữ và xử lý log (Grafana Loki 3.0):
* **Vai trò:** Log Aggregation Server. Lưu trữ các chunk log nén trên filesystem và phân tách luồng truy vấn LogQL theo từng category độc lập.
* **Cấu hình chi tiết:** `InlaneWeb/monitoring/loki/loki-config.yml`.

#### 5. Bộ quy tắc cảnh báo phát hiện sự cố tự động (Alert Rules):
Được định nghĩa tại `InlaneWeb/monitoring/loki/rules/fake/alert-rules.yml`:
* **`ApplicationCauseExceptionDetected`:** Kích hoạt cảnh báo mức `critical` khi phát hiện chuỗi ngoại lệ nguyên nhân phát sinh trong container `ilfreight_web`.
* **`HttpSqlInjectionDetected`:** Kích hoạt cảnh báo mức `critical` khi phát hiện payload SQL Injection (UNION SELECT, Time-based, Boolean, Out-of-band exfil).
* **`HttpPathTraversalDetected`:** Kích hoạt cảnh báo mức `high` khi phát hiện payload Path Traversal / LFI (`../`, `/etc/passwd`, PHP wrappers).
* **`HttpXssDetected`:** Kích hoạt cảnh báo mức `warning` khi phát hiện mã kịch bản XSS (`<script>`, event handlers, SVG injection).
* **`HttpCommandInjectionDetected`:** Kích hoạt cảnh báo mức `critical` khi phát hiện ký tự nối lệnh hệ thống (`;`, `|`, `&&`, shell binaries).
* **`HttpErrorBasedResponseLeak`:** Kích hoạt cảnh báo mức `high` khi phát hiện phản hồi HTTP trả về client có chứa thông tin lỗi cú pháp SQL hoặc rò rỉ error-based.
* **`HighHttp5xxRate`:** Cảnh báo mức `critical` khi tần suất lỗi HTTP 5xx tăng vọt.
* **`DatabaseConnectionLost`:** Cảnh báo mức `critical` khi ứng dụng mất kết nối tới MariaDB.

#### 6. Trực quan hóa và bảng điều khiển (Grafana 11.0):
* Dashboard `inlaneweb-overview.json` được bố trí thành 8 panel chuyên biệt phân tách theo từng loại lỗ hổng:
  * Panel 1: Giám sát toàn bộ luồng Application Cause Exceptions & Stacktraces.
  * Panel 2: Giám sát chuyên sâu tấn công SQL Injection (SQLi).
  * Panel 3: Giám sát chuyên sâu tấn công Path Traversal & Local File Inclusion (LFI/RFI).
  * Panel 4: Giám sát chuyên sâu tấn công Cross-Site Scripting (XSS).
  * Panel 5: Giám sát chuyên sâu tấn công Remote Code Execution & Command Injection (CMDi).
  * Panel 6: Giám sát các phản hồi rò rỉ lỗi Error-Based và mã lỗi HTTP 4xx/5xx.
  * Panel 7: Biểu đồ biến động tần suất sự kiện theo từng loại lỗ hổng (Multi-Vector Incident Rate).
  * Panel 8: Nhật ký truy vấn và kết nối cơ sở dữ liệu MariaDB.

#### 7. Bộ điều phối tự phục hồi (Container Autoheal):
* **Nền tảng:** `willfarrell/autoheal`.
* **Cơ chế:** Tự động kích hoạt khởi động lại container Web khi trạng thái sức khỏe chuyển sang `unhealthy`.

---

## 4. SƠ ĐỒ LUỒNG DỮ LIỆU TOÀN HỆ THỐNG

```text
 ┌──────────────────────────────────────────────────────────────────────────────────┐
 │                          TẦNG ỨNG DỤNG NGHIỆP VỤ & HTTP                          │
 │                                                                                  │
 │   [ilfreight_web]                                                                │
 │    ├── LUỒNG 1: LOG ỨNG DỤNG (Application Exceptions & Cause Chains)             │
 │    │    - Throwable Catching, Nested Causes ($e->getPrevious()), Stack Traces    │
 │    │    - Database Query Failures (mysqli_error())                               │
 │    │                                                                             │
 │    └── LUỒNG 2: LOG HTTP (Traffic, Attack Vectors & Error-Based Leaks)           │
 │         - Detailed Apache Access Log (URI, Query String, Duration, Status)       │
 │         - Pre-Router Attack Vector Capture (SQLi, Traversal, XSS)                │
 │         - Post-Execution Error-Based Inspection (Response Body Error Leaks)      │
 └─────────────────────────┬────────────────────────────────────────────────────────┘
                           │
                           │ Docker Socket Log Streaming
                           ▼
 ┌──────────────────────────────────────────────────────────────────────────────────┐
 │                          TẦNG THU THẬP & PHÂN LUỒNG LOG                          │
 │                                                                                  │
 │   [Promtail] (Docker Socket Scraper)                                             │
 │    ├── Bóc tách nhãn Luồng 1: {log_category="app_exception", level="error"}      │
 │    └── Bóc tách nhãn Luồng 2: {log_category="http_traffic", traffic_type="..."}  │
 └─────────────────────────┬────────────────────────────────────────────────────────┘
                           │
                           │ Ingestion qua Loki HTTP Push API
                           ▼
 ┌──────────────────────────────────────────────────────────────────────────────────┐
 │                         TẦNG LƯU TRỮ & CẢNH BÁO TẬP TRUNG                        │
 │                                                                                  │
 │   [Grafana Loki] (TSDB Index & Compressed Chunks)                                │
 │    ├── Ruler Rule 1: ApplicationCauseExceptionDetected                           │
 │    ├── Ruler Rule 2: HttpAttackVectorDetected                                    │
 │    └── Ruler Rule 3: HttpErrorBasedResponseLeak                                  │
 └─────────────────────────┬────────────────────────────────────────────────────────┘
                           │
                           ▼ Truy vấn LogQL phân tách
 ┌──────────────────────────────────────────────────────────────────────────────────┐
 │                          TẦNG TRỰC QUAN HÓA & PHẢN ỨNG                           │
 │                                                                                  │
 │   [Grafana Dashboard]                                                            │
 │    ├── Khu vực 1: Application Cause Exceptions & Stacktraces                     │
 │    ├── Khu vực 2: HTTP Attack Vectors & Parameter Inspection                     │
 │    └── Khu vực 3: HTTP Error-Based Response Leaks & Status Rates                 │
 └──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. ĐẶC TẢ MẠNG VÀ BẢO MẬT HẠ TẦNG

1. **Mạng cục bộ (Bridge Network):**
   * Tên định danh: `inlaneweb_net` (được thiết lập rõ ràng `name: inlaneweb_net` trong cả hai tệp compose).
   * Mọi trao đổi giữa Promtail, Loki, Grafana và Web diễn ra trong mạng cô lập này qua DNS nội bộ của Docker.
2. **Cơ chế bảo vệ cổng (Port Exposure):**
   * Môi trường Production chỉ mở công khai cổng dịch vụ Web (`8088` hoặc `80/443` qua reverse proxy).
   * Cổng cơ sở dữ liệu `3306` tuyệt đối không ánh xạ ra ngoài host, chỉ truy cập nội bộ từ container Web.
   * Cổng Loki `3100` và Grafana `3000` được quản lý truy cập nội bộ hoặc qua VPN quản trị.

---

## 6. QUY CHUẨN CẤU TRÚC THƯ MỤC DỰ ÁN

```text
InlaneWeb/
├── docker-compose.yml                # Quản lý Web và Database (Local & Runner Smoke Test)
├── docker-compose.prod.yml           # Quản lý Web và Database trên Production (Image từ GHCR)
├── docker-compose.monitoring.yml     # Quản lý cụm Giám sát & Tự phục hồi
├── web/
│   ├── Dockerfile                    # Image Apache + PHP 8.2 (Self-contained)
│   ├── php.ini                       # Cấu hình log errors sang stderr
│   └── src/                          # Mã nguồn ứng dụng Logistics
├── db/
│   ├── Dockerfile                    # Image MariaDB 10.11 (Self-contained)
│   └── init.sql                      # Dữ liệu khởi tạo hệ thống (Idempotent)
└── monitoring/
    ├── loki/
    │   ├── loki-config.yml           # Cấu hình lưu trữ và ruler của Loki
    │   └── rules/fake/
    │       └── alert-rules.yml       # Quy tắc phát hiện sự cố 5xx, DB fail
    ├── promtail/
    │   └── promtail-config.yml       # Cấu hình Scrape và gắn nhãn Docker
    └── grafana/
        └── provisioning/
            ├── datasources/
            │   └── loki-ds.yml       # Tự động nạp Datasource Loki
            └── dashboards/
                ├── dashboard.yml     # Khai báo đường dẫn dashboard
                └── inlaneweb-overview.json # Bảng điều khiển giám sát
```

---

## 7. QUY TRÌNH VẬN HÀNH VÀ LỆNH ĐIỀU PHỐI (RUNBOOK)

### 7.1. Khởi tạo môi trường lần đầu

```bash
# 1. Di chuyển vào thư mục dịch vụ
cd InlaneWeb

# 2. Khởi tạo hạ tầng ứng dụng nghiệp vụ và mạng nội bộ
docker compose up -d --build

# 3. Khởi tạo hạ tầng giám sát và kết nối mạng dùng chung
docker compose -f docker-compose.monitoring.yml up -d
```

### 7.2. Triển khai phát hành ứng dụng Web (Không gián đoạn giám sát)

Khi có bản cập nhật mã nguồn PHP hoặc cấu hình Web, thực hiện tái triển khai độc lập dịch vụ Web:

```bash
cd InlaneWeb

# Tái xây dựng và thay thế container Web mà không khởi động lại DB hay cụm Monitoring
docker compose up -d --no-deps --build web
```
*Lưu ý:* Tham số `--no-deps` ngăn chặn việc khởi động lại cơ sở dữ liệu; hạ tầng Promtail/Loki duy trì hoạt động 100% để thu thập log trong suốt tiến trình thay thế container.

### 7.3. Cập nhật cấu hình giám sát và quy tắc cảnh báo

Khi cập nhật các quy tắc trong `alert-rules.yml` hoặc bảng điều khiển Grafana:

```bash
cd InlaneWeb

# Áp dụng thay đổi cấu hình giám sát
docker compose -f docker-compose.monitoring.yml up -d --remove-orphans
```

### 7.4. Kiểm tra sức khỏe toàn bộ hệ thống

```bash
# 1. Kiểm tra trạng thái toàn bộ container
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 2. Kiểm tra sức khỏe API nội bộ
curl -I http://localhost:8088/health

# 3. Kiểm tra tính sẵn sàng của hệ thống lưu trữ log
curl -s http://localhost:3100/ready
```

---

## 8. ĐẶC TẢ TỰ ĐỘNG HÓA TRIỂN KHAI PRODUCTION (CONTINUOUS DEPLOYMENT)

Hệ thống hỗ trợ cơ chế triển khai tự động trực tiếp từ GitHub Actions lên máy chủ Production (`[STAGE 4: Production CD]`):

### 8.1. Danh mục biến bí mật (GitHub Repository Secrets)

Để kích hoạt tính năng tự động SSH và deploy lên máy chủ thật, quản trị viên cấu hình các Secrets sau tại **Settings → Secrets and variables → Actions**:

| Tên Secret | Bắt buộc | Mô tả |
| :--- | :---: | :--- |
| `PROD_HOST` | Có | Địa chỉ IP hoặc tên miền FQDN của máy chủ Production |
| `PROD_USER` | Có | Tên tài khoản người dùng có quyền quản trị Docker trên host |
| `PROD_SSH_KEY` | Có | Khóa riêng tư SSH Private Key (OpenSSH RSA/Ed25519) |
| `PROD_PORT` | Không | Cổng SSH máy chủ (Mặc định: `22`) |
| `PROD_PATH` | Không | Đường dẫn thư mục cài đặt dự án trên máy chủ (Mặc định: `/opt/inlaneweb`) |

### 8.2. Kiến trúc phân tách 2 Job triển khai độc lập (Decoupled Stage 4 CD)

Giai đoạn Stage 4 được thiết kế phân tách hoàn toàn thành **2 Jobs độc lập** chạy song song hoặc có điều kiện trong GitHub Actions, tuyệt đối không gộp chung:

1. **Job `production_deploy_monitoring` (`Deploy Observability Platform`):**
   - **Nhiệm vụ:** Độc lập triển khai hoặc cập nhật cụm Loki, Promtail, Grafana và Autoheal.
   - **Lệnh điều phối:** `docker compose -f docker-compose.monitoring.yml up -d --remove-orphans`.
   - **Đặc tính:** Duy trì tính bền vững 24/7, chỉ tái nạp khi có thay đổi cấu hình giám sát hoặc rules.
2. **Job `production_deploy_web` (`Deploy Web Workload`):**
   - **Nhiệm vụ:** Độc lập kéo Docker Images an toàn đã qua kiểm thử từ GHCR (`inlaneweb` và `inlaneweb-db`) và cập nhật container qua `docker-compose.prod.yml`.
   - **Lệnh điều phối:** `INLANEWEB_IMAGE=<ghcr_web> INLANEWEB_DB_IMAGE=<ghcr_db> docker compose -f docker-compose.prod.yml up -d --remove-orphans`.
   - **Đặc tính:** Không cần mã nguồn hay tiến trình build trên host (Self-contained Image), bảo toàn 100% dữ liệu database qua volume `db_data` và không gián đoạn cụm logging.
3. **Hậu kiểm tra (Post-Deployment Healthcheck Loop):** Tự động thăm dò API `http://127.0.0.1:8088/health` với vòng lặp 30 lần (mỗi lần cách nhau 3s). Nếu đạt HTTP 200 thì hoàn tất triển khai thành công; nếu sau 30 lần không đạt, pipeline tự động trích xuất container logs chẩn đoán và báo lỗi.


