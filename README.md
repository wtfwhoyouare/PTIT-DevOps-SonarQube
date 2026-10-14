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

**InlaneWeb** là hệ thống cổng thông tin quản lý vận tải và logistics đường biển, được xây dựng trên nền tảng **PHP 8.2** và cơ sở dữ liệu **MariaDB**. Dự án được triển khai theo mô hình container hóa bằng **Docker & Docker Compose**, tích hợp quy trình **DevSecOps** tự động hóa kiểm thử tĩnh bảo mật (SAST) với **SonarQube Community** và **Semgrep**.

---

## 🌳 Chiến lược phân nhánh & Quy trình làm việc nhóm (Git Branching Strategy)

Dự án áp dụng mô hình phân nhánh chuẩn (Git Feature Branch Workflow) để đảm bảo chất lượng mã nguồn và tính an toàn khi tích hợp:

### 1. Hệ thống các nhánh trong Repository

| Tên nhánh | Mục đích & Quyền hạn |
| :--- | :--- |
| `main` | **Nhánh Production (Stable Release):** Chứa mã nguồn ổn định nhất. **Nghiêm cấm commit và push trực tiếp lên nhánh này.** Chỉ nhận mã nguồn khi Admin chủ động tạo Pull Request và duyệt merge từ nhánh `dev`. |
| `dev` | **Nhánh Integration / Development:** Nơi tích hợp toàn bộ tính năng đang phát triển từ các thành viên trong nhóm. |
| `namng` | Nhánh làm việc cá nhân của thành viên **Nam** |
| `haind` | Nhánh làm việc cá nhân của thành viên **Hải** |
| `manhdx` | Nhánh làm việc cá nhân của thành viên **Mạnh** |
| `anhld` | Nhánh làm việc cá nhân của thành viên **Đức Anh** |
| `mainp` | Nhánh làm việc cá nhân của thành viên **Mai** |

---

### 2. Quy tắc phát triển & Đóng góp mã nguồn (Contribution Rules)

```text
  [Nhánh cá nhân]             [Nhánh Tích hợp]             [Nhánh Production]
   (namng, haind,                  (dev)                         (main)
    manhdx, ...)
         │                            │                             │
         │─── Commit & Push ─────────>│                             │
         │    (Chỉ push lên dev)      │                             │
         │                            │                             │
         │                            │─── Admin Review & Merge ───>│
         │                            │    (Chỉ Admin thực hiện)    │
         │                            │                             ├── [CI/CD Triggered]
         │                            │                             ├── 1. Unit Tests
         │                            │                             ├── 2. SonarQube SAST
         │                            │                             └── 3. Semgrep SAST
```

1. **Phát triển độc lập trên nhánh cá nhân:**
   - Mỗi thành viên làm việc trên nhánh mang tên của mình (`namng`, `haind`, `manhdx`, `anhnd`, `mainp`).
   - Thường xuyên cập nhật mã nguồn mới nhất từ `dev` về nhánh cá nhân:
     ```bash
     git checkout dev
     git pull origin dev
     git checkout <tên_nhánh_cá_nhân>
     git merge dev
     ```

2. **Chỉ commit & push lên nhánh `dev`:**
   - Khi hoàn thành tính năng, thành viên commit và push lên nhánh cá nhân, sau đó tạo **Pull Request (PR) merge vào nhánh `dev`** (hoặc merge trực tiếp vào `dev` theo thỏa thuận nội bộ nhóm).
   - **Tuyệt đối không push trực tiếp lên nhánh `main`**.

3. **Kích hoạt CI/CD khi Admin merge từ `dev` về `main`:**
   - Khi phiên bản trên nhánh `dev` đã được cả nhóm kiểm thử nội bộ hoàn tất và hoạt động ổn định, **Admin/Lead sẽ chủ động tạo Pull Request và thực hiện merge từ `dev` vào `main`**.
   - Thao tác merge vào `main` sẽ **tự động kích hoạt toàn bộ quy trình CI/CD DevSecOps** trên GitHub Actions:
     - Chạy bộ kiểm thử tự động (Unit Tests tooling).
     - Quét toàn diện chất lượng mã nguồn, bugs, code smells và kiểm soát Quality Gate qua **SonarQube SAST**.
     - Phân tích an toàn thông tin, quét lỗ hổng SQL Injection và XSS qua **Semgrep SAST**.

---

## 🛡️ Kiến trúc DevSecOps Pipeline

Hệ thống CI/CD được thiết lập tự động hóa 100% trên **GitHub Actions**:

```text
Merge to main
  ├── 1. Unit Tests & Tooling Validation (python3 -m unittest)
  ├── 2. SonarQube Community SAST & Quality Gate
  │      ├── Khởi tạo container SonarQube 26.9 tạm thời (Ephemeral instance)
  │      ├── Phân tích độ tin cậy, quy chuẩn lập trình, bugs và code smells
  │      ├── Tự động xuất báo cáo chi tiết vào GitHub Step Summary & Artifacts
  │      └── Thực thi Quality Gate kiểm soát tiêu chuẩn chất lượng
  └── 3. Semgrep Security SAST
         ├── Bộ rulesets chính thức từ cộng đồng Semgrep Registry
         │   (p/owasp-top-ten, p/php, p/security-audit, p/cwe-top-25)
         ├── Phân tích luồng dữ liệu chuyên sâu (Taint Tracking: Source -> Sink)
         ├── Phát hiện các lỗ hổng Injection (CWE-89, CWE-79, Misconfiguration)
         └── Xuất báo cáo trực quan kèm đoạn code vi phạm lên GitHub Summary
```

---

## 🚀 Hướng dẫn khởi chạy ứng dụng cục bộ

Yêu cầu môi trường: **Docker** & **Docker Compose**.

1. **Clone repository:**
   ```bash
   git clone https://github.com/wtfwhoyouare/PTIT-DevOps-SonarQube.git
   cd PTIT-DevOps-SonarQube
   ```

2. **Khởi chạy container:**
   ```bash
   cd InlaneWeb
   docker compose up -d --build
   ```

3. **Truy cập ứng dụng:**
   - Cổng thông tin Web: `http://localhost:8080`
   - Cơ sở dữ liệu MariaDB: Cổng nội bộ `3306` (Container `inlaneweb_db`)
