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

| Tên nhánh | Chức năng & Quyền hạn |
| :--- | :--- |
| `main` | **Nhánh Production (Chạy thực tế):** Nhánh này **chỉ sử dụng để lưu trữ mã nguồn chạy production**. Nghiêm cấm commit và push code trực tiếp lên `main`. Tuyệt đối không được tạo Pull Request từ các nhánh đang phát triển cá nhân lên `main`. Nhánh `main` chỉ nhận mã nguồn khi Admin/Lead tạo Pull Request và duyệt merge từ nhánh `dev`. |
| `dev` | **Nhánh Integration (Tổng hợp):** Nhánh này **chỉ sử dụng để tổng hợp lại mã nguồn của toàn bộ thành viên trong nhóm**. Nghiêm cấm commit và push code trực tiếp lên `dev`. Toàn bộ thành viên chỉ được đóng góp mã nguồn bằng cách tạo Pull Request từ nhánh đang code của mình vào `dev`. |
| `namng` | Nhánh làm việc cá nhân của thành viên **Nam** |
| `haind` | Nhánh làm việc cá nhân của thành viên **Hải** |
| `manhdx` | Nhánh làm việc cá nhân của thành viên **Mạnh** |
| `anhld` | Nhánh làm việc cá nhân của thành viên **Đức Anh** |
| `mainp` | Nhánh làm việc cá nhân của thành viên **Mai** |

