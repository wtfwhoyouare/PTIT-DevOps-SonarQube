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
Trong pipeline `.github/workflows/sonarqube.yml`, hai tầng kiểm soát tự động được thực thi:
1. **Branch Policy Guard (`branch_policy_guard`):** Tự động kiểm tra nhánh nguồn và nhánh đích của mọi Pull Request.
   - Nếu phát hiện PR hướng vào `main` nhưng nhánh nguồn không phải là `dev`, pipeline sẽ **lập tức ném mã lỗi (exit 1)** kèm cảnh báo đỏ rực:
     > `❌ VI PHẠM CHÍNH SÁCH: Chỉ cho phép tạo Pull Request vào nhánh 'main' từ nhánh 'dev'. Nghiêm cấm tạo PR trực tiếp từ nhánh phát triển '<nhánh>' lên 'main'!`
   - Thao tác merge sẽ bị khóa lại trên GitHub.
2. **Production Readiness & Smoke Test Gate (`production_smoke_test`):** Dành riêng cho PR từ `dev` vào `main`.
   - **Docker Build Validation:** Tự động build sạch toàn bộ Dockerfile (Web & DB). Chặn đứng nếu build thất bại.
   - **Ephemeral Preview & Healthcheck:** Khởi chạy cụm container tạm thời trong runner, ping `/health` xác nhận HTTP 200 OK và kết nối Database sống, tải thử Trang chủ.
   - **Điều kiện nạp code vào `main`:** Chỉ khi CẢ HAI điều kiện (Build thành công + Healthcheck HTTP 200) đều PASS thì code mới được phép merge vào `main`.

### Tầng 2: Thiết lập Branch Protection Rules trên GitHub Repository
Admin repository kích hoạt cấu hình bảo vệ trên GitHub Web (**Settings → Branches / Rulesets**):
1. **Áp dụng cho nhánh `main` và `dev`:**
   - [x] **Require a pull request before merging:** Bắt buộc phải thông qua PR, chặn đứng hoàn toàn `git push origin main` hoặc `git push origin dev`.
   - [x] **Require approvals:** Yêu cầu tối thiểu 1 người phê duyệt trước khi merge.
   - [x] **Require status checks to pass before merging:** Bắt buộc các job `Verify Branch & PR Policy` và `Production Readiness & Smoke Test Gate` phải báo xanh (Success).
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

---

## 6. Quy tắc chuẩn hóa đặt tên Commit & Pull Request (Naming Conventions)

Để đảm bảo lịch sử Git rõ ràng, chuyên nghiệp và phục vụ tự động hóa kiểm soát CI/CD, toàn bộ thành viên bắt buộc tuân thủ quy ước đặt tên sau:

### 6.1. Quy tắc đặt tên Commit (Toàn bộ Repository)
Áp dụng tiêu chuẩn quốc tế **Conventional Commits**:
```text
<loại_thay_đổi>(<phạm_vi>): <mô tả ngắn bằng tiếng Việt hoặc tiếng Anh>
```
- **Các loại thay đổi (Types) hợp lệ:**
  - `feat`: Thêm tính năng mới (Feature)
  - `fix`: Sửa lỗi logic / chức năng (Bugfix)
  - `sec`: Vá lỗ hổng bảo mật / SAST
  - `ci`: Cấu hình Pipeline, GitHub Actions, Docker Compose
  - `docs`: Viết tài liệu hướng dẫn, báo cáo đồ án
  - `refactor`: Tái cấu trúc mã nguồn không làm thay đổi logic
  - `test`: Viết thêm unit tests, kịch bản kiểm thử
- **Ví dụ:**
  - `feat(db): tối ưu hóa kết nối mariadb và thêm route /health`
  - `fix(auth): khắc phục lỗi kiểm tra quyền hạn tài khoản`
  - `ci(docker): bổ sung cổng smoke test kiểm tra healthcheck`

### 6.2. Quy tắc đặt tên Pull Request (PR) theo 2 tầng riêng biệt

