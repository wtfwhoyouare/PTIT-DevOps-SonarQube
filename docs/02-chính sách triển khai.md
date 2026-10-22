# 📜 CHÍNH SÁCH PHÂN NHÁNH VÀ TRIỂN KHAI MÃ NGUỒN (GIT BRANCHING & DEPLOYMENT POLICY)

> **Dự án:** InlaneWeb Logistics Portal — Hệ thống CI/CD DevSecOps  
> **Cơ quan áp dụng:** Nhóm phát triển PTIT-DevOps-SonarQube  
> **Phiên bản chính sách:** 2.0 (Siết chặt kiểm soát luồng tích hợp & Shift-Left SAST)

---

## 1. Mục đích & Nguyên tắc cốt lõi

Tài liệu này quy định chi tiết và bắt buộc về chức năng, quyền hạn của từng nhánh trong kho mã nguồn (Repository) nhằm bảo vệ tính toàn vẹn của mã nguồn Production, ngăn chặn mã lỗi / lỗ hổng an ninh xâm nhập vào nhánh chính, và chuẩn hóa quy trình phối hợp làm việc nhóm.

### Ba nguyên tắc bất biến (Inviolable Rules):
1. 🚫 **KHÔNG commit và push trực tiếp** lên nhánh `main` và `dev`.
2. 🔀 **CHỈ ĐƯỢC TẠO Pull Request** từ nhánh phát triển cá nhân/feature vào nhánh `dev`.
3. ⛔ **TUYỆT ĐỐI CẤM tạo Pull Request** từ các nhánh đang phát triển cá nhân/feature trực tiếp lên `main`. Nhánh `main` **CHỈ DUY NHẤT** nhận mã nguồn từ nhánh `dev`.

---

## 2. Định nghĩa chức năng & Quyền hạn của các nhánh

```text
 ┌────────────────────────────────────────────────────────────────────────────────────────┐
 │                                   SƠ ĐỒ PHÂN CẤP NHÁNH                                 │
 └────────────────────────────────────────────────────────────────────────────────────────┘

    [Nhánh Tính Năng / Cá Nhân]
     namng, haind, manhdx, anhld, mainp
         │
         │  (1) Tạo PR vào dev (Kiểm thử Shift-Left SAST tự động)
         ▼
    [Nhánh Tích Hợp Chung]
     dev
         │
         │  (2) Duyệt & Merge sau khi Review
         │
         │  (3) Chỉ Admin/Lead mở PR từ dev vào main
         ▼
    [Nhánh Production - Ổn định tuyệt đối]
     main
```

### 2.1. Nhánh `main` — Nhánh Production (Phát hành chính thức)
- **Chức năng duy nhất:** Lưu trữ mã nguồn đã qua kiểm thử, đạt chuẩn an toàn thông tin và sẵn sàng triển khai chạy trên môi trường **Production**.
- **Chính sách siết chặt:**
  - ❌ **Cấm tuyệt đối mọi thành viên (kể cả Admin) commit và push code trực tiếp.**
  - ❌ **Cấm mọi Pull Request đến từ các nhánh cá nhân/feature.**
  - ✅ **Chỉ nhận mã nguồn thông qua Pull Request xuất phát từ duy nhất nhánh `dev`** do Admin/Tech Lead chủ động mở và phê duyệt sau khi đã kiểm thử toàn diện trên nhánh `dev`.

### 2.2. Nhánh `dev` — Nhánh Integration (Tích hợp & Kiểm thử nhóm)
- **Chức năng duy nhất:** Tổng hợp, kết nối và kiểm thử toàn bộ mã nguồn tính năng từ tất cả các thành viên trong nhóm đang trong quá trình phát triển.
- **Chính sách siết chặt:**
  - ❌ **Cấm commit và push code trực tiếp.** Mọi thành viên đều phải làm việc trên nhánh riêng của mình.
  - ✅ **Nhận đóng góp mã nguồn thông qua Pull Request từ các nhánh cá nhân.**
  - 🛡️ **Kiểm thử tự động Shift-Left:** Mỗi PR vào `dev` sẽ tự động kích hoạt pipeline GitHub Actions (SonarQube & Semgrep) để phát hiện sớm các vi phạm Code Quality và Security trước khi được xem xét merge.