> 📌 **Chi tiết toàn bộ quy định:** Xem tài liệu đầy đủ tại [docs/02-chính sách triển khai.md](file:///d:/ThS/DevOpsSec/PTIT-DevOps-SonarQube/docs/02-ch%C3%ADnh%20s%C3%A1ch%20tri%E1%BB%83n%20khai.md).

---

### 2. Quy tắc phát triển & Đóng góp mã nguồn (Contribution Rules)

```text
  dev ── cập nhật mã mới ──> nhánh cá nhân (namng, haind, ...)
                               │
                               ├── commit + push lên nhánh cá nhân
                               └── Pull Request ──> dev ── Pull Request + merge ──> main
                                       │               │           │                   │
                                       └── CI/CD quét ─┴───────────┴── CI/CD quét ─────┘
                                           (Shift-Left SAST)           (Post-merge Scan)
```

**⚠️ BA NGUYÊN TẮC BẤT BIẾN (INVIOLABLE RULES):**
1. **User không được commit và push code trực tiếp lên `main` và lên `dev`.**
2. **Chỉ được tạo Pull Request (PR) từ nhánh đang code lên `dev`.**
3. **Tuyệt đối không được tạo Pull Request từ nhánh đang phát triển cá nhân lên `main`.** (Hệ thống CI/CD Guard sẽ tự động chặn đứng nếu vi phạm).

Thực hiện lệnh Git từ thư mục gốc `PTIT-DevOps-SonarQube` (nếu đang ở `InlaneWeb`, chạy `cd ..` trước). Ví dụ dùng nhánh `namng`; các thành viên khác thay bằng nhánh của mình (`haind`, `manhdx`, `anhld`, `mainp`). Không push trực tiếp lên `dev` hoặc `main` trong luồng làm việc này.

**Trước vòng làm việc mới:** Nếu `main` có commit chưa nằm trên `dev`, Admin/Lead mở **Pull requests → New pull request** trên GitHub, chọn **base: `dev`**, **compare: `main`**, review rồi merge để cập nhật `dev`. Mỗi lần merge tạo commit mới trên `dev` cũng sẽ chạy workflow và lưu báo cáo.

1. **Lấy mã mới nhất từ `dev` vào nhánh cá nhân, trước khi sửa file:**

   ```bash
   git fetch origin
   git switch namng
   git pull --ff-only origin namng
   git merge origin/dev
   ```

   Nếu vừa clone và chưa có nhánh `namng` trên máy, dùng `git switch --track origin/namng` thay cho `git switch namng`. Nếu merge báo xung đột, sửa các file bị xung đột, chạy `git add <file-da-sua>` và `git commit` để hoàn tất merge; sau đó mới sửa phần việc của mình.

2. **Commit và push lên nhánh cá nhân:**

   ```bash
   git status
   git add <cac-file-duoc-phan-cong>
   git diff --cached --stat
   git commit -m "Mo ta thay doi"
   git push origin namng
   ```

   Chỉ thêm các file thuộc phần việc cần gửi lên. Nếu Git báo `nothing to commit`, kiểm tra lại `git status` và các file đã sửa.

3. **Tạo PR từ nhánh cá nhân vào `dev` (Kiểm thử Shift-Left SAST):**

   - Trên GitHub, mở **Pull requests → New pull request**, chọn **base: `dev`**, **compare: `namng`** (hoặc nhánh cá nhân tương ứng).
   - Kiểm tra danh sách file thay đổi, nhấn **Create pull request** và ghi rõ nội dung đã làm.
   - **Tự động kích hoạt CI/CD (Shift-Left):** Ngay khi PR được mở hoặc có commit mới đẩy lên PR, workflow SonarQube & Semgrep sẽ tự động kích hoạt để phân tích mã nguồn ngay tại cửa trước của PR. Kết quả kiểm tra (Checks) và Job Summary được đính kèm trực tiếp vào giao diện PR để Lead/Reviewer đánh giá chất lượng trước khi gộp code.
   - Sau khi review, xử lý góp ý và xung đột (nếu có), người phụ trách nhấn **Merge pull request → Confirm merge**. Sau khi merge, sự kiện `push` trên `dev` tiếp tục chạy một lần quét chính thức để lưu trữ Artifacts của trạng thái nhánh tích hợp.

4. **Tạo PR từ `dev` vào `main` để triển khai Production:**

   - Khi các PR cần thiết đã vào `dev`, Admin/Lead mở **Pull requests → New pull request**, chọn **base: `main`**, **compare: `dev`**.
   - Pipeline tiếp tục tự động quét kiểm tra trên PR vào `main`. Review rồi nhấn **Merge pull request → Confirm merge**.
   - Commit mới trên `main` kích hoạt workflow trong `.github/workflows/sonarqube.yml`. Xem kết quả tại **Actions → SonarQube → Job summary / Artifacts**. Run màu xanh vẫn có thể chứa phát hiện bảo mật vì Quality Gate mặc định ở chế độ báo cáo.

Workflow tự động kích hoạt trên cả sự kiện mở **Pull Request** (vào `dev`, `main`) nhằm phát hiện sớm lỗ hổng bảo mật trước khi gộp (Shift-Left), và trên sự kiện **Push / Merge** để lưu trữ báo cáo audit chính thức.

---

## 🛡️ Kiến trúc DevSecOps Pipeline

Hệ thống CI/CD được thiết lập tự động hóa 100% trên **GitHub Actions**:

```text
Sự kiện: Pull Request (Shift-Left) hoặc Merge vào dev / main (Audit Scan)
  ├── 1. Unit Tests & Tooling Validation (python3 -m unittest)
  ├── 2. SonarQube Community SAST & Quality Gate
  │      ├── Khởi tạo container SonarQube 26.9 tạm thời (Ephemeral instance)
  │      ├── Phân tích độ tin cậy, quy chuẩn lập trình, bugs và code smells
  │      ├── Tự động xuất báo cáo chi tiết vào GitHub Step Summary & Artifacts
  │      └── Ghi nhận Quality Gate ở chế độ báo cáo (report-only) hoặc chặn lỗi (enforce)
  └── 3. Semgrep Security SAST
         ├── Bộ rulesets chính thức từ cộng đồng Semgrep Registry
         │   (p/owasp-top-ten, p/php, p/security-audit, p/cwe-top-25)
         ├── Phân tích luồng dữ liệu chuyên sâu (Taint Tracking: Source -> Sink)
         ├── Phát hiện các lỗ hổng Injection (CWE-89, CWE-79, Misconfiguration)
         └── Xuất báo cáo trực quan kèm đoạn code vi phạm lên GitHub Summary & Artifacts
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
