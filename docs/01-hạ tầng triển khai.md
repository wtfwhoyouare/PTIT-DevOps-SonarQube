# 🏗️ HẠ TẦNG TRIỂN KHAI DỰ ÁN (INFRASTRUCTURE & ENVIRONMENT)

> **Dự án:** InlaneWeb Logistics Portal  
> **Trạng thái:** Tài liệu đặc tả hạ tầng môi trường và kiến trúc container

---

## 1. Môi trường ứng dụng InlaneWeb
- **Web Server:** Apache 2.4 + PHP 8.2 (Containerized qua Dockerfile tại `InlaneWeb/web/Dockerfile`).
- **Database Server:** MariaDB 10.11 LTS (Containerized qua `InlaneWeb/db/Dockerfile`).
- **Orchestration:** Docker Compose (`InlaneWeb/docker-compose.yml`), quản lý mạng nội bộ `inlaneweb_net` và phân quyền dữ liệu.

---

## 2. Hạ tầng CI/CD Runner
- **Runner Environment:** GitHub-hosted runner `ubuntu-24.04`.
- **Ephemeral SAST Engine:** SonarQube Community `26.9.0.129388` khởi chạy dạng container tạm thời trong môi trường job CI.
- **Security Scanner:** Semgrep Community CLI chạy qua `pipx` với ruleset OWASP Top 10, CWE Top 25 và rules cục bộ.

---

## 3. Hạ tầng Giám sát Log tập trung & Tự động phát hiện lỗi (Centralized Logging & Auto-Healing FOSS Stack)

Nhằm tối ưu hóa tài nguyên phần cứng cho môi trường học tập và bài tập lớn (BTL) mà vẫn đáp ứng đầy đủ tiêu chuẩn vận hành công nghiệp, toàn bộ hạ tầng theo dõi và giám sát được thiết kế dựa trên **100% giải pháp Mã nguồn mở (Free & Open-Source Software - FOSS)**, không phụ thuộc vào các dịch vụ đám mây trả phí.

### 3.1. Sơ đồ kiến trúc luồng dữ liệu (Dataflow Architecture)

