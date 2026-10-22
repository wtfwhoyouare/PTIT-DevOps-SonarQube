# CHÍNH SÁCH PHÂN NHÁNH VÀ TRIỂN KHAI MÃ NGUỒN (GIT BRANCHING & DEPLOYMENT POLICY)

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

### Tầng 1: Tự động chặn bằng GitHub Actions CI/CD Pipeline (Phân tách 3 Stage độc lập)

Trong pipeline `.github/workflows/sonarqube.yml`, quy trình kiểm soát được phân tách thành **3 Giai đoạn (Stages)** riêng biệt theo mô hình DAG (Directed Acyclic Graph) tuần tự, không gộp chung khối gây hiểu nhầm:

```text
  ┌────────────────────────────────────────────────────────┐
  │ [STAGE 1] Policy Guard — Kiểm tra Nhánh, Commit & PR   │  (Chạy nhanh 3-5s cho mọi Push & PR)
  └───────────────────────────┬────────────────────────────┘
                              │
          ┌───────────────────┴───────────────────┐
          ▼ (Khi PR hoặc Merge vào DEV)           ▼ (Khi PR hoặc Merge vào MAIN)
  ┌────────────────────────────────────────┐      │
  │ [STAGE 2: Dev Gate] Shift-Left SAST    │      │
  │  ├── SonarQube SAST & Code Quality     │      │
  │  └── Semgrep Security SAST (Taint Data)│      │
  └───────────────────┬────────────────────┘      │
                      │                           │
                      ▼ (Sau khi hoàn tất Stage 2)▼
  ┌────────────────────────────────────────────────────────┐
  │ [STAGE 3: Production Gate] Docker Build & Smoke Test   │  (Chỉ mở cổng kiểm thử trước khi nạp vào MAIN)
  │  ├── Build sạch toàn bộ Docker Images                  │
  │  ├── Khởi chạy Preview trong Runner (Docker Compose)   │
  │  ├── Healthcheck MariaDB đạt trạng thái healthy       │
  │  └── Gọi API /health (HTTP 200) & Smoke Test Trang chủ │
  └────────────────────────────────────────────────────────┘
```

#### 📋 Bảng tổng hợp các Stage trong Pipeline:

