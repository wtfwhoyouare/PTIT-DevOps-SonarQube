# QUY CHUẨN PHÂN NHÁNH VÀ TRIỂN KHAI MÃ NGUỒN (GIT BRANCHING & DEPLOYMENT POLICY)
**HỆ THỐNG CỔNG THÔNG TIN VẬN TẢI INLANEWEB**

---

| Thuộc tính | Chi tiết |
| :--- | :--- |
| **Mã tài liệu:** | POL-DEVOPS-02 |
| **Dự án:** | InlaneWeb Logistics Portal |
| **Phân loại:** | Quy định kỹ thuật bắt buộc (Standard Operating Procedure - SOP) |
| **Phiên bản:** | 2.1.0 |
| **Ngày cập nhật:** | 23/10/2026 |
| **Trạng thái:** | Đã phê duyệt |

---

## 1. MỤC ĐÍCH VÀ PHẠM VI ÁP DỤNG

Quy chuẩn này quy định chi tiết cấu trúc phân nhánh mã nguồn, tiêu chuẩn thông điệp commit, quy trình tích hợp và các cơ chế kiểm soát kỹ thuật tự động (Automated Governance Gates).

Mục tiêu chính:
* Bảo vệ tính ổn định và an ninh của mã nguồn môi trường Production.
* Thực hiện nguyên lý kiểm thử an ninh sớm (Shift-Left Security) đối với mọi đóng góp mã nguồn.
* Đảm bảo tính nhất quán của lịch sử phát triển thông qua tiêu chuẩn Conventional Commits.
* Tự động hóa kiểm soát và phản hồi lỗi kỹ thuật qua hệ thống CI/CD.

---

## 2. NGUYÊN TẮC CỐT LÕI (INVIOLABLE RULES)

Mọi kỹ sư tham gia dự án phải tuân thủ nghiêm ngặt 3 nguyên tắc sau:
1. **Tuyệt đối không commit hoặc push trực tiếp** lên hai nhánh chính: `main` và `dev`.
2. **Mọi Pull Request của thành viên chỉ được hướng vào nhánh `dev`** với định dạng tiêu đề bắt buộc: `[<mã_nhánh>] <loại>(<phạm_vi>): <mô tả>`.
3. **Tuyệt đối cấm tạo Pull Request từ các nhánh cá nhân vào `main`.** Nhánh `main` chỉ nhận mã nguồn thông qua Pull Request xuất phát từ nhánh `dev` với định dạng phát hành: `release: vX.Y.Z - <mô tả>`.

---

## 3. CƠ CẤU PHÂN CẤP NHÁNH VÀ PHÂN QUYỀN (RACI MATRIX)

### 3.1. Sơ đồ luồng phân cấp nhánh

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

### 3.2. Ma trận quyền hạn trên các nhánh

| Tên nhánh | Phân loại | Mục đích sử dụng | Quyền Push trực tiếp | Nguồn tiếp nhận Pull Request |
| :--- | :--- | :--- | :---: | :--- |
| `main` | Production | Mã nguồn chính thức triển khai môi trường thực tế | Cấm | Duy nhất từ nhánh `dev` |
| `dev` | Integration | Tích hợp và kiểm thử hệ thống tổng thể | Cấm | Các nhánh cá nhân / tính năng |
| `namng`, `haind`, `manhdx`, `anhld`, `mainp` | Feature / Dev | Không gian làm việc độc lập của kỹ sư phát triển | Được phép | Nhận merge đồng bộ từ `origin/dev` |

---

## 4. QUY TRÌNH PHÁT TRIỂN CHUẨN HÓA (4 BƯỚC)

Kỹ sư phát triển thực hiện các bước sau cho mỗi hạng mục công việc:

### Bước 1: Đồng bộ mã nguồn mới nhất từ nhánh tích hợp
Trước khi viết mã mới, kỹ sư bắt buộc cập nhật nhánh cá nhân từ `origin/dev`:
```bash
git fetch origin
git switch <tên_nhánh_cá_nhân>
git pull --ff-only origin <tên_nhánh_cá_nhân>
git merge origin/dev
```

### Bước 2: Viết mã nguồn và tạo commit theo chuẩn
```bash
git add <danh_sách_tệp>
git commit -m "feat(auth): thêm cơ chế kiểm tra tính hợp lệ của token"
git push origin <tên_nhánh_cá_nhân>
```

