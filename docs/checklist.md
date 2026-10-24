# CHECKLIST ĐÁNH GIÁ & HOÀN THIỆN BÁO CÁO CUỐI KỲ DEVSECOPS
> **Căn cứ yêu cầu:** Đề bài "Báo cáo bài tập nhóm đánh giá cuối kỳ" môn DevSecOps (Hạn nộp: 31/10/2026).  
> **Tài liệu hoàn thiện:** [`docs/05-Báo cáo bài tập lớn DevSecOps.md`](file:///d:/PTIT-DevOps-SonarQube/docs/05-Báo%20cáo%20bài%20tập%20lớn%20DevSecOps.md)  
> **Kho mã nguồn & minh chứng:** [`https://github.com/wtfwhoyouare/PTIT-DevOps-SonarQube`](https://github.com/wtfwhoyouare/PTIT-DevOps-SonarQube)

---

## PHẦN 1: BẢNG ĐỐI CHIẾU NHANH VỚI YÊU CẦU CỦA GIẢNG VIÊN

| STT | Yêu cầu của Giảng viên theo Đề bài | Trạng thái hiện tại | Đánh giá so với kỳ vọng | Ghi chú hành động cần làm |
| :---: | :--- | :---: | :---: | :--- |
| **1** | **Mô tả ứng dụng & tối thiểu 2 nghiệp vụ liên quan an toàn** | ✅ ĐÃ ĐẠT | Chuẩn mực | Đã có InlaneWeb Logistics; cần bổ sung thêm Sơ đồ CSDL (ERD) cho rõ luồng dữ liệu. |
| **2** | **Mô tả môi trường triển khai (yêu cầu an toàn tối thiểu)** | 🌟 VƯỢT KỲ VỌNG | Vượt xa | Triển khai thực tế trên Cloud VPS, có SSL Full Strict, NPM Reverse Proxy kép, Docker isolation. |
| **3** | **Mỗi thành viên chỉ ra 1 vấn đề an toàn (5 thành viên = 5 vấn đề):**<br>- Cách phát hiện & xử lý<br>- **Vi phạm chính sách: Nghị định 13/2023 hoặc GDPR**<br>- Nêu rõ pha trong quy trình DevSecOps<br>- Thể hiện Policy-as-Code hoặc Security-as-Code<br>- Có tối thiểu 2 nhóm lỗi: Code và Triển khai/Vận hành | ✅ **ĐÃ HOÀN THÀNH** | **Chuẩn mực 100%** | Đã hoàn thiện toàn diện tại **Mục 5.1 Báo cáo 05**: phân bổ 5 thành viên, 5 pha DevSecOps, viện dẫn chi tiết điều luật NĐ 13/2023 và GDPR kèm mã demo thực tế. |
| **4** | **Mỗi thành viên demo đoạn code phát hiện / khắc phục / cảnh báo** | ✅ ĐÃ ĐẠT | Chuẩn mực | Đã có code Policy Guard, Semgrep rules, SonarQube, PDO prepared statement, LogQL, Autoheal. |
| **5** | **Ghi tên trưởng nhóm, mã học viên, dài không quá 30 trang, < 10MB** | ✅ **ĐÃ HOÀN TẤT** | **Chuẩn mực 100%** | Đã ghi rõ Trưởng nhóm Nguyễn Giang Nam, vị trí Mã học viên cho cả 5 bạn; báo cáo đã được cô đọng bảng biểu và sơ đồ logic để sẵn sàng xuất bản PDF ≤ 30 trang. |
| **6** | **Nộp báo cáo trước ngày 31/10/2026** | ⏳ TRONG KẾ HOẠCH | Chủ động | Hệ thống đã chạy thực tế trên VPS; hoàn thiện báo cáo trước 26/10. |
| **7** | **Tham khảo tài liệu trong đường dẫn môn học** | ✅ ĐÃ ĐẠT | Chuẩn mực | Đã có danh mục tài liệu tham khảo chuẩn IEEE/NIST/OWASP/CWE. |

---

## PHẦN 2: PHÂN TÍCH CHI TIẾT THEO 3 TRẠNG THÁI

### 🌟 A. NHỮNG GÌ HỆ THỐNG ĐÃ LÀM TỐT HƠN (VƯỢT NGOÀI KỲ VỌNG CỦA ĐỀ BÀI)
*Đa số các nhóm sinh viên chỉ dựng lab cục bộ (localhost) hoặc chạy script thủ công. Đề tài này đã hiện thực hóa một hệ thống tiêu chuẩn kỹ thuật tiệm cận môi trường doanh nghiệp:*

1. **Triển khai Production thực tế trên Cloud VPS với 2 tên miền độc lập có SSL/TLS thật:**
   - Ứng dụng vận tải: `https://inlaneweb.ecotools.online`
   - Bảng điều khiển an ninh: `https://grafana.ecotools.online`
   - Điều phối qua Reverse Proxy kép Nginx Proxy Manager, mã hóa cấp cao qua Cloudflare SSL Full Strict và chứng chỉ Let's Encrypt với cờ HSTS.
2. **Quy trình DevSecOps 4 Stage tự động hóa hoàn chỉnh và khép kín:**
   - `Stage 1`: Policy Guard kiểm soát nhánh, chuẩn hóa Conventional Commits.
   - `Stage 2`: Phân tích an ninh đa tầng với Semgrep Taint Analysis & SonarQube Quality Gate Rating A.
   - `Stage 3`: Môi trường kiểm thử tạm thời (Ephemeral Preview Stack) chạy trực tiếp trong GitHub Runner, thực thi E2E Smoke Test và đẩy ảnh Docker bất biến lên GitHub Container Registry (GHCR).
   - `Stage 4`: Triển khai tự động từ xa qua kết nối an toàn SSH Ed25519.
3. **Kiến trúc tách rời độc lập (Decoupled Zero-Downtime) & Stage 4 chạy song song:**
   - Khối ứng dụng nghiệp vụ (`inlaneweb-prod`) và Khối hạ tầng giám sát (`inlaneweb-monitoring`) có vòng đời độc lập, chỉ chia sẻ Docker Network nội bộ.
   - Stage 4 được thiết kế theo mô hình đồ thị có hướng song song (Parallel DAG Execution): vừa deploy Web vừa deploy cụm Giám sát đồng thời, rút ngắn 50% thời gian triển khai.
4. **Cơ chế tự phục hồi dịch vụ (Self-Healing / Autoheal):**
   - Tích hợp container Autoheal tự động giám sát nhịp tim `/health`. Nếu container Web rơi vào trạng thái `unhealthy` quá 90 giây, Autoheal tự động restart container trong 5 giây mà không cần kỹ sư can thiệp thủ công.
5. **Hệ thống giám sát an ninh tập trung 8 phân vùng chuyên sâu với LogQL thời gian thực:**
   - Tách biệt hai luồng nhật ký (Dual-Stream Logging): Log chẩn đoán ứng dụng PHP vs Log lưu lượng HTTP JSON của Apache.
   - Dashboard Grafana trực quan hóa 8 phân vùng giám sát phát hiện ngay lập tức các cuộc tấn công SQLi, XSS, Path Traversal/LFI, RCE/CMDi, lỗi 5xx và chẩn đoán MariaDB.
6. **Hồ sơ thực nghiệm và phân tích sâu 14 vector tấn công SQL Injection:**
   - Nghiên cứu thực nghiệm đầy đủ 14 kỹ thuật khai thác thực tế: từ Error-based (XPath extractvalue, updatexml), UNION-based, Blind (Boolean, Time delay), Out-of-band cho đến RCE ghi tệp webshell.
7. **Cơ chế nhận diện thông minh bỏ qua triển khai khi chỉ cập nhật tài liệu:**
   - Tự động phát hiện phạm vi thay đổi: nếu commit chỉ chỉnh sửa `docs/**`, `*.md`, `*.docx`, pipeline tự động bỏ qua Stage 3 và Stage 4, tiết kiệm 100% tài nguyên máy ảo.

---

### ✅ B. NHỮNG GÌ HỆ THỐNG ĐÃ ĐẠT CHUẨN ĐÚNG THEO ĐỀ BÀI
1. **Mô tả ứng dụng và 2 nghiệp vụ liên quan an toàn:**
   - Ứng dụng web InlaneWeb Logistics với các nghiệp vụ: Tra cứu vận đơn (Tracking), Tra cứu cảng biển (Ports), Xác thực đăng nhập quản trị viên, Gửi phản hồi/bình luận đơn hàng.
2. **Mô tả môi trường triển khai đáp ứng an toàn tối thiểu:**
   - Máy chủ VPS Ubuntu 24.04 LTS.
   - Cổng cơ sở dữ liệu `3306` được đóng kín hoàn toàn trong mạng nội bộ `inlaneweb_net`, không mở ra Internet.
   - Dữ liệu MariaDB được bảo vệ an toàn trên Docker Named Volume `db_data`.
3. **Áp dụng đầy đủ triết lý Policy-as-Code và Security-as-Code:**
   - Policy-as-Code: `ci/policy_guard.py` cưỡng chế quy chuẩn đóng góp mã nguồn.
   - Security-as-Code: `ci/semgrep-local-rules.yml`, `ci/sonarqube-quality-gate.json`, `ci/validate_configs.py`.
4. **Bao quát đầy đủ 2 nhóm lỗi: Lỗi mã nguồn (Code) và Lỗi vận hành/triển khai (Ops):**
   - Nhóm Code: SQL Injection (CWE-89), Hardcoded Credentials (CWE-798), Session cookie thiếu bảo mật, LFI.
   - Nhóm Ops: Xung đột container Compose, Mất kết nối DB gây lỗi 500, NPM lỗi 502, Lộ thông tin nhạy cảm qua phản hồi HTTP.

---

### ⚠️ C. NHỮNG GÌ CHƯA ĐẠT HOẶC CÒN THIẾU CẦN BỔ SUNG GẤP VÀO BÁO CÁO

Đây là các điểm mấu chốt giảng viên sẽ chấm điểm trực tiếp, **bắt buộc phải bổ sung vào Báo cáo 05**:

#### 1. [TRỌNG YẾU] Chưa đối chiếu với Nghị định 13/2023/NĐ-CP hoặc GDPR
* **Thực trạng:** Báo cáo hiện tại mới chỉ viện dẫn các tiêu chuẩn kỹ thuật (OWASP, CWE, NIST), **hoàn toàn chưa có điều khoản nào của Nghị định 13/2023/NĐ-CP (Luật Bảo vệ dữ liệu cá nhân Việt Nam) hoặc GDPR (Châu Âu)**.
* **Yêu cầu bổ sung:** Đối chiếu trực tiếp các vi phạm an toàn của ứng dụng với:
  - **Nghị định 13/2023/NĐ-CP:**
    - *Điều 9:* Vi phạm nghĩa vụ bảo vệ dữ liệu cá nhân của khách hàng khi để lộ thông tin vận đơn và tài khoản qua SQLi.
    - *Điều 13:* Vi phạm quy định về áp dụng các biện pháp kỹ thuật và an ninh để bảo vệ dữ liệu cá nhân (lưu mật khẩu dạng thô plaintext trong bảng `users`, không mã hóa dữ liệu nhạy cảm).
    - *Điều 17:* Vi phạm quy định về trách nhiệm thông báo và xử lý sự cố rò rỉ dữ liệu cá nhân khi thiếu hệ thống ghi vết nhật ký kiểm toán.
  - **GDPR:**
    - *Article 5(1)(f):* Vi phạm nguyên tắc bảo mật và toàn vẹn dữ liệu (Integrity and Confidentiality).
    - *Article 25:* Vi phạm nguyên tắc bảo vệ dữ liệu ngay từ khâu thiết kế (Data protection by design and by default).
    - *Article 32:* Vi phạm yêu cầu thực thi các biện pháp kỹ thuật phù hợp (Security of processing).

#### 2. [TRỌNG YẾU] Cần cấu trúc rõ ràng 5 vấn đề an toàn tương ứng với 5 thành viên nhóm
* **Thực trạng:** Báo cáo đang trình bày các lỗi kỹ thuật dàn trải, chưa phân bổ tường minh theo từng thành viên.
* **Yêu cầu bổ sung:** Thiết kế mục chuyên biệt **Chương 5: Phân tích 5 vấn đề an toàn ứng dụng và minh chứng xử lý của 5 thành viên**:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│             PHÂN BỔ 5 VẤN ĐỀ AN TOÀN THEO 5 THÀNH VIÊN VÀ PHA DEVSECOPS                │
├──────────────────┬──────────────────────┬─────────────┬──────────────┬─────────────────┤
│ Thành viên nhóm  │ Vấn đề an toàn       │ Nhóm lỗi    │ Pha DevSecOps│ Chính sách luật │
├──────────────────┼──────────────────────┼─────────────┼──────────────┼─────────────────┤
│ 1. Nguyễn Giang  │ Kiểm soát phân nhánh │ Vận hành &  │ CODE / COMMIT│ NĐ 13: Điều 13  │
│    Nam (Lead)    │ & quy chuẩn đóng góp │ Quản trị    │ (Stage 1)    │ (Kiểm soát đổi) │
├──────────────────┼──────────────────────┼─────────────┼──────────────┼─────────────────┤
│ 2. Nguyễn Đình   │ Lỗ hổng SQL Injection│ Mã nguồn    │ TEST / SAST  │ NĐ 13: Điều 9   │
│    Hải           │ lộ dữ liệu đơn hàng  │ (Code)      │ (Stage 2)    │ GDPR: Art. 32   │
├──────────────────┼──────────────────────┼─────────────┼──────────────┼─────────────────┤
│ 3. Đào Xuân      │ Mật khẩu lưu tĩnh và │ Mã nguồn    │ BUILD / GATE │ NĐ 13: Điều 13  │
│    Mạnh          │ rò rỉ thông tin CSDL │ (Code)      │ (Stage 2)    │ GDPR: Art. 25   │
├──────────────────┼──────────────────────┼─────────────┼──────────────┼─────────────────┤
│ 4. Lê Đức        │ Mất an toàn cấu hình │ Triển khai  │ RELEASE / CD │ NĐ 13: Điều 13  │
│    Anh           │ & lộ cổng kết nối DB │ (Deployment)│ (Stage 3 & 4)│ (Cô lập hạ tầng)│
├──────────────────┼──────────────────────┼─────────────┼──────────────┼─────────────────┤
│ 5. Nguyễn Phương │ Thiếu giám sát truy  │ Vận hành &  │ OPERATE /    │ NĐ 13: Điều 17  │
│    Mai           │ vết rò rỉ dữ liệu    │ Giám sát    │ MONITOR (S4) │ GDPR: Art. 33   │
└──────────────────┴──────────────────────┴─────────────┴──────────────┴─────────────────┘
```

#### 3. Bổ sung đoạn code demo cụ thể của từng thành viên
Mỗi thành viên cần có một hộp code demo làm rõ:
- Mã công cụ phát hiện (Script / Rule / LogQL).
- Mã nguồn khắc phục / Cấu hình vá lỗi.

#### 4. Bổ sung thông tin Mã sinh viên và GVHD ở trang bìa
- Bổ sung Mã học viên (MSV) của cả 5 bạn, đặc biệt là Trưởng nhóm Nguyễn Giang Nam.
- Bổ sung tên Giảng viên hướng dẫn môn học.

#### 5. Bổ sung Sơ đồ CSDL (ERD) và Cây thư mục dự án
- Bổ sung cấu trúc 2 database (`ilfreight` và `dev`) để làm sáng tỏ đối tượng dữ liệu cá nhân cần bảo vệ.

#### 6. Kiểm soát dung lượng và độ dài báo cáo (Dưới 30 trang khi xuất PDF)
- Báo cáo hiện tại đang khá chi tiết; khi xuất bản sang PDF nộp thầy, cần rút gọn khoảng trống, căn lề và định dạng bảng để không bị vượt quá giới hạn 30 trang theo yêu cầu của thầy.

---

## PHẦN 3: KẾ HOẠCH HÀNH ĐỘNG TRIỂN KHAI VÀO BÁO CÁO 05

Dưới đây là checklist từng đầu việc cụ thể cần thực hiện để nâng cấp tệp [`docs/05-Báo cáo bài tập lớn DevSecOps.md`](file:///d:/PTIT-DevOps-SonarQube/docs/05-Báo%20cáo%20bài%20tập%20lớn%20DevSecOps.md):

### Giai đoạn 1: Bổ sung các yêu cầu bắt buộc của Giảng viên (Ưu tiên số 1)
- [x] **Task 1.1:** Cập nhật bảng thông tin trang bìa:
  - Thêm tên Giảng viên hướng dẫn môn học.
  - Thêm Mã học viên (MSV) của Trưởng nhóm Nguyễn Giang Nam và 4 thành viên.
- [x] **Task 1.2:** Tái cấu trúc mục phân công và trách nhiệm (Phần mở đầu):
  - Bổ sung cột `% Mức độ đóng góp` (100% cho mỗi thành viên).
  - Thêm tóm tắt ma trận 5 vấn đề an toàn tương ứng với 5 thành viên và liên kết neo trực tiếp tới Mục 5.1.
- [x] **Task 1.3:** Xây dựng mục phân tích chi tiết 5 vấn đề an toàn theo 5 thành viên (Tại Chương 5):
  - **Mục 5.1.1 — Vấn đề 1 (Nguyễn Giang Nam):** Vi phạm chính sách kiểm soát thay đổi hệ thống và lộ mã nguồn thiếu kiểm soát (NĐ 13/2023 Điều 13 Khoản 1 & GDPR Art. 25). Giải pháp Policy-as-Code qua `ci/policy_guard.py`. Code demo kiểm tra quy chuẩn PR/Commit.
  - **Mục 5.1.2 — Vấn đề 2 (Nguyễn Đình Hải):** Vi phạm bảo mật dữ liệu người dùng qua lỗ hổng SQL Injection (NĐ 13/2023 Điều 9 Khoản 2 & GDPR Art. 32). Giải pháp Security-as-Code qua Semgrep Taint Analysis & SonarQube `php:S2077`. Code demo quy tắc Semgrep, đoạn mã vi phạm và mã vá PDO Prepared Statement.
  - **Mục 5.1.3 — Vấn đề 3 (Đào Xuân Mạnh):** Vi phạm lưu trữ dữ liệu xác thực và mật khẩu gán cứng (NĐ 13/2023 Điều 13 Khoản 2 & GDPR Art. 5(1)(f) & Art. 25). Giải pháp kiểm định Quality Gate qua SonarQube & Semgrep local rules. Code demo phát hiện rule `php-hardcoded-db-password-fallback` và mã hash an toàn Bcrypt.
  - **Mục 5.1.4 — Vấn đề 4 (Lê Đức Anh):** Vi phạm an toàn triển khai hạ tầng và mở cổng cơ sở dữ liệu (NĐ 13/2023 Điều 13 Khoản 1 & GDPR Art. 32). Giải pháp thẩm định cấu hình tĩnh qua `ci/validate_configs.py` và phân lập mạng Docker Compose. Code demo test case kiểm tra port và cấu hình Compose cách ly cổng 3306.
  - **Mục 5.1.5 — Vấn đề 5 (Nguyễn Phương Mai):** Vi phạm yêu cầu ghi vết nhật ký và ứng phó sự cố an ninh dữ liệu (NĐ 13/2023 Điều 17 & GDPR Art. 33). Giải pháp giám sát tập trung Loki/Promtail/Grafana và Autoheal. Code demo biểu thức LogQL trích xuất tấn công và cấu hình tự phục hồi container.

---

### Giai đoạn 2: Bổ sung kiến trúc dữ liệu và kỹ thuật cốt lõi (Ưu tiên số 2)
- [x] **Task 2.1:** Thêm Sơ đồ quan hệ thực thể (ERD) và bảng mô tả 2 cơ sở dữ liệu `ilfreight` và `dev` tại Chương 1 (làm rõ dữ liệu nhạy cảm: mật khẩu, API key, email, thông tin vận chuyển).
- [x] **Task 2.2:** Thêm Sơ đồ cây thư mục mã nguồn dự án (Project Directory Structure) tại Chương 1.
- [x] **Task 2.3:** Thêm công đoạn kiểm tra cú pháp PHP Linting (`php -l`) tại Chương 2.
- [x] **Task 2.4:** Thêm cơ chế nhận diện tự động bỏ qua đóng gói khi chỉ sửa tài liệu (`eval_stage3`) tại Chương 3.
- [x] **Task 2.5:** Thêm bảng đặc tả chi tiết câu lệnh LogQL và Regex bóc tách của toàn bộ 8 Panel trên Dashboard Grafana tại Chương 4.

---

### Giai đoạn 3: Chuẩn hóa học thuật & Kiểm soát số trang (Ưu tiên số 3)
- [x] **Task 3.1:** Bổ sung Danh mục hình vẽ và Danh mục bảng biểu sau Mục lục.
- [x] **Task 3.2:** Bổ sung tiểu mục Phương pháp nghiên cứu khoa học (Lý thuyết, Thực nghiệm, Phân tích tĩnh, Mô phỏng tấn công) ở Phần mở đầu.
- [x] **Task 3.3:** Bổ sung Bảng phân tích tối ưu tổng chi phí sở hữu (TCO) ở Chương 6 (đối chiếu giải pháp FOSS với công cụ thương mại > $35,000/năm).
- [x] **Task 3.4:** Rà soát lại toàn bộ liên kết neo Mục lục (Anchor Links) bằng `scratch/verify_toc.py` để đảm bảo 100% không bị lỗi link.
- [x] **Task 3.5:** Tinh gọn các đoạn log thô thành trích dẫn trọng tâm để khi chuyển đổi sang PDF đảm bảo không vượt quá 30 trang theo quy định (Đã cô đọng các đoạn log thô thành cấu trúc bảng biểu và trích dẫn JSON ngắn gọn, loại bỏ các chuỗi lặp dư thừa).

---

## HƯỚNG DẪN SỬ DỤNG FILE CHECKLIST
Mỗi khi một đầu việc trong danh sách trên được hoàn thành và cập nhật vào [`docs/05-Báo cáo bài tập lớn DevSecOps.md`](file:///d:/PTIT-DevOps-SonarQube/docs/05-Báo%20cáo%20bài%20tập%20lớn%20DevSecOps.md), chuyển ký hiệu `[ ]` thành `[x]` để theo dõi tiến độ hoàn thiện báo cáo trước ngày nộp 31/10/2026.