| Giai đoạn | Job GitHub Actions | Điều kiện chạy | Nhiệm vụ chính | Tiêu chuẩn PASS | Xử lý khi FAIL |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **STAGE 1: Policy Guard** | `[STAGE 1] Policy Guard — Kiểm tra Nhánh, Commit & PR` | **Mọi sự kiện Push** lên nhánh cá nhân & **Mọi PR** vào `dev`/`main` *(3-5s)* | 1. **Kiểm tra Commit:** Quét toàn bộ commit trong payload đẩy lên, đối chiếu chuẩn Conventional Commits.<br>2. **Bảo vệ nhánh Main:** Ngăn chặn ngay lập tức nếu ai đó mở PR từ nhánh cá nhân vào `main`.<br>3. **Kiểm tra tiêu đề PR:** Xác thực cú pháp PR vào `dev` (`[<nhánh>] ...`) và PR vào `main` (`release: vX.Y.Z ...`). | - **100% commit** khớp regex Conventional Commits.<br>- Nhánh đích `main` chỉ nhận head từ `dev`.<br>- Tiêu đề PR khớp 100% regex theo tầng tương ứng. | ❌ **FAIL ngay lập tức (Exit 1)**.<br>Khóa lệnh commit/PR, in hộp hướng dẫn kèm câu lệnh sửa lỗi (`git commit --amend` hoặc đổi tên PR). |
| **STAGE 2: Dev Gate** | `[STAGE 2: Dev Gate] SonarQube SAST & Code Quality`<br><br>`[STAGE 2: Dev Gate] Semgrep Security SAST` | **Chỉ kích hoạt khi:**<br>- Tạo Pull Request vào `dev`<br>- Merge/Push chính thức trên `dev` | 1. **SonarQube SAST:** Khởi tạo container SonarQube phân tích độ tin cậy, nợ kỹ thuật (Technical Debt), Code Smells, Bugs và tính chuẩn mực PSR-12 của PHP 8.2.<br>2. **Semgrep SAST:** Quét chuyên sâu bảo mật theo luồng dữ liệu Taint-Tracking (Source -> Sink), dò tìm các lỗ hổng Injection (SQLi, XSS), cấu hình sai bảo mật.<br>3. **Báo cáo:** Xuất Step Summary trực quan và đính kèm Artifacts báo cáo PDF/HTML/JSON. | - **Unit test CI:** 20/20 test cases chạy PASS (`exit 0`).<br>- **PHP Lint:** Cú pháp PHP 8.2 không có lỗi Fatal/Syntax.<br>- **Báo cáo SAST:** Quét hoàn tất, không phát hiện lỗi crash hệ thống, báo cáo được đính kèm vào Step Summary.<br>- **Reviewer duyệt:** Đạt tối thiểu 1 Approval từ Tech Lead sau khi đánh giá các phát hiện bảo mật. | ⚠️ **Cảnh báo chất lượng** trên giao diện PR.<br>Lead/Reviewer dựa vào kết quả kiểm tra để yêu cầu dev vá lỗ hổng trước khi phê duyệt merge vào nhánh `dev`. |
| **STAGE 3: Production Gate** | `[STAGE 3: Production Gate] Docker Build & Smoke Test Healthcheck` | **Chỉ kích hoạt khi:**<br>- Tạo Pull Request từ `dev` vào `main`<br>- Merge/Push chính thức trên `main` | 1. **Docker Build Validation:** Tự động build sạch toàn bộ Dockerfile (Apache PHP 8.2 & MariaDB). Đảm bảo mã nguồn đóng gói thành container thành công 100%.<br>2. **Ephemeral Deployment:** Bung cụm container chạy thử nghiệm thật ngay trong GitHub Runner bằng `docker compose up -d`.<br>3. **Database Healthcheck:** Vòng lặp ping kiểm tra container `ilfreight_db` đạt trạng thái `healthy` (schema và dữ liệu khởi tạo xong).<br>4. **API Healthcheck:** Gọi `GET /health`, bắt buộc phản hồi HTTP 200 OK và xác nhận Database kết nối thông suốt.<br>5. **E2E Smoke Test:** Tải thử Trang chủ (`/`), kiểm tra nạp đủ nội dung thương hiệu IlFreight.<br>6. **Teardown:** Tự động dọn dẹp sạch sẽ cụm container trong runner sau khi kiểm thử xong. | - **Docker Build:** Mã thoát `exit 0`, không thiếu file/package.<br>- **MariaDB Status:** Báo `healthy` trong vòng tối đa 90 giây.<br>- **API /health:** Trả về HTTP Code đúng `200` và JSON `status: UP, database: connected`.<br>- **Smoke Test:** Trang chủ nạp thành công HTTP 200 và chứa nội dung `IlFreight`. | ⛔ **CHẶN ĐỨNG MERGE VÀO MAIN**.<br>Nếu Docker build gãy hoặc `/health` không trả về 200, PR lập tức bị khóa, không cho phép nạp mã nguồn lỗi lên môi trường Production! |

### Tầng 2: Thiết lập Branch Protection Rules trên GitHub Repository
Admin repository kích hoạt cấu hình bảo vệ trên GitHub Web (**Settings → Branches / Rulesets**):
1. **Áp dụng cho nhánh `main` và `dev`:**
   - [x] **Require a pull request before merging:** Bắt buộc phải thông qua PR, chặn đứng hoàn toàn `git push origin main` hoặc `git push origin dev`.
   - [x] **Require approvals:** Yêu cầu tối thiểu 1 người phê duyệt trước khi merge.
   - [x] **Require status checks to pass before merging:** Bắt buộc các job `[STAGE 1] Policy Guard` và `[STAGE 3: Production Gate]` phải báo xanh (Success).
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

Để đảm bảo lịch sử Git trong sạch, chuyên nghiệp theo tiêu chuẩn công nghiệp và phục vụ tự động hóa kiểm soát CI/CD, toàn bộ thành viên bắt buộc tuân thủ quy ước đặt tên sau:

### 6.1. Quy tắc đặt tên Commit (Toàn bộ Repository)

Áp dụng tiêu chuẩn quốc tế **Conventional Commits**:
```text
<loại_thay_đổi>(<phạm_vi>): <mô tả ngắn bằng tiếng Việt hoặc tiếng Anh>
```

#### 📋 Bảng tra cứu các tiền tố (Types) bắt buộc:

| Tiền tố (Type) | Ý nghĩa nghiệp vụ | Ví dụ thực tế trong dự án |
| :--- | :--- | :--- |
| `feat` | Thêm tính năng mới (Feature) | `feat(auth): thêm cơ chế đăng nhập và phân quyền người dùng` |
| `fix` | Sửa lỗi chức năng (Bugfix / Hotfix) | `fix(db): xử lý timeout và fallback mật khẩu khi kết nối mariadb` |
| `sec` / `fix(sec)` | Vá lỗ hổng bảo mật SAST (SQLi, XSS, etc.) | `sec(sqli): chuyển đổi câu lệnh sang prepared statement` |
| `ci` | Cấu hình Pipeline, GitHub Actions, Docker | `ci(docker): thêm healthcheck và smoke test preview` |
| `docs` | Viết tài liệu (README, Docs, Báo cáo đồ án) | `docs(policy): quy định quy tắc phân nhánh và đặt tên commit/PR` |
| `refactor` | Tối ưu, cơ cấu lại code không đổi logic | `refactor(layout): gom nhóm css và tách header dùng chung` |
| `test` | Viết thêm unit tests hoặc kịch bản kiểm thử | `test(ci): bổ sung test case cho parser báo cáo sonarqube` |
| `perf` | Tối ưu hóa hiệu năng thực thi (Performance) | `perf(query): thêm chỉ mục index cho bảng tra cứu vận đơn` |
| `style` | Định dạng mã nguồn (khoảng trắng, dấu ngoặc) | `style: định dạng lại thụt lề file index.php theo chuẩn PSR-12` |
| `chore` | Tác vụ bảo trì linh tinh, dọn dẹp phụ trợ | `chore: dọn dẹp các tệp tạm và cập nhật danh sách .gitignore` |

> 💡 **Quy tắc về Phạm vi (`scope`):** Đặt trong ngoặc đơn ngay sau Type, mô tả phân hệ bị ảnh hưởng: `auth`, `db`, `ports`, `logistics`, `admin`, `docker`, `policy`, `layout`.  
> 💡 **Quy tắc về Mô tả (`subject`):** Viết ngắn gọn súc tích, không kết thúc bằng dấu chấm câu.

---

### 6.2. Quy tắc đặt tên Pull Request (PR) theo 2 tầng riêng biệt

Quy trình đóng góp phân biệt rõ ràng giữa hai tầng: **Tầng phát triển cá nhân** và **Tầng phát hành hệ thống**. Do đó, tiêu đề PR bắt buộc tuân theo 2 mẫu khác nhau:

#### 🔹 Tầng 1: PR từ nhánh cá nhân vào `dev` (Tính năng & Đóng góp thành viên)
Mỗi PR từ nhánh thành viên vào `dev` đại diện cho một phần việc cá nhân được phân công, bắt buộc phải có định danh người thực hiện và loại công việc:

- **Cú pháp bắt buộc:**
  ```text
  [<mã_nhánh_cá_nhân>] <loại>(<phạm_vi>): <mô tả ngắn gọn>
  ```
- **Danh sách mã nhánh cá nhân hợp lệ:** `[namng]`, `[haind]`, `[manhdx]`, `[anhld]`, `[mainp]`.
- **Biểu thức chính quy (Regex) kiểm tra:**
  ```regex
  ^\[(namng|haind|manhdx|anhld|mainp)\]\s+(feat|fix|sec|ci|docs|refactor|test|chore|style|perf|revert)(\([a-zA-Z0-9_\-\.\/]+\))?:\s.+
  ```
- **Ví dụ thực tế theo từng thành viên:**
  - `[namng] feat(db): bổ sung endpoint healthcheck phục vụ docker preview`
  - `[manhdx] feat(auth): xây dựng trang đăng nhập và bảng tin thảo luận`
  - `[haind] fix(ui): sửa lỗi hiển thị header trên giao diện mobile`
  - `[mainp] feat(logistics): hoàn thiện api tra cứu vận đơn /api/track`
  - `[anhld] feat(admin): xây dựng bảng điều khiển quản trị và xuất báo cáo`

#### 🔹 Tầng 2: PR từ nhánh `dev` vào `main` (Phát hành chính thức lên Production)
Nhánh `main` đại diện cho sản phẩm thật chạy môi trường Production. Do đó, PR từ `dev` vào `main` mang tính chất của một **phiên bản phát hành (Release Milestone / SemVer)**, không gắn tên cá nhân:

- **Cú pháp bắt buộc:**
  ```text
  release: v<Major>.<Minor>.<Patch> - <Mô tả tổng quát phiên bản phát hành>
  ```
  *(Chấp nhận tiền tố `release:` hoặc `RELEASE:`)*
- **Biểu thức chính quy (Regex) kiểm tra:**
  ```regex
  ^(release|RELEASE):\s+v[0-9]+\.[0-9]+\.[0-9]+(\s+-\s+.+|\s*:\s*.+)
  ```