#### 🔹 Tầng 1: PR từ nhánh cá nhân vào `dev` (Tính năng & Đóng góp thành viên)
Mỗi PR từ nhánh thành viên vào `dev` đại diện cho một phần việc cá nhân được phân công, bắt buộc phải có định danh người thực hiện và loại công việc:
- **Cú pháp bắt buộc:**
  ```text
  [<mã_nhánh_cá_nhân>] <loại>(<phạm_vi>): <mô tả ngắn>
  ```
- **Danh sách mã nhánh hợp lệ:** `[namng]`, `[haind]`, `[manhdx]`, `[anhld]`, `[mainp]`.
- **Ví dụ thực tế:**
  - `[namng] feat(db): bổ sung endpoint healthcheck phục vụ docker preview`
  - `[manhdx] feat(auth): xây dựng trang đăng nhập và bảng tin thảo luận`
  - `[haind] fix(ui): sửa lỗi hiển thị header trên giao diện mobile`
  - `[mainp] feat(logistics): hoàn thiện api tra cứu vận đơn /api/track`
  - `[anhld] feat(admin): xây dựng bảng điều khiển quản trị và xuất báo cáo`

#### 🔹 Tầng 2: PR từ nhánh `dev` vào `main` (Phát hành chính thức lên Production)
Nhánh `main` đại diện cho sản phẩm thật chạy môi trường Production. Do đó, PR từ `dev` vào `main` mang tính chất của một **phiên bản phát hành (Release Milestone / SemVer)**:
- **Cú pháp bắt buộc:**
  ```text
  release: v<Major>.<Minor>.<Patch> - <Mô tả tổng quát phiên bản phát hành>
  ```
- **Quy tắc phiên bản Semantic Versioning (SemVer):**
  - **`v1.0.0`**: Bản phát hành chính thức đầu tiên (Production Launch).
  - **`v1.1.0`**: Cập nhật cụm tính năng mới lớn (Minor update).
  - **`v1.0.1`**: Bản vá lỗi khẩn cấp, vá lỗ hổng bảo mật (Patch/Hotfix).
- **Ví dụ thực tế:**
  - `release: v1.0.0 - Triển khai cổng thông tin Logistics InlaneWeb lên Production`
  - `release: v1.1.0 - Tích hợp hệ thống quản trị admin và kiểm thử tự động SAST`
  - `release: v1.1.1 - Vá lỗi bảo mật phân quyền tài khoản người dùng`

### 6.3. Cơ chế tự động kiểm tra trên GitHub Actions (Automated Title Validator)
Pipeline CI/CD tự động kích hoạt kiểm tra trong 2 tình huống:
1. **Khi User push code lên nhánh cá nhân:** Job `branch_policy_guard` chạy nhanh trong 3-5 giây để quét toàn bộ commit được đẩy lên. Nếu phát hiện commit sai chuẩn Conventional Commits, pipeline sẽ **lập tức báo FAIL đỏ rực**, in rõ commit vi phạm kèm hướng dẫn sửa lại bằng lệnh `git commit --amend` hoặc `git rebase`.
2. **Khi User tạo PR vào `dev`:** Kiểm tra tiêu đề PR theo mẫu `[tên_nhánh] loại(phạm_vi): mô tả`. Nếu sai, lập tức reject PR và hướng dẫn đổi tên trên giao diện GitHub.
3. **Khi Admin tạo PR vào `main`:** Kiểm tra tiêu đề PR theo mẫu `release: vX.Y.Z - <mô tả>`. Nếu sai, lập tức reject PR.

### 6.4. Kích hoạt Git Hook chặn lỗi ngay từ máy cá nhân (Khuyên dùng)
Để không bị đẩy nhầm commit sai format lên server, thành viên có thể kích hoạt Git Hook cục bộ có sẵn trong repository:
```bash
# Chạy 1 lệnh duy nhất tại thư mục gốc dự án:
git config core.hooksPath .githooks
```
Sau khi chạy lệnh trên, mỗi khi gõ `git commit`, hook `.githooks/commit-msg` sẽ tự động chạy trước. Nếu tiêu đề commit vi phạm quy tắc, lệnh commit sẽ **bị hủy bỏ ngay tại máy cá nhân** kèm thông báo lỗi hướng dẫn cụ thể!