### Bước 3: Khởi tạo Pull Request vào nhánh tích hợp (`dev`)
* Thiết lập trên GitHub: `base: dev` <--- `compare: <tên_nhánh_cá_nhân>`.
* Đặt tiêu đề theo đúng định dạng quy định: `[<tên_nhánh>] <loại>(<phạm_vi>): <mô tả>`.
* Hệ thống CI/CD sẽ tự động kích hoạt Stage 1 (Policy Guard) và Stage 2 (SAST Scanner).

### Bước 4: Đánh giá mã nguồn (Code Review) và Phát hành (Release)
* Sau khi toàn bộ các bài kiểm tra tự động đạt trạng thái thành công, Tech Lead tiến hành phê duyệt và merge vào `dev`.
* Khi hoàn thành một mốc phát hành (Milestone), Tech Lead khởi tạo Pull Request từ `dev` vào `main` theo cú pháp `release: vX.Y.Z - <mô tả>`. Pipeline kích hoạt Stage 3 để kiểm thử tải và sức khỏe dịch vụ trước khi hoàn tất triển khai.

---

## 5. TIÊU CHUẨN ĐỊNH DẠNG COMMIT VÀ PULL REQUEST

### 5.1. Tiêu chuẩn thông điệp Commit (Conventional Commits)

Áp dụng tiêu chuẩn quốc tế Conventional Commits trên toàn bộ kho mã nguồn:
```text
<loại_thay_đổi>(<phạm_vi>): <mô tả ngắn gọn>
```

#### Bảng danh mục loại thay đổi (Commit Types):

| Tiền tố (Type) | Mục đích kỹ thuật | Ví dụ thực tế |
| :--- | :--- | :--- |
| `feat` | Bổ sung tính năng mới | `feat(auth): thêm cơ chế đăng nhập và phân quyền người dùng` |
| `fix` | Khắc phục lỗi logic hoặc lỗi xử lý ngoại lệ | `fix(db): xử lý timeout khi kết nối cơ sở dữ liệu` |
| `sec` / `fix(sec)` | Khắc phục lỗ hổng an ninh mã nguồn | `sec(sqli): chuyển đổi câu truy vấn sang prepared statement` |
| `ci` | Cấu hình tự động hóa, pipeline, Docker | `ci(docker): bổ sung kịch bản kiểm tra sức khỏe container` |
| `docs` | Bổ sung hoặc chỉnh sửa tài liệu kỹ thuật | `docs(spec): cập nhật tài liệu kiến trúc hạ tầng giám sát` |
| `refactor` | Tái cấu trúc mã nguồn không thay đổi logic | `refactor(layout): tách giao diện phần đầu trang dùng chung` |
| `test` | Bổ sung hoặc cập nhật kịch bản kiểm thử | `test(ci): bổ sung kịch bản kiểm tra cú pháp cấu hình loki` |
| `perf` | Tối ưu hóa hiệu năng và tốc độ xử lý | `perf(query): bổ sung chỉ mục index cho bảng dữ liệu vận đơn` |
| `style` | Căn chỉnh định dạng mã nguồn (khoảng trắng, chuẩn PSR-12) | `style: định dạng thụt lề tệp index.php theo psr-12` |
| `chore` | Tác vụ phụ trợ, dọn dẹp tệp tạm | `chore: cập nhật danh sách loại trừ trong .gitignore` |

---

### 5.2. Tiêu chuẩn tiêu đề Pull Request 2 tầng (Two-Tier PR Naming)

#### Tầng 1: Đóng góp tính năng từ nhánh cá nhân vào `dev`
* **Cú pháp:** `[<mã_nhánh>] <loại>(<phạm_vi>): <mô tả>`
* **Danh sách mã nhánh hợp lệ:** `[namng]`, `[haind]`, `[manhdx]`, `[anhld]`, `[mainp]`.
* **Biểu thức chính quy (Regex):**
  ```regex
  ^\[(namng|haind|manhdx|anhld|mainp)\]\s+(feat|fix|sec|ci|docs|refactor|test|chore|style|perf|revert)(\([a-zA-Z0-9_\-\.\/]+\))?:\s.+
  ```
* **Ví dụ:**
  * `[namng] feat(db): bổ sung endpoint healthcheck phục vụ preview`
  * `[manhdx] feat(auth): xây dựng module xác thực người dùng`

#### Tầng 2: Phát hành chính thức từ `dev` vào `main`
* **Cú pháp:** `release: v<Major>.<Minor>.<Patch> - <Mô tả phiên bản>`
* **Biểu thức chính quy (Regex):**
  ```regex
  ^(release|RELEASE):\s+v[0-9]+\.[0-9]+\.[0-9]+(\s+-\s+.+|\s*:\s*.+)
  ```