- **Quy tắc tăng số phiên bản Semantic Versioning (SemVer):**
  - **`vX.0.0` (Major):** Phát hành phiên bản chính thức ban đầu hoặc có thay đổi lớn phá vỡ tính tương thích ngược.
  - **`v1.X.0` (Minor):** Bổ sung cụm tính năng mới lớn tích hợp từ các thành viên.
  - **`v1.0.X` (Patch):** Bản vá lỗi khẩn cấp, vá lỗ hổng an ninh mạng (Hotfix).
- **Ví dụ thực tế:**
  - `release: v1.0.0 - Triển khai cổng thông tin Logistics InlaneWeb lên Production`
  - `release: v1.1.0 - Tích hợp hệ thống quản trị admin và kiểm thử tự động SAST`
  - `release: v1.1.1 - Vá lỗ hổng SQL Injection và phân quyền tài khoản`

---

### 6.3. Sơ đồ cơ chế phòng thủ 2 tầng (Two-Tier Title Guard Architecture)

Để đảm bảo không một commit hoặc Pull Request sai định dạng nào có thể lọt vào lịch sử dự án, hệ thống thiết lập cơ chế **phòng thủ 2 tầng (Defense-in-Depth)**:

```text
               [ THAO TÁC CỦA DEV ]
                        │
                        ▼
            gõ `git commit -m "..."`
                        │
                        ▼
          ┌───────────────────────────┐
          │  TẦNG 1: LOCAL GIT HOOK   │
          │   (.githooks/commit-msg)  │
          └─────────────┬─────────────┘
                        │
             Đúng chuẩn Conventional?
             ├── ❌ KHÔNG ───> [HỦY BỎ NGAY TẠI MÁY] (Không tạo commit)
             │                 (In hướng dẫn sửa cú pháp)
             │
             └── ✅ ĐÚNG (hoặc cố tình vượt rào bằng `git commit --no-verify`)
                        │
                        ▼
                 Tạo commit cục bộ
                        │
                        ▼
             gõ `git push origin <nhánh>`
                        │
                        ▼
         ┌─────────────────────────────┐
         │  TẦNG 2: GITHUB ACTIONS CI  │
         │     (branch_policy_guard)   │
         └──────────────┬──────────────┘
                        │
                        ├── Khi PUSH code: Quét toàn bộ commit trong payload
                        │   ├── ❌ Sai chuẩn ──> [FAIL PIPELINE (Exit 1)] (Báo đỏ rực)
                        │   └── ✅ Đúng chuẩn ─> PASS kiểm tra
                        │
                        └── Khi MỞ PULL REQUEST:
                            ├── PR vào `dev`: Bắt buộc `[<nhánh>] <type>(<scope>): <mô tả>`
                            │   ├── ❌ Sai chuẩn ──> [FAIL PIPELINE] (Khóa merge PR)
                            │   └── ✅ Đúng chuẩn ─> Kích hoạt SAST Scanner (SonarQube/Semgrep)
                            │
                            └── PR vào `main`: Bắt buộc `release: vX.Y.Z - <mô tả>` & Head là `dev`
                                ├── ❌ Sai chuẩn ──> [FAIL PIPELINE] (Khóa nạp vào Production)
                                └── ✅ Đúng chuẩn ─> Kích hoạt Production Smoke Test Gate
```

---

### 6.4. Các kịch bản từ chối tự động & Mẫu thông báo lỗi (Automated CI/CD Feedback)

Job `branch_policy_guard` trong pipeline GitHub Actions tự động kiểm tra nghiêm ngặt trong mọi tình huống. Nếu vi phạm, pipeline sẽ **lập tức REJECT (exit 1)** và hiển thị hộp thông báo kèm helper hướng dẫn chi tiết:

#### ❌ Case A: Khi User push commit sai format lên nhánh cá nhân
```text
======================================================================
❌ LỖI VI PHẠM CHÍNH SÁCH ĐẶT TÊN COMMIT (CONVENTIONAL COMMITS)
======================================================================
🚫 Commit [def7890]: "update code"
👉 Lý do: Tiêu đề commit 'update code' vi phạm chuẩn Conventional Commits.
Cú pháp bắt buộc: <loại>(<phạm_vi>): <mô tả>
Các loại (types) hợp lệ: feat, fix, sec, ci, docs, refactor, test, chore, style, perf.
Ví dụ chuẩn: feat(auth): thêm chức năng xác thực token JWT
             fix(db): khắc phục timeout khi truy vấn mariadb
             ci(docker): bổ sung cổng smoke test kiểm tra healthcheck

----------------------------------------------------------------------
🛠️ HƯỚNG DẪN KHẮC PHỤC NHANH TRÊN MÁY CỦA BẠN:
1. Nếu commit vi phạm là commit gần nhất:
   git commit --amend -m "feat(<phạm_vi>): <mô tả lại cho đúng>"
   git push --force origin <tên_nhánh_của_bạn>
2. Nếu có nhiều commit vi phạm:
   git rebase -i HEAD~<số_lượng_commit>
   Đổi chữ 'pick' thành 'reword' ở các commit sai, sửa lại tên rồi push --force.
======================================================================
```