### 2.3. Nhánh cá nhân / Feature — Nhánh phát triển độc lập
- **Danh sách nhánh:** `namng` (Nam), `haind` (Hải), `manhdx` (Mạnh), `anhld` (Đức Anh), `mainp` (Mai).
- **Chức năng:** Không gian làm việc riêng biệt của từng thành viên để nghiên cứu, cài đặt chức năng hoặc vá lỗ hổng.
- **Chính sách:**
  - Thành viên tự do commit và push trên nhánh của mình.
  - Phải thường xuyên đồng bộ mã mới nhất từ `dev` về nhánh của mình trước khi viết thêm code:
    ```bash
    git fetch origin
    git switch <tên_nhánh_cá_nhân>
    git merge origin/dev
    ```
  - Khi hoàn thành tính năng, **chỉ được tạo Pull Request hướng tới nhánh đích là `dev`**.

---

## 3. Bảng đối chiếu chính sách hoạt động Git

| Hành động | Nhánh nguồn (Head) | Nhánh đích (Base) | Trạng thái | Cơ chế kiểm soát |
| :--- | :--- | :--- | :---: | :--- |
| `git push` trực tiếp | Máy local | `main` | ❌ **NGHIÊM CẤM** | GitHub Branch Protection / Server Reject |
| `git push` trực tiếp | Máy local | `dev` | ❌ **NGHIÊM CẤM** | GitHub Branch Protection / Quy ước nhóm |
| `git push` | Máy local | Nhánh cá nhân (`namng`, ...) | ✅ **CHO PHÉP** | Tự do phát triển |
| Tạo Pull Request | Nhánh cá nhân | `dev` | ✅ **CHO PHÉP** | Chạy CI/CD kiểm thử Shift-Left |
| Tạo Pull Request | Nhánh cá nhân | `main` | ⛔ **BỊ CHẶN ĐỨNG** | CI/CD Guard Job từ chối & fail ngay lập tức |
| Tạo Pull Request | `dev` | `main` | ✅ **HỢP LỆ** | Chỉ Admin/Lead thực hiện khi release |

---

## 4. Cơ chế cưỡng chế kỹ thuật (Technical Enforcement)

Để chính sách không dừng lại ở mức "lời nói", dự án áp dụng 2 tầng bảo vệ tự động:

### Tầng 1: Tự động chặn bằng GitHub Actions CI/CD Guard
Trong pipeline `.github/workflows/sonarqube.yml`, job `branch_policy_guard` tự động kiểm tra nhánh nguồn và nhánh đích của mọi Pull Request:
- Nếu phát hiện PR hướng vào `main` nhưng nhánh nguồn không phải là `dev`, pipeline sẽ **lập tức ném mã lỗi (exit 1)** kèm cảnh báo đỏ rực:
  > `❌ VI PHẠM CHÍNH SÁCH: Chỉ cho phép tạo Pull Request vào nhánh 'main' từ nhánh 'dev'. Nghiêm cấm tạo PR trực tiếp từ nhánh phát triển '<nhánh>' lên 'main'!`
- Thao tác merge sẽ bị khóa lại trên GitHub.

### Tầng 2: Thiết lập Branch Protection Rules trên GitHub Repository
Admin repository kích hoạt cấu hình bảo vệ trên GitHub Web (**Settings → Branches / Rulesets**):
1. **Áp dụng cho nhánh `main` và `dev`:**
   - [x] **Require a pull request before merging:** Bắt buộc phải thông qua PR, chặn đứng hoàn toàn `git push origin main` hoặc `git push origin dev`.
   - [x] **Require approvals:** Yêu cầu tối thiểu 1 người phê duyệt trước khi merge.
   - [x] **Require status checks to pass before merging:** Bắt buộc job `branch_policy_guard` phải báo xanh (Success).
   - [x] **Do not allow bypassing the above settings:** Áp dụng cho cả Administrators.

---

## 5. Quy trình đóng góp chuẩn dành cho thành viên (Step-by-Step)

Mọi thành viên tuân thủ nghiêm ngặt 4 bước sau:

```bash
# Bước 1: Lấy code mới nhất từ dev về nhánh cá nhân
git fetch origin
git switch namng
git pull --ff-only origin namng
git merge origin/dev

# Bước 2: Viết mã, commit và push lên nhánh cá nhân
git add <các_file_thực_hiện>
git commit -m "feat(auth): thêm cơ chế kiểm tra token"
git push origin namng

# Bước 3: Mở PR trên giao diện GitHub
# CHỌN: base: dev  <---  compare: namng
# Đợi CI/CD quét kiểm tra chất lượng và an ninh mã nguồn.

# Bước 4: Sau khi Lead duyệt và merge PR vào dev:
# Lead sẽ là người mở PR từ dev vào main để đưa mã nguồn lên Production.
```