* **Nguyên tắc định danh phiên bản (Semantic Versioning - SemVer):**
  * `vX.0.0` (Major): Thay đổi lớn phá vỡ tính tương thích ngược hoặc ra mắt hệ thống.
  * `v1.X.0` (Minor): Bổ sung nhóm tính năng mới nhưng đảm bảo tương thích ngược.
  * `v1.0.X` (Patch): Bản vá lỗi khẩn cấp hoặc vá lỗ hổng an ninh mạng.
* **Ví dụ:**
  * `release: v1.0.0 - Triển khai cổng thông tin Logistics InlaneWeb`
  * `release: v1.1.0 - Tích hợp phân hệ giám sát FOSS và kiểm thử SAST`

---

## 6. CƠ CHẾ KIỂM SOÁT TỰ ĐỘNG (TECHNICAL ENFORCEMENT)

Hệ thống bảo vệ chất lượng mã nguồn thông qua 3 tầng rào chắn kỹ thuật:

```text
 ┌──────────────────────────────────────────────────────────────────┐
 │                  MÔ HÌNH BẢO VỆ 3 TẦNG KỸ THUẬT                  │
 ├──────────────────────────────────────────────────────────────────┤
 │                                                                  │
 │  [TẦNG 1: KIỂM SOÁT CỤC BỘ PHÍA CLIENT - GIT HOOK]               │
 │   Chặn ngay tại máy trạm nếu thông điệp commit sai chuẩn         │
 │                                                                  │
 │            ▼ Khi push code hoặc mở Pull Request                  │
 │                                                                  │
 │  [TẦNG 2: KIỂM SOÁT TỰ ĐỘNG TRÊN CI/CD - GITHUB ACTIONS]        │
 │   Stage 1: Policy Guard (Commit format, Target branch, PR Title) │
 │   Stage 2: Shift-Left SAST (SonarQube & Semgrep Scan)            │
 │   Stage 3: Production Gate (Dual-Track CD & Smoke Test)          │
 │                                                                  │
 │            ▼ Khi đủ điều kiện merge                              │
 │                                                                  │
 │  [TẦNG 3: BẢO VỆ NHÁNH PHÍA SERVER - BRANCH PROTECTION RULES]    │
 │   Khóa nút Merge nếu thiếu review hoặc các stage CI chưa đạt     │
 │                                                                  │
 └──────────────────────────────────────────────────────────────────┘
```

### 6.1. Chi tiết 4 Stage trong GitHub Actions Pipeline

| Giai đoạn | Tên Job | Điều kiện kích hoạt | Nhiệm vụ chính | Tiêu chí đạt (Pass) | Biện pháp khi thất bại |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Stage 1: Policy Guard** | `Policy Guard - Branch, Commit & PR Validation` | Mọi sự kiện Push và mọi Pull Request (Thời gian: 3-5s) | - Quét toàn bộ commit trong payload đẩy lên.<br>- Ngăn chặn PR từ nhánh cá nhân vào `main`.<br>- Kiểm tra định dạng tiêu đề PR. | - 100% commit đúng chuẩn Conventional Commits.<br>- Nhánh `main` chỉ nhận head từ `dev`.<br>- Tiêu đề PR khớp 100% biểu thức regex. | Hủy bỏ tiến trình (Exit 1), xuất log cảnh báo kèm câu lệnh sửa lỗi chi tiết. |
| **Stage 2: Dev Gate** | `SonarQube SAST & Code Quality`<br><br>`Semgrep Security SAST` | PR hoặc Push trên nhánh `dev` | - Quét chất lượng mã, độ tin cậy và code smells với SonarQube Community.<br>- Quét chuyên sâu lỗ hổng an ninh Taint-Tracking với Semgrep.<br>- Kiểm tra cú pháp cấu hình giám sát bằng Python validator. | - Bài kiểm tra cú pháp đạt 21/21 test cases.<br>- Báo cáo SAST xuất thành công.<br>- Nhận tối thiểu 1 phê duyệt từ Tech Lead. | Hiển thị cảnh báo chất lượng trên PR; yêu cầu kỹ sư sửa lỗi trước khi được duyệt merge. |
| **Stage 3: Production Gate** | `Dual-Track CD & Smoke Test` | PR từ `dev` vào `main` hoặc Push trên `main` | - Phân tích thay đổi đường dẫn (Path-based selective execution).<br>- Kiểm tra build sạch Docker Web và cấu hình Monitoring.<br>- Khởi động môi trường kiểm thử tạm thời, xác nhận API `/health` đạt HTTP 200.<br>- Đảm bảo tính độc lập: Triển khai web không làm khởi động lại cụm giám sát. | - Docker build mã thoát 0.<br>- MariaDB đạt trạng thái healthy.<br>- API `/health` trả về HTTP 200.<br>- Cấu hình Monitoring hợp lệ. | Chặn hoàn toàn thao tác merge vào nhánh `main`. Không cho phép đưa mã nguồn lỗi lên Production. |
| **Stage 4: Production CD** | 1. `Deploy Observability Platform`<br><br>2. `Deploy Web Workload`<br>*(Phân tách 2 Job độc lập)* | Push/Merge chính thức vào nhánh `main` sau khi Stage 3 đạt | - **Job 1 (Monitoring):** Độc lập cập nhật cụm Loki/Promtail/Grafana/Autoheal khi có thay đổi cấu hình giám sát.<br>- **Job 2 (Web):** Độc lập rebuild và deploy Web container (`--no-deps --build web`), bảo toàn 100% uptime của cụm logging.<br>- **Hậu kiểm tra:** Ping endpoint `/health` trên host Production. | - Phân phát thành công lên máy chủ.<br>- Cụm logging duy trì 24/7.<br>- Endpoint `/health` trên host Production phản hồi HTTP 200. | Cảnh báo thất bại trên Actions, kích hoạt quy trình rollback của quản trị viên. |

