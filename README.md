# PTIT-DevOps-SonarQube
**HỆ THỐNG CỔNG THÔNG TIN VẬN TẢI INLANEWEB & QUY TRÌNH DEVSECOPS**

---

| Thuộc tính | Chi tiết |
| :--- | :--- |
| **Dự án:** | InlaneWeb Logistics Portal |
| **Công nghệ:** | PHP 8.2, MariaDB 10.11, Docker Compose, Grafana Loki Stack |
| **Học phần:** | Thực hành DevOps / DevSecOps |
| **Tổ chức:** | Học viện Công nghệ Bưu chính Viễn thông (PTIT) |

### Danh sách kỹ sư phụ trách:
* **Nam** (`namng`) - Trưởng nhóm / Kiến trúc DevOps & Hạ tầng cơ sở dữ liệu
* **Hải** (`haind`) - Kỹ sư Web lõi & Kiến trúc hệ thống
* **Mạnh** (`manhdx`) - Kỹ sư Xác thực người dùng & Module cộng đồng
* **Đức Anh** (`anhld`) - Kỹ sư Quản trị hệ thống & Báo cáo số liệu
* **Mai** (`mainp`) - Kỹ sư Nghiệp vụ Logistics & Vận đơn

---

## 1. GIỚI THIỆU HỆ THỐNG

**InlaneWeb Logistics Portal** là nền tảng quản lý vận tải đường biển được xây dựng trên kiến trúc container hóa kết hợp quy trình vận hành bảo mật DevSecOps tự động.

Hệ thống tích hợp:
* **Kiểm tra an ninh mã nguồn tự động (SAST):** Phân tích mã nguồn PHP 8.2 bằng SonarQube Community và Semgrep CLI.
* **Hạ tầng giám sát phân luồng chuyên biệt (Dual-Stream Observability):** Tách bạch độc lập giữa luồng nhật ký ứng dụng web (bắt trọn vẹn Cause Exceptions, chuỗi lỗi lồng nhau, stack trace) và luồng nhật ký lưu lượng HTTP (nhận diện Attack Vectors, payload khai thác và phản hồi rò rỉ Error-Based) qua Promtail 3.0, Grafana Loki 3.0 và Grafana 11.0.
* **Cơ chế tự phục hồi (Container Auto-Healing):** Theo dõi nhịp tim container thông qua Docker Healthcheck và tự động tái khởi động dịch vụ khi phát sinh sự cố.
* **Kiến trúc triển khai phân tách (Dual-Track Deployment):** Vòng đời phát hành ứng dụng web hoạt động độc lập với hạ tầng giám sát 24/7.

---

## 2. HỆ THỐNG TÀI LIỆU TIÊU CHUẨN (SPECIFICATIONS & SOPS)

Toàn bộ quy định kỹ thuật và hướng dẫn vận hành chi tiết được lưu trữ tại thư mục `docs/`:

1. [**Tài liệu đặc tả hạ tầng kỹ thuật và giám sát hệ thống (docs/01-hạ tầng triển khai.md)**](docs/01-h%E1%BA%A1%20t%E1%BA%A7ng%20tri%E1%BB%83n%20khai.md)  
   *Mã hiệu: SPEC-INFRA-01* — Kiến trúc container, nguyên lý phân tách vòng đời ứng dụng và giám sát, cấu hình Promtail/Loki/Grafana, quy tắc cảnh báo sự cố và runbook vận hành.

2. [**Quy chuẩn phân nhánh và triển khai mã nguồn (docs/02-Quy tắc triển khai.md)**](docs/02-Quy%20t%E1%BA%AFc%20tri%E1%BB%83n%20khai.md)  
   *Mã hiệu: POL-DEVOPS-02* — **(Tài liệu bắt buộc)** Ma trận phân quyền nhánh (RACI), tiêu chuẩn Conventional Commits, quy chuẩn Pull Request 2 tầng, và cơ chế kiểm soát kỹ thuật tự động 3 tầng (Git Hooks, GitHub Actions, Branch Protection).

3. [**Tiêu chuẩn kiểm soát an ninh và đảm bảo chất lượng mã nguồn (docs/03-Kiểm soát an ninh và chất lượng mã nguồn.md)**](docs/03-Ki%E1%BB%83m%20so%C3%A1t%20an%20ninh%20v%C3%A0%20ch%E1%BA%A5t%20l%C6%B0%E1%BB%A3ng%20m%C3%A3%20ngu%E1%BB%93n.md)  
   *Mã hiệu: STD-APPSEC-03* — Tiêu chuẩn kiểm thử an ninh tĩnh (SAST), phương pháp luận phân tích luồng dữ liệu (Taint Analysis/Source-Sink), kỹ thuật xây dựng mẫu nhận diện lỗ hổng Semgrep, ngưỡng chặn chất lượng SonarQube Quality Gate và cơ chế thẩm định tự động trong CI/CD.

---

## 3. SƠ ĐỒ PHÂN CẤP NHÁNH VÀ LUỒNG PHÁT TRIỂN

