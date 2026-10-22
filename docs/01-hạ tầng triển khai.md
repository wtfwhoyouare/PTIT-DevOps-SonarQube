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