---

### 6.2. Cấu hình bảo vệ nhánh phía Server (Branch Protection Rules)

Áp dụng trên cả hai nhánh `main` và `dev` qua giao diện quản trị GitHub:
1. **Require a pull request before merging:** Bắt buộc mọi thay đổi phải thông qua PR. Chặn thao tác `git push origin main` hoặc `git push origin dev`.
2. **Require approvals:** Yêu cầu tối thiểu 1 phê duyệt từ kỹ sư phụ trách trước khi hoàn tất merge.
3. **Require status checks to pass before merging:** Bắt buộc các job `Policy Guard` và `Production Gate` phải đạt trạng thái thành công.
4. **Do not allow bypassing the above settings:** Áp dụng ràng buộc bình đẳng cho toàn bộ tài khoản, bao gồm cả quyền Quản trị viên (Admin).

---

### 6.3. Kích hoạt kiểm soát cục bộ bằng Git Hook (Khuyến nghị áp dụng)

Nhằm giảm thiểu việc commit sai cú pháp và bị hệ thống CI/CD từ chối sau khi push, kỹ sư kích hoạt bộ lọc kiểm tra cục bộ được cấu hình sẵn trong repository bằng một câu lệnh:

```bash
git config core.hooksPath .githooks
```

*Nguyên lý hoạt động:* Tệp script `.githooks/commit-msg` sẽ tự động chặn thao tác tạo commit nếu tiêu đề vi phạm quy chuẩn Conventional Commits, đồng thời hướng dẫn sửa đổi cú pháp ngay tại terminal của máy trạm.

---

## 7. BẢNG TRA CỨU VÀ KHẮC PHỤC VI PHẠM THƯỜNG GẶP

| Tình huống vi phạm | Nguyên nhân | Hướng dẫn xử lý |
| :--- | :--- | :--- |
| **Commit sai cú pháp** | Tiêu đề commit không chứa tiền tố quy chuẩn (ví dụ: `update code`). | Sửa commit gần nhất bằng lệnh:<br>`git commit --amend -m "feat(phạm_vi): mô_tả_chuẩn"`<br>Sau đó cập nhật lên remote:<br>`git push --force origin <tên_nhánh>` |
| **Tiêu đề PR vào `dev` bị từ chối** | Thiếu mã định danh thành viên hoặc sai cú pháp (ví dụ: `fix login error`). | Nhấn nút **Edit** cạnh tiêu đề PR trên giao diện GitHub, đổi thành:<br>`[<mã_nhánh>] fix(auth): mô tả sự cố`<br>Sau khi lưu, pipeline sẽ tự động chạy lại. |
| **PR vào `main` bị chặn đứng** | Mở PR từ nhánh cá nhân thay vì từ nhánh `dev`. | Đóng Pull Request hiện tại. Mở Pull Request hướng vào nhánh `dev` để thực hiện kiểm thử tích hợp trước. |
| **Tiêu đề PR phát hành bị từ chối** | Không tuân theo định dạng SemVer khi merge vào `main`. | Nhấn nút **Edit** cạnh tiêu đề PR trên GitHub, điều chỉnh thành:<br>`release: vX.Y.Z - Mô tả phiên bản phát hành` |
