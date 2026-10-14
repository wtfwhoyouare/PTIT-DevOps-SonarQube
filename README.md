# 🚢 PTIT-DevOps-SonarQube

> **Học phần:** Thực hành DevOps / DevSecOps  
> **Ứng dụng mục tiêu:** InlaneWeb Logistics Portal (PHP 8.2 & MariaDB vulnerable-by-design)  
> **Nhóm thực hiện:** Nam, Hải, Mạnh, Đức Anh, Mai  
> **Tài liệu phân công chi tiết:** [PHAN_CONG_NHIEM_VU.md](PHAN_CONG_NHIEM_VU.md)

---

## 👥 Thành viên nhóm & Phân công nhiệm vụ

Chi tiết phân bổ 33 file mã nguồn và 20 lỗi (10 Code Quality + 10 Security) được quy định tại [PHAN_CONG_NHIEM_VU.md](PHAN_CONG_NHIEM_VU.md):

| STT | Thành viên | Vai trò phụ trách | Số lượng file | Phạm vi báo cáo |
| :-: | :--- | :--- | :-: | :--- |
| 1 | **Nam** | DevOps & Database Lead | 7 files | Hạ tầng Docker, MariaDB schema, thư viện CSDL lib/db.php |
| 2 | **Hải** | Core Web, Routing & Layout | 7 files | Cấu hình Apache, PHP runtime, Router index.php, Layout |
| 3 | **Mạnh** | User Auth, Profile & Community | 7 files | Xác thực đăng nhập/đăng xuất, Hồ sơ tài khoản, Thảo luận |
| 4 | **Đức Anh** | Admin Portal & Reporting | 6 files | Bảng điều khiển Quản trị viên, Console nội bộ, Xuất báo cáo |
| 5 | **Mai** | Logistics Tracking & Ports Catalog | 6 files | Tra cứu vận đơn logistics, API hành trình, Danh bạ cảng biển |

---

## 🛡️ DevSecOps Pipeline Architecture

Dự án tích hợp quy trình kiểm thử tĩnh tự động (**SAST**) ngay trên GitHub Actions khi code được merge vào main:

`	ext
Commit / Merge to main
  ├── 1. Kiểm thử Unit Test bộ công cụ báo cáo (python3 -m unittest)
  ├── 2. SonarQube Community SAST & Quality Gate
  │      ├── Ephemeral SonarQube 26.9 container (zero external config)
  │      ├── Phân tích độ tin cậy, chuẩn lập trình, code smells, bugs (23 issues)
  │      ├── Xuất báo cáo toàn diện vào GitHub Step Summary & Artifacts
  │      └── Thực thi Quality Gate kiểm soát chất lượng
  └── 3. Semgrep Security SAST
         ├── Bộ rulesets chính thức từ cộng đồng Semgrep Registry
         │   (p/owasp-top-ten, p/php, p/security-audit, p/cwe-top-25)
         ├── Truy vết phân tích luồng dữ liệu (Taint Tracking: SOURCE -> SINK)
         ├── Phát hiện các lỗ hổng Injection (CWE-89, CWE-79, Misconfiguration)
         └── Xuất báo cáo chi tiết trực quan lên GitHub Actions Step Summary
`

---

## 🚀 Hướng dẫn khởi chạy ứng dụng cục bộ

Khi các thành viên hoàn tất commit mã nguồn vào InlaneWeb/:

`ash
cd InlaneWeb
docker compose up -d --build
`

Ứng dụng sẽ hoạt động tại: http://localhost:8080.
