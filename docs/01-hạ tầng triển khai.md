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
| **Tệp điều phối** | `InlaneWeb/docker-compose.yml` | `InlaneWeb/docker-compose.monitoring.yml` |
| **Các dịch vụ** | `ilfreight_web`, `ilfreight_db` | `ilfreight_loki`, `ilfreight_promtail`, `ilfreight_grafana`, `autoheal` |
| **Tần suất cập nhật** | Liên tục theo các Pull Request vào nhánh `main` | Rất thấp (chỉ khi thay đổi quy tắc cảnh báo hoặc nâng cấp phiên bản) |
| **Lệnh triển khai** | `docker compose up -d --no-deps --build web` | `docker compose -f docker-compose.monitoring.yml up -d` |
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

### 3.2. Khối giám sát tập trung và thu thập log (Observability Engine)

#### 1. Trình thu thập dữ liệu (Promtail 3.0):
* **Vai trò:** Log Shipper thu thập luồng log từ các container đang chạy trên host.
* **Cơ chế thu thập:** Gắn socket máy chủ `/var/run/docker.sock` ở chế độ chỉ đọc kết hợp cấu hình `user: root` để đảm bảo quyền truy cập file socket trên hệ điều hành Linux.
* **Quy trình xử lý:** Promtail tự động gắn nhãn (labeling) dựa trên metadata của Docker (container_name, service_name) và áp dụng biểu thức chính quy để bóc tách mã lỗi HTTP, phát hiện stack trace của PHP.
* **Cấu hình chi tiết:** `InlaneWeb/monitoring/promtail/promtail-config.yml`.

#### 2. Máy chủ lưu trữ và xử lý log (Grafana Loki 3.0):
* **Vai trò:** Log Aggregation Server.
* **Nguyên lý lưu trữ:** Chỉ đánh chỉ mục (index) metadata và labels, lưu trữ nội dung log nén thành các chunk nhị phân trên hệ thống tệp cục bộ (`filesystem`). Cấu trúc này giảm mức tiêu thụ bộ nhớ RAM xuống dưới 100MB, phù hợp với mọi quy mô phần cứng.
* **Bộ quy tắc cảnh báo (Loki Ruler Engine):** Định kỳ đánh giá các truy vấn LogQL theo chu kỳ 10 giây.
* **Cấu hình chi tiết:** `InlaneWeb/monitoring/loki/loki-config.yml`.

#### 3. Bộ quy tắc cảnh báo phát hiện sự cố tự động (Alert Rules):
Được định nghĩa tại `InlaneWeb/monitoring/loki/rules/fake/alert-rules.yml`:
* **`HighHttp5xxRate`:** Kích hoạt cảnh báo mức `critical` khi số lượng lỗi HTTP 5xx vượt quá 5 lỗi trong vòng 1 phút.
* **`DatabaseConnectionLost`:** Kích hoạt cảnh báo mức `critical` khi phát hiện các chuỗi thông báo mất kết nối MariaDB (`Access denied`, `Connection refused`, `Can't connect to MySQL server`) trong log của Apache/PHP.
* **`PhpFatalCrash`:** Kích hoạt cảnh báo mức `warning` khi xuất hiện các sự kiện `Fatal error` hoặc `Uncaught Exception`.

#### 4. Trực quan hóa và bảng điều khiển (Grafana 11.0):
* **Cơ chế nạp tự động (Provisioning):** Tự động liên kết Loki Datasource và import Dashboard mẫu `inlaneweb-overview.json` tại thời điểm khởi động container.
* **Nội dung hiển thị:**
  * Giám sát trạng thái nhịp tim API `/health` thời gian thực.
  * Biểu đồ đường phân bố lưu lượng phản hồi HTTP 2xx, 4xx, 5xx.
  * Bộ lọc log stream tương tác trực tiếp theo từ khóa và mức độ cảnh báo.
* **Cấu hình chi tiết:** `InlaneWeb/monitoring/grafana/provisioning/`.

#### 5. Bộ điều phối tự phục hồi (Container Autoheal):
* **Nền tảng:** `willfarrell/autoheal`.
* **Cơ chế vận hành:** Theo dõi trạng thái kiểm tra sức khỏe từ Docker Daemon. Khi container Web bị suy giảm chất lượng dịch vụ hoặc crash (chuyển trạng thái sang `unhealthy`), Autoheal sẽ lập tức ra lệnh khởi động lại container mục tiêu mà không cần can thiệp thủ công.
* **Phạm vi giám sát:** Chỉ áp dụng cho các container được khai báo nhãn `autoheal: "true"`.