#### ❌ Case B: Khi User tạo PR vào `dev` sai format tiêu đề
```text
======================================================================
❌ SAI QUY ƯỚC ĐẶT TÊN PULL REQUEST VÀO NHÁNH DEV
======================================================================
Tiêu đề PR "feat(db): missing username prefix" không đúng quy ước đóng góp vào nhánh 'dev'.
Cú pháp bắt buộc: [<mã_nhánh>] <loại>(<phạm_vi>): <mô tả>
Các mã nhánh hợp lệ: [namng], [haind], [manhdx], [anhld], [mainp]
Các loại hợp lệ: feat, fix, sec, ci, docs, refactor, test, chore, style, perf
Ví dụ chuẩn: [namng] feat(db): bổ sung endpoint healthcheck phục vụ preview
----------------------------------------------------------------------
🛠️ CÁCH SỬA NHANH TRÊN GIAO DIỆN GITHUB:
1. Tại trang Pull Request này trên GitHub, bấm nút 'Edit' ở cạnh tiêu đề.
2. Đổi lại tiêu đề theo đúng mẫu: [tên_nhánh] loại(phạm_vi): mô tả
3. Nhấn 'Save'. Pipeline sẽ tự động kiểm tra lại và bật xanh!
======================================================================
```

#### ❌ Case C: Khi Admin tạo PR vào `main` sai format phiên bản
```text
======================================================================
❌ SAI QUY ƯỚC ĐẶT TÊN PULL REQUEST RELEASE VÀO NHÁNH MAIN
======================================================================
Tiêu đề PR "merge dev to main" không đúng chuẩn Release SemVer vào nhánh 'main'.
Cú pháp bắt buộc: release: v<Major>.<Minor>.<Patch> - <Mô tả phiên bản>
Ví dụ chuẩn: release: v1.0.0 - Triển khai cổng thông tin InlaneWeb lên Production
----------------------------------------------------------------------
🛠️ CÁCH SỬA NHANH TRÊN GIAO DIỆN GITHUB:
1. Bấm nút 'Edit' cạnh tiêu đề PR trên GitHub.
2. Đổi tiêu đề thành: release: vX.Y.Z - <Mô tả phiên bản phát hành>
3. Bấm 'Save' để kích hoạt lại kiểm tra.
======================================================================
```

#### ❌ Case D: Khi có người cố tình mở PR vào `main` từ nhánh cá nhân
```text
======================================================================
⛔ VI PHẠM CHÍNH SÁCH BẢO VỆ NHÁNH MAIN
======================================================================
Chỉ cho phép tạo Pull Request vào nhánh 'main' xuất phát từ nhánh 'dev'.
Nghiêm cấm tạo PR trực tiếp từ nhánh phát triển 'namng' lên 'main'!
----------------------------------------------------------------------
🛠️ HƯỚNG DẪN: Hãy đóng PR này và mở PR mới hướng vào nhánh 'dev' trước.
======================================================================
```

---

### 6.5. Kích hoạt Git Hook chặn lỗi ngay từ máy cá nhân (Khuyên dùng)

Để bảo vệ lịch sử commit và không bị pipeline server từ chối sau khi push, mỗi thành viên được khuyến nghị kích hoạt hook kiểm tra cục bộ có sẵn trong repository:

```bash
# Chạy duy nhất 1 lệnh tại thư mục gốc dự án:
git config core.hooksPath .githooks
```

- **Nguyên lý hoạt động:** Hook `.githooks/commit-msg` sẽ tự động kích hoạt mỗi khi gõ lệnh `git commit`. 
- Nếu tiêu đề commit vi phạm quy tắc Conventional Commits, tiến trình commit sẽ **lập tức bị hủy bỏ ngay trên máy của bạn**, yêu cầu đặt lại tên đúng chuẩn trước khi tệp được ghi vào lịch sử Git!