```text
 ┌────────────────────────────────────────────────────────────────────────────────────────┐
 │                      HẠ TẦNG ỨNG DỤNG (APPLICATION LAYER)                              │
 │                                                                                        │
 │  ┌───────────────────────┐          ┌───────────────────────┐                          │
 │  │      ilfreight_web    │          │      ilfreight_db     │                          │
 │  │    (Apache + PHP 8.2) │          │    (MariaDB 10.11)    │                          │
 │  │                       │          │                       │                          │
 │  │ • Access Log (JSON)   │          │ • Error Log           │                          │
 │  │ • Error Log / Fatal   │          │ • Slow Query Log      │                          │
 │  │ • Healthcheck:        │          │ • Healthcheck:        │                          │
 │  │   curl /health -> 200 │          │   healthcheck.sh      │                          │
 │  └───────────┬───────────┘          └───────────┬───────────┘                          │
 └──────────────┼──────────────────────────────────┼──────────────────────────────────────┘
                │ Docker Log Driver / Volume       │
                ▼                                  ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────┐
 │               HỆ THỐNG THU THẬP & PHÂN TÍCH LOG (LOGGING & METRICS ENGINE)             │
 │                                                                                        │
 │  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
 │  │ Promtail (Log Shipper - Siêu nhẹ, viết bằng Go):                                  │  │
 │  │  - Đọc log container từ Docker Socket (/var/run/docker.sock) và log files.       │  │
 │  │  - Parse log Apache & PHP, tự động gắn nhãn (level=error, status=500, service).  │  │
 │  └──────────────────────────────────────────┬───────────────────────────────────────┘  │
 │                                             │ Đẩy log đã gán nhãn                      │
 │                                             ▼                                          │
 │  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
 │  │ Grafana Loki (Log Aggregation - "Prometheus for logs"):                          │  │
 │  │  - Chỉ index metadata/labels -> Tiết kiệm RAM vượt trội (< 100MB RAM).           │  │
 │  │  - Hỗ trợ LogQL để lọc log lỗi, đếm tần suất HTTP 5xx, lỗi kết nối cơ sở dữ liệu. │  │
 │  │  - Ruler Engine: Tự động đánh giá LogQL để phát hiện bất thường & sinh cảnh báo. │  │
 │  └───────────────────┬──────────────────────────────────────┬───────────────────────┘  │
 └──────────────────────┼──────────────────────────────────────┼──────────────────────────┘
                        │ Log Stream                           │ Kích hoạt Alert Rule
                        ▼                                      ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────┐
 │                   TRỰC QUAN HÓA & CẢNH BÁO TỰ ĐỘNG (DASHBOARD & ALERTS)                │
 │                                                                                        │
 │  ┌────────────────────────────────────────┐     ┌───────────────────────────────────┐  │
 │  │ Grafana OSS Dashboard:                 │     │ Alertmanager / Loki Ruler Alert:  │  │
 │  │  - Real-time Log Stream Viewer         │     │  - Bắn Webhook tức thì tới:       │  │
 │  │  - Biểu đồ tần suất lỗi (4xx, 5xx)     │     │    • Discord Webhook (FOSS/Free)  │  │
 │  │  - Top IP & URL gây lỗi hệ thống       │     │    • Telegram Bot (FOSS/Free)     │  │
 │  │  - Trạng thái DB & phản hồi /health    │     │    • Slack Incoming Webhook       │  │
 │  └────────────────────────────────────────┘     └───────────────────────────────────┘  │
 └────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 3.2. Bốn thành phần cốt lõi của hệ thống

#### 1. Thu thập & Bóc tách Log tập trung (Structured Logging & Log Ingestion)
- **Nguồn dữ liệu log:**
  - **Apache Access Log:** Định dạng kết hợp (Combined Log) và JSON log ghi nhận: Client IP, Request Method, Request URI, HTTP Status Code, Response Time.
  - **Apache / PHP Error Log:** Bắt toàn bộ các lỗi thực thi mức mã nguồn: `Fatal error`, `Parse error`, `Uncaught Exception`, `mysqli_real_connect() failed`.
  - **MariaDB Log:** Ghi nhận lỗi khởi tạo engine InnoDB, lỗi kết nối bị từ chối hoặc lỗi vượt quá tài nguyên.
- **Thành phần thu thập:** **Promtail** container kết nối trực tiếp vào Docker Daemon thông qua `/var/run/docker.sock` hoặc đọc trực tiếp từ thư mục log dùng chung, phân tích cú pháp (Regex/JSON Parser) và đẩy về **Grafana Loki**.

#### 2. Cơ chế tự động phát hiện lỗi & Bắn cảnh báo (Automated Anomaly & Error Detection)
- **Engine phân tích:** **Loki Ruler Engine** hoặc **Alertmanager** chạy nền, liên tục đánh giá các biểu thức truy vấn **LogQL** định kỳ theo chu kỳ 10–30 giây:
  - **Quy tắc `HighHttp5xxRate`:** Kích hoạt cảnh báo khi số lượng phản hồi HTTP 5xx vượt quá ngưỡng cho phép (ví dụ: > 5 lỗi trong 1 phút).
  - **Quy tắc `DatabaseConnectionLost`:** Bắt ngay các cụm từ *"Access denied"*, *"Connection refused"*, hoặc *"Can't connect to MySQL server"* xuất hiện trong log PHP.
  - **Quy tắc `PhpFatalCrash`:** Phát hiện lập tức các sự kiện nghiêm trọng như *"Fatal error"* hoặc *"Stack trace"*.
- **Kênh tiếp nhận cảnh báo (100% Miễn phí):** Tự động format tin nhắn và bắn Webhook trực tiếp vào kênh **Discord** hoặc bot **Telegram** của nhóm phát triển kèm theo thời gian, tên container và đoạn trích xuất log lỗi.

#### 3. Bảng điều khiển trực quan thời gian thực (Grafana Dashboard)
- **Cơ chế nạp tự động (Provisioning):** Toàn bộ cấu hình Datasource Loki và Dashboard được định nghĩa sẵn bằng các tệp YAML/JSON trong kho mã nguồn, tự động khởi tạo ngay khi chạy lệnh `docker compose up` mà không cần cấu hình thủ công:
  - **Thanh trạng thái Live Health:** Hiển thị trực quan trạng thái sống/chết của API `/health` (HTTP 200 OK vs 503 Service Unavailable).
  - **Đồ thị biểu diễn lỗi:** Biểu đồ đường (Time Series) theo dõi biến động số lượng lỗi 4xx, 5xx theo từng phút.
  - **Bộ lọc Log tương tác (Live Log Stream):** Tìm kiếm và tra cứu log tức thì theo từ khóa, mã phản hồi HTTP hoặc mức độ nghiêm trọng (`level=error`, `sqli`).

#### 4. Cơ chế tự phục hồi & Kiểm tra sức khỏe (Auto-Healing & Container Healthcheck)
- **Docker Native Healthcheck & Restart Policy:**
  - Áp dụng cấu hình `restart: always` hoặc `restart: on-failure:5` cho các dịch vụ cốt lõi.
  - Container Web được trang bị câu lệnh Healthcheck định kỳ 10 giây gọi trực tiếp tới endpoint `/health`.
  - Nếu Apache hoặc MariaDB gặp sự cố đơ, nghẽn luồng hoặc sập tiến trình khiến trạng thái container chuyển sang `unhealthy`, Docker Daemon sẽ tự động tiến hành khởi động lại container.
- **Bộ điều phối tự phục hồi (Autoheal Container - FOSS):** Triển khai container `willfarrell/autoheal` lắng nghe các sự kiện Docker socket, tự động phát hiện và thực hiện khởi động lại (restart) ngay tức thì các container bị suy giảm chất lượng dịch vụ hoặc crash.

---

### 3.3. Cấu trúc thư mục triển khai dự kiến

```text
InlaneWeb/
├── monitoring/
│   ├── loki/
│   │   ├── loki-config.yml          # Cấu hình lưu trữ và quy tắc LogQL của Loki
│   │   └── rules/fake/
│   │       └── alert-rules.yml      # Định nghĩa các rule phát hiện lỗi 5xx, DB fail
│   ├── promtail/
│   │   └── promtail-config.yml      # Cấu hình Scrape targets và Labeling log từ Docker
│   ├── grafana/
│   │   ├── provisioning/
│   │   │   ├── datasources/         # Tự động liên kết Loki Datasource
│   │   │   │   └── loki-ds.yml
│   │   │   └── dashboards/          # Tự động nạp Dashboard giám sát hệ thống
│   │   │       ├── dashboard.yml
│   │   │       └── inlaneweb-overview.json
│   └── docker-compose.monitoring.yml # Cụm container giám sát (Loki, Promtail, Grafana, Autoheal)
```

---

### 3.4. Chiến lược triển khai phân tách vòng đời (Decoupled Dual-Track Deployment Strategy)

#### 1. Nguyên lý phân tách vòng đời (Application vs. Standing Infrastructure Lifecycle)
Trong kiến trúc vận hành Production chuẩn SRE/DevSecOps:
* **Ứng dụng Web (`ilfreight_web` / `ilfreight_db`):** Có vòng đời ngắn, biến động cao (High Churn), thay đổi liên tục theo từng commit/feature/bugfix của lập trình viên.
* **Hạ tầng Giám sát (`Loki`, `Promtail`, `Grafana`, `Autoheal`):** Là hạ tầng nền tảng bền vững (Standing Persistent Infrastructure). Hệ thống này phải duy trì hoạt động liên tục 24/7 với **Zero-Downtime**, tuyệt đối **không được phép bị restart kéo theo** mỗi khi có bản release code web mới.
* **Lợi ích vận hành:**
  1. **Không bị mù thông tin (Eliminate Deployment Blind Spots):** Cụm giám sát luôn sống để bắt trọn từng log khởi động và ghi nhận lỗi crash ngay trong tích tắc ứng dụng Web đang deploy.
  2. **Bảo toàn dữ liệu & Buffer:** Tránh việc Promtail mất chỉ mục quét container hoặc Loki bị ngắt quãng tiến trình flush chunk log lên ổ đĩa.
  3. **Tối ưu tài nguyên CI/CD:** Khi chỉ sửa code Web, hệ thống không phải tải lại các image giám sát nặng hàng trăm MB, rút ngắn 80% thời gian chạy pipeline.

#### 2. Sơ đồ kiến trúc phân tách luồng chạy trên Production

```text
 ┌────────────────────────────────────────────────────────────────────────────────────────┐
 │                      MÁY CHỦ PRODUCTION (HOST ENVIRONMENT)                             │
 │                                                                                        │
 │  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
 │  │ [HẠ TẦNG NỀN TẢNG BỀN VỮNG - STANDING OBSERVABILITY PLATFORM] (24/7 Zero-Downtime)│  │
 │  │  • Dịch vụ: ilfreight_loki, ilfreight_promtail, ilfreight_grafana, autoheal      │  │
 │  │  • Quản lý qua: docker-compose.monitoring.yml                                    │  │
 │  │  • Chu kỳ cập nhật: Rất thấp (Chỉ khi đổi Alert Rule hoặc nâng cấp Dashboard)    │  │
 │  │  • Lệnh cập nhật: docker compose -f docker-compose.monitoring.yml up -d          │  │
 │  └──────────────────────────────────────────┬───────────────────────────────────────┘  │
 │                                             │ Lắng nghe Docker Socket                  │
 │                                             │ (/var/run/docker.sock)                   │
 │                                             ▼                                          │
 │  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
 │  │ [KHỐI ỨNG DỤNG NGHIỆP VỤ - APPLICATION WORKLOAD] (Biến động theo từng Release)    │  │
 │  │  • Dịch vụ: ilfreight_web, ilfreight_db                                          │  │
 │  │  • Quản lý qua: docker-compose.yml                                               │  │
 │  │  • Chu kỳ cập nhật: Thường xuyên theo từng Pull Request vào main                 │  │
 │  │  • Lệnh cập nhật: docker compose up -d --no-deps --build web                     │  │
 │  │                                                                                  │  │
 │  │  👉 Khi container Web mới được tạo, Promtail tự động phát hiện (Service         │  │
 │  │     Discovery) và hút log ngay tức khắc mà KHÔNG CẦN restart cụm monitoring!     │  │
 │  └──────────────────────────────────────────────────────────────────────────────────┘  │
 └────────────────────────────────────────────────────────────────────────────────────────┘
```

#### 3. Quy tắc điều phối Idempotent trong CI/CD & Production
* **Lệnh deploy Web độc lập:**
  ```bash
  cd InlaneWeb
  docker compose up -d --no-deps --build web
  ```
  *(Cờ `--no-deps` đảm bảo không tái khởi động DB và không ảnh hưởng đến các service khác)*
* **Lệnh deploy Monitoring độc lập:**
  ```bash
  cd InlaneWeb
  docker compose -f docker-compose.monitoring.yml up -d --remove-orphans
  ```
  *(Docker Compose tự đối chiếu cấu hình, chỉ cập nhật container có file thay đổi, giữ nguyên các container khác)*