---

## 4. SƠ ĐỒ LUỒNG DỮ LIỆU TOÀN HỆ THỐNG

```text
 ┌──────────────────────────────────────────────────────────────────┐
 │                      TẦNG ỨNG DỤNG NGHIỆP VỤ                     │
 │                                                                  │
 │   [ilfreight_web]                     [ilfreight_db]             │
 │   - Apache Access Log (JSON)          - MariaDB Error Log        │
 │   - PHP Error Stream (stderr)         - Healthcheck Service      │
 │   - Healthcheck (/health)             - Volume: db_data          │
 └─────────────────┬─────────────────────────────────┬──────────────┘
                   │                                 │
                   │ Luồng Docker Logging            │
                   ▼                                 ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │                   TẦNG THU THẬP & LƯU TRỮ LOG                    │
 │                                                                  │
 │   [Promtail] (Docker Socket Scraper)                             │
 │   └── Bóc tách nhãn: service, level, http_status                 │
 │            │                                                     │
 │            ▼ Đẩy stream đã gắn nhãn                              │
 │   [Grafana Loki] (TSDB Index & Chunk Storage)                    │
 │   └── Ruler Engine: Thực thi truy vấn LogQL phát hiện lỗi        │
 └─────────────────┬─────────────────────────────────┬──────────────┘
                   │                                 │
                   │ Truy vấn LogQL                  │ Kích hoạt cảnh báo
                   ▼                                 ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │                  TẦNG TRỰC QUAN HÓA & PHẢN ỨNG                   │
 │                                                                  │
 │   [Grafana Dashboard]                 [Webhook & Autoheal]       │
 │   - Bảng theo dõi HTTP 5xx/4xx        - Thông báo Discord/Tele   │
 │   - Luồng Log trực tiếp               - Khởi động lại khi lỗi    │
 └──────────────────────────────────────────────────────────────────┘
```

---

## 5. ĐẶC TẢ MẠNG VÀ BẢO MẬT HẠ TẦNG

1. **Mạng cục bộ (Bridge Network):**
   * Tên định danh: `inlaneweb_net` (được thiết lập rõ ràng `name: inlaneweb_net` trong cả hai tệp compose).
   * Mọi trao đổi giữa Promtail, Loki, Grafana và Web diễn ra trong mạng cô lập này qua DNS nội bộ của Docker.
2. **Cơ chế bảo vệ cổng (Port Exposure):**
   * Môi trường Production chỉ mở công khai cổng dịch vụ Web (`8080` hoặc `80/443`).
   * Cổng cơ sở dữ liệu `3306` tuyệt đối không ánh xạ ra ngoài host, chỉ truy cập nội bộ từ container Web.
   * Cổng Loki `3100` và Grafana `3000` được quản lý truy cập nội bộ hoặc qua VPN quản trị.

---

## 6. QUY CHUẨN CẤU TRÚC THƯ MỤC DỰ ÁN

```text
InlaneWeb/
├── docker-compose.yml                # Quản lý Web và Database
├── docker-compose.monitoring.yml     # Quản lý cụm Giám sát & Tự phục hồi
├── web/
│   ├── Dockerfile                    # Image Apache + PHP 8.2
│   ├── php.ini                       # Cấu hình log errors sang stderr
│   └── src/                          # Mã nguồn ứng dụng Logistics
├── db/
│   ├── Dockerfile                    # Image MariaDB 10.11
│   └── init.sql                      # Dữ liệu khởi tạo hệ thống
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
curl -I http://localhost:8080/health

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
   - **Nhiệm vụ:** Độc lập build và thay thế container ứng dụng Web PHP 8.2 khi có phát hành mới.
   - **Lệnh điều phối:** `docker compose up -d --no-deps --build web`.
   - **Đặc tính:** Tham số `--no-deps` đảm bảo không tái khởi động database và không ảnh hưởng đến cụm logging đang hoạt động.
3. **Hậu kiểm tra (Post-Deployment Verification):** Tự động ping API `/health` của máy chủ Production. Nếu phản hồi mã khác 200, pipeline lập tức ghi nhận lỗi để quản trị viên can thiệp rollback.


