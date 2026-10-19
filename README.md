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
  dev ── cập nhật mã mới ──> nhánh cá nhân (namng, haind, ...)
                               │
                               ├── commit + push lên nhánh cá nhân
                               └── Pull Request ──> dev ── Pull Request + merge ──> main
                                                                      │
                                                                      └── GitHub Actions: kiểm thử,
                                                                          SonarQube, Semgrep
```

1. **Phát triển độc lập trên nhánh cá nhân:**
   - Mỗi thành viên làm việc trên nhánh mang tên của mình (`namng`, `haind`, `manhdx`, `anhld`, `mainp`).
   - Lấy mã mới nhất từ `dev` vào nhánh cá nhân trước khi sửa. Xem lệnh cụ thể ở phần **Quy trình đưa mã lên GitHub và chạy CI/CD** bên dưới.

2. **Commit và push lên nhánh cá nhân:**
   - Khi hoàn thành, thành viên push lên nhánh cá nhân rồi tạo **Pull Request (PR) vào `dev`**; người phụ trách review và merge PR.
   - Không push trực tiếp lên `dev` hoặc `main` trong luồng làm việc này.

3. **Kích hoạt CI/CD khi Admin merge từ `dev` về `main`:**
   - Khi mã trên `dev` sẵn sàng tích hợp, **Admin/Lead tạo PR `dev` → `main`, review và merge**.
   - Workflow hiện tại chỉ tự chạy khi có commit mới trên `main` (sự kiện `push`), bao gồm commit do merge PR tạo ra. Push lên nhánh cá nhân, push lên `dev` hoặc chỉ mở PR sẽ chưa chạy workflow này.
   - Sau khi merge vào `main`, GitHub Actions sẽ:
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

### Quy trình đưa mã lên GitHub và chạy CI/CD

Thực hiện các lệnh Git từ thư mục gốc `PTIT-DevOps-SonarQube` (nếu đang ở `InlaneWeb`, chạy `cd ..` trước). Ví dụ dưới đây dùng nhánh `namng`; các thành viên khác thay bằng nhánh của mình, như `haind` hoặc `mainp`.

**Trước vòng làm việc mới:** Nếu `main` có commit chưa nằm trên `dev`, Admin/Lead tạo PR với **base: `dev`**, **compare: `main`**, review và merge để cập nhật `dev`. Việc này không kích hoạt workflow SonarQube/Semgrep hiện tại. Sau đó các thành viên thực hiện bước 1 để lấy bản `dev` mới.

**1. Lấy mã mới nhất từ `dev` vào nhánh cá nhân, trước khi sửa file:**

```bash
git fetch origin
git switch namng
git pull --ff-only origin namng
git merge origin/dev
```

Nếu vừa clone và chưa có nhánh `namng` trên máy, dùng `git switch --track origin/namng` thay cho `git switch namng`. Nếu `git merge origin/dev` báo xung đột, sửa các file bị xung đột, chạy `git add <file-da-sua>` và `git commit` để hoàn tất merge. Sau đó mới tiếp tục chỉnh sửa phần việc của mình.

**2. Commit và push thay đổi lên nhánh cá nhân:**

```bash
git status
git add <cac-file-duoc-phan-cong>
git diff --cached --stat
git commit -m "Mo ta thay doi"
git push origin namng
```

Chỉ thêm các file thuộc phần việc cần gửi lên. Nếu Git báo `nothing to commit` thì kiểm tra lại `git status` và các file đã sửa.

**3. Tạo PR từ nhánh cá nhân vào `dev`:**

1. Mở tab **Pull requests** của repository trên GitHub, chọn **New pull request**.
2. Chọn **base: `dev`** và **compare: `namng`** (hoặc nhánh cá nhân tương ứng). Kiểm tra danh sách file thay đổi và nhấn **Create pull request**.
3. Ghi rõ nội dung đã làm, nhờ người phụ trách review. Sau khi xử lý góp ý và xung đột (nếu có), người phụ trách nhấn **Merge pull request** rồi **Confirm merge**. Mã lúc này nằm trên `dev`; workflow SonarQube/Semgrep hiện tại chưa tự chạy.

**4. Tạo PR từ `dev` vào `main` để chạy CI/CD:**

1. Khi các PR cần thiết đã được merge vào `dev`, Admin/Lead mở **Pull requests → New pull request**.
2. Chọn **base: `main`**, **compare: `dev`**. Kiểm tra các commit, file thay đổi và tạo PR.
3. Sau khi review, Admin/Lead nhấn **Merge pull request** rồi **Confirm merge**. Commit mới trên `main` sẽ kích hoạt workflow trong `.github/workflows/sonarqube.yml`.
4. Vào tab **Actions**, mở run mới nhất của workflow **SonarQube** để xem kết quả trong **Job summary** và **Artifacts**. Một run màu xanh vẫn có thể chứa phát hiện bảo mật vì Quality Gate mặc định ở chế độ báo cáo.

Ở vòng làm việc tiếp theo, lặp lại quy trình từ bước đồng bộ `main` vào `dev` (nếu cần), rồi lấy `dev` mới nhất về từng nhánh cá nhân.
