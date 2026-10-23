# 🚢 PTIT-DevOps-SonarQube

> **Học phần:** Thực hành DevOps / DevSecOps  
> **Ứng dụng mục tiêu:** InlaneWeb Logistics Portal (PHP 8.2 & MariaDB)  
> **Nhóm sinh viên thực hiện:**
> - **Nam** (`namng`) - *Nhóm trưởng / DevOps & Database*
> - **Hải** (`haind`) - *Core Web & Architecture*
> - **Mạnh** (`manhdx`) - *User Authentication & Community*
> - **Đức Anh** (`anhld`) - *Admin Portal & Reporting*
> - **Mai** (`mainp`) - *Logistics Services & Tracking*

---

## 📌 Giới thiệu dự án

**InlaneWeb** là hệ thống cổng thông tin quản lý vận tải và logistics đường biển, được xây dựng trên nền tảng **PHP 8.2** và cơ sở dữ liệu **MariaDB**. Toàn bộ hệ thống được container hóa bằng **Docker & Docker Compose**, vận hành quy trình **DevSecOps** tự động hóa kiểm thử tĩnh bảo mật (SAST) với **SonarQube Community** và **Semgrep**.

---

## 📚 Tài liệu dự án (Documentation)

Hệ thống tài liệu chi tiết được tổ chức trong thư mục [`docs/`](docs/):

- 📜 [**01. Hạ tầng triển khai (docs/01-hạ tầng triển khai.md)**](docs/01-hạ%20tầng%20triển%20khai.md): Kiến trúc Container, máy chủ Runner, cấu hình Docker Compose và mạng nội bộ.
- 📜 [**02. Quy tắc triển khai & Quy ước Git (docs/02-Quy tắc triển khai.md)**](docs/02-Quy%20tắc%20triển%20khai.md): **(Bắt buộc đọc)** Toàn bộ chính sách phân nhánh, quy chuẩn đặt tên Commit (Conventional Commits), quy chuẩn PR 2 tầng, và cơ chế kỹ thuật tự động kiểm tra (CI/CD Guard & Git Hooks).

---

## 🌳 Tổng quan luồng phát triển & Phân nhánh

Dự án áp dụng mô hình phân nhánh nghiêm ngặt:

```text
 ┌──────────────────────────────────────────────────────────────────┐
 │                  SO DO PHAN CAP NHANH & CI/CD LUONG              │
 └──────────────────────────────────────────────────────────────────┘

     [1. NHANH CA NHAN / TINH NANG]
      namng, haind, manhdx, anhld, mainp
         │
         │  • git commit (Theo chuan Conventional Commits)
         │  • git push origin <ten_nhanh_ca_nhan>
         │
         ▼  (1) Mo PR vao dev: [<ma_nhanh>] <loai>(<pham_vi>): <mo ta>
     ┌──────────────────────────────────────────────────────────────┐
     │ [CI/CD Shift-Left Gate] Kiem tra tu dong chat luong ma nguon:│
     │   ├── [Stage 1] Policy Guard (Commit format & PR Title)      │
     │   └── [Stage 2] SonarQube & Semgrep SAST Scanner             │
     └──────────────────────────────┬───────────────────────────────┘
                                    │
                                    │  [PASS SAST & Lead phe duyet]
                                    ▼
     [2. NHANH TICH HOP CHUNG - DEV]
      dev (Tong hop, ket noi va kiem thu toan bo tinh nang)
         │
         ▼  (2) Mo PR vao main: release: vX.Y.Z - <mo ta phat hanh>
     ┌──────────────────────────────────────────────────────────────┐
     │ [CI/CD Production Gate] Kiem thu thuc te truoc release:      │
     │   └── [Stage 3] Dual-Track CD & Smoke Test Healthcheck       │
     └──────────────────────────────┬───────────────────────────────┘
                                    │
                                    │  [PASS Smoke Test & Lead merge]
                                    ▼
     [3. NHANH PRODUCTION - ON DINH TUYET DOI]
      main (San sang trien khai phuc vu nguoi dung)
```

### Ba nguyên tắc cốt lõi:
1. 🚫 **KHÔNG commit và push trực tiếp** lên `main` và `dev`.
2. 🔀 **Pull Request của thành viên CHỈ hướng vào nhánh `dev`** với định dạng tiêu đề: `[<mã_nhánh>] <loại>(<phạm_vi>): <mô tả>`.
3. ⛔ **TUYỆT ĐỐI CẤM tạo PR từ nhánh cá nhân lên `main`.** Nhánh `main` chỉ nhận PR từ `dev` với định dạng Release: `release: vX.Y.Z - <mô tả>`.

👉 *Xem chi tiết bảng tra cứu Types, biểu thức Regex, mẫu lỗi và cách kích hoạt Git Hook cục bộ tại [docs/02-Quy tắc triển khai.md](docs/02-Quy%20tắc%20triển%20khai.md).*

---

## 🛡️ Kiến trúc DevSecOps Pipeline (3 Giai đoạn kiểm soát)

Hệ thống CI/CD được thiết lập tự động hóa 100% trên **GitHub Actions** phân tách thành 3 giai đoạn rõ ràng:

```text
GitHub Actions Pipeline:
  ├── [STAGE 1] Policy Guard — Kiểm tra Nhánh, Commit & PR
  │      └── Kích hoạt nhanh 3-5s: Chặn commit sai Conventional Commits & PR sai nhánh/tiêu đề
  │
  ├── [STAGE 2: Dev Gate] Shift-Left Security & Code Quality (Khi PR hoặc Merge vào DEV)
  │      ├── SonarQube SAST & Code Quality: Quét bugs, code smells, lỗ hổng & chất lượng mã nguồn
  │      └── Semgrep Security SAST: Phân tích luồng dữ liệu Source-to-Sink (SQLi, XSS, Misconfigs)
  │
  └── [STAGE 3: Production Gate] Docker Build & Smoke Test Healthcheck (Khi PR hoặc Merge vào MAIN)
         ├── Build sạch toàn bộ Docker Images (PHP 8.2 & MariaDB)
         ├── Khởi chạy cụm Preview tạm thời trong runner bằng Docker Compose
         ├── Chờ MariaDB đạt trạng thái healthy
         ├── Gọi API /health xác nhận HTTP 200 OK & kết nối DB thông suốt
         └── Smoke Test tải Trang chủ trước khi cho phép nạp code vào Production
```

---

## 🚀 Khởi chạy ứng dụng cục bộ (Local Development)

Yêu cầu môi trường: **Docker** & **Docker Compose**.

1. **Clone repository:**
   ```bash
   git clone https://github.com/wtfwhoyouare/PTIT-DevOps-SonarQube.git
   cd PTIT-DevOps-SonarQube
   ```

2. **Kích hoạt Git Hook kiểm tra commit cục bộ (Khuyên dùng):**
   ```bash
   git config core.hooksPath .githooks
   ```

3. **Khởi chạy cụm dịch vụ:**
   ```bash
   cd InlaneWeb
   docker compose up -d --build
   ```

4. **Truy cập ứng dụng:**
   - 🌐 **Web Portal:** `http://localhost:8080`
   - 💓 **Healthcheck Endpoint:** `http://localhost:8080/health`
   - 🗄️ **MariaDB Database:** Port nội bộ `3306` (Container `inlaneweb_db`)