```text
 ┌──────────────────────────────────────────────────────────────────┐
 │               SƠ ĐỒ PHÂN CẤP NHÁNH VÀ LUỒNG PHÁT TRIỂN           │
 └──────────────────────────────────────────────────────────────────┘

     [1. NHÁNH TÍNH NĂNG / CÁ NHÂN]
      namng, haind, manhdx, anhld, mainp
         │
         │  - Thực hiện commit theo chuẩn Conventional Commits
         │  - Push lên remote nhánh cá nhân
         │
         ▼  (1) Mở PR vào dev: [<mã_nhánh>] <loại>(<phạm_vi>): <mô tả>
     ┌──────────────────────────────────────────────────────────────┐
     │ CỔNG KIỂM SOÁT SHIFT-LEFT GATE (Tự động):                    │
     │  - Stage 1: Policy Guard (Xác thực Commit & Tiêu đề PR)      │
     │  - Stage 2: SonarQube & Semgrep SAST Scanner                 │
     └──────────────────────────────┬───────────────────────────────┘
                                    │
                                    │  (Đạt tiêu chuẩn và Lead duyệt)
                                    ▼
     [2. NHÁNH TÍCH HỢP CHUNG - DEV]
      dev (Tổng hợp, kiểm thử tích hợp các phân hệ)
         │
         ▼  (2) Mở PR vào main: release: vX.Y.Z - <mô tả phát hành>
     ┌──────────────────────────────────────────────────────────────┐
     │ CỔNG KIỂM SOÁT PRODUCTION GATE (Tự động):                    │
     │  - Stage 3: Dual-Track CD & Smoke Test Healthcheck           │
     └──────────────────────────────┬───────────────────────────────┘
                                    │
                                    │  (Đạt Smoke Test và Lead duyệt)
                                    ▼
     [3. NHÁNH MÔI TRƯỜNG THỰC TẾ - MAIN]
      main (Trạng thái ổn định tuyệt đối, sẵn sàng triển khai)
```

### Ba nguyên tắc cốt lõi:
1. **Tuyệt đối không commit hoặc push trực tiếp** lên hai nhánh chính: `main` và `dev`.
2. **Mọi Pull Request của thành viên chỉ được hướng vào nhánh `dev`** với định dạng: `[<mã_nhánh>] <loại>(<phạm_vi>): <mô tả>`.
3. **Tuyệt đối cấm tạo Pull Request từ các nhánh cá nhân vào `main`.** Nhánh `main` chỉ nhận mã nguồn từ `dev` với định dạng phát hành: `release: vX.Y.Z - <mô tả>`.

---

## 4. KIẾN TRÚC PIPELINE CI/CD (4 GIAI ĐOẠN ĐỘC LẬP)

Pipeline tự động hóa trên GitHub Actions (`.github/workflows/sonarqube.yml`) gồm 4 giai đoạn:

```text
GitHub Actions Pipeline:
  ├── [STAGE 1] Policy Guard — Kiểm tra Nhánh, Commit & Tiêu đề PR
  │      └── Kích hoạt nhanh 3-5s: Chặn commit sai cú pháp & PR sai nhánh/tiêu đề
  │
  ├── [STAGE 2: Dev Gate] Shift-Left SAST & Kiểm thử an ninh (Khi PR hoặc Merge vào DEV)
  │      ├── SonarQube SAST: Quét nợ kỹ thuật, bugs, code smells và chuẩn PSR-12
  │      ├── Semgrep SAST: Dò tìm lỗ hổng Taint-Tracking (SQLi, XSS, Misconfigurations)
  │      └── Config Validator: Kiểm tra cú pháp YAML/JSON và Alert Rules FOSS
  │
  ├── [STAGE 3: Production Gate] Dual-Track CD & Smoke Test (Khi PR vào MAIN hoặc Push trên MAIN)
  │      ├── Nhận diện thay đổi theo đường dẫn (Path-based selective execution)
  │      ├── Khởi chạy môi trường thử nghiệm tạm thời (Ephemeral Preview Deployment)
  │      ├── Xác nhận MariaDB healthy và endpoint /health phản hồi HTTP 200
  │      ├── Kiểm tra Loki /ready và luồng log bóc tách từ Promtail
  │      └── Smoke Test trang chủ trước khi cho phép nạp code vào Production
  │
  └── [STAGE 4: Production CD] Automated Dual-Track Deployment (Khi Merge vào MAIN)
         ├── Job 1: Deploy Observability Platform (docker compose -f ...monitoring.yml up -d)
         ├── Job 2: Deploy Web Workload (docker compose up -d --no-deps --build web)
         └── Hậu kiểm tra: Xác thực endpoint /health trên máy chủ Production
```

---

## 5. HƯỚNG DẪN TRIỂN KHAI VÀ VẬN HÀNH CỤC BỘ

### Yêu cầu tiên quyết:
* Docker Engine 24.0+
* Docker Compose V2

### Các bước thực hiện:

#### Bước 1: Lấy mã nguồn dự án
```bash
git clone https://github.com/wtfwhoyouare/PTIT-DevOps-SonarQube.git
cd PTIT-DevOps-SonarQube
```

#### Bước 2: Kích hoạt Git Hook kiểm soát commit cục bộ (Khuyến nghị)
```bash
git config core.hooksPath .githooks
```

#### Bước 3: Khởi chạy cụm dịch vụ ứng dụng nghiệp vụ
```bash
cd InlaneWeb
docker compose up -d --build
```

#### Bước 4: Khởi chạy cụm dịch vụ giám sát tập trung
```bash
docker compose -f docker-compose.monitoring.yml up -d
```

#### Bước 5: Kiểm tra kết nối dịch vụ
* **Web Portal:** `http://localhost:8080`
* **Healthcheck API:** `http://localhost:8080/health`
* **Grafana Dashboard:** `http://localhost:3000` (Tài khoản mặc định: `admin` / `admin`)
* **Loki Ingestion Status:** `http://localhost:3100/ready`
