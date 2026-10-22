# Bàn giao phần việc Đào Xuân Mạnh

- Thành viên: **Đào Xuân Mạnh** — GitHub `vstxckr`.
- Tác giả commit: `Manh Dao Xuan <manhdaoxuan2808@gmail.com>`.
- Phạm vi: User Authentication, Profile & Community.
- Nguồn phân công: mục 3 (MẠNH) trong `PTIT-DevOps-Draft/PHAN_CONG_NHIEM_VU.md`.
- Nhánh làm việc: `manhdx`, xuất phát từ `dev` (`ed67851`). PR đích: `dev`, theo README hiện tại của repository SonarQube. Quy trình này thay cho nhánh `feature/user-auth-profile` → `main` trong Draft.

## Phạm vi đã thực hiện

Bổ sung đủ 7 file được giao từ Draft, giữ nguyên nội dung sau khi chuẩn hóa CRLF thành LF. Đây là phiên bản lab cố ý có lỗi để pipeline thu thập bằng chứng cho bài tập; các hướng sửa bên dưới chưa được áp dụng vào bản baseline này.

| File trong `InlaneWeb/web/src/pages/` | Route tích hợp qua router có sẵn | Chức năng |
| --- | --- | --- |
| `login.php` | `GET/POST /login` | Form đăng nhập, truy vấn tài khoản, lưu `uid` vào session, chuyển tới hồ sơ |
| `logout.php` | `/logout` | Hủy session và chuyển về trang chủ |
| `account.php` | `GET /account` | Yêu cầu đăng nhập; hiển thị hồ sơ, form email và danh sách vận đơn cá nhân |
| `account_update.php` | `POST /account/update` | Yêu cầu đăng nhập; cập nhật email và hiển thị số dòng bị ảnh hưởng |
| `news.php` | `GET /news`, `GET /news?id=` | Danh sách và chi tiết tin tức |
| `comment_add.php` | `/shipments/{id}/comments` (nội dung qua POST) | Yêu cầu đăng nhập; thêm bình luận vận đơn |
| `comment_delete.php` | `/comments/{id}/delete` | Yêu cầu đăng nhập; xóa bình luận |

Các handler dùng `db.php`, `layout.php`, session và schema do các thành viên khác phụ trách. Không cần sửa router để nạp 7 file này. Bình luận thuộc vận đơn, không thuộc bài tin tức. Tính đầy đủ của toàn ứng dụng còn phụ thuộc các module của thành viên khác được tích hợp vào `dev`.

## Bốn lỗi được phân công

Dòng mã bên dưới lấy từ phiên bản thực tế, không chép số dòng ước lượng của Draft. Mã rule SonarQube lấy từ bảng phân công; chỉ được xác nhận là kết quả SonarQube khi có artifact của lần scan thật.

| Mục | Vị trí thực tế | Phân tích và tác động | Hướng khắc phục sau baseline |
| --- | --- | --- | --- |
| Code Quality 1 — dự kiến `php:S121` | `login.php:36` | `if ($error) flash(...)` thiếu `{}`; thêm lệnh sau này dễ tạo nhầm phạm vi điều kiện. Draft ghi Critical; chưa xác nhận severity bằng SonarQube thực tế. | Bọc lời gọi `flash` trong khối `{}`. |
| Code Quality 2 — dự kiến `Web:InputWithoutLabelCheck` | `login.php:39-44`, `account.php:28-29` | Label không có `for`, input không có `id`, cũng không nằm trong label; công cụ trợ năng không có liên kết nhãn rõ ràng. | Thêm `id` duy nhất cho từng input và `for` tương ứng vào label. |
| Security 1 — CWE-89 | `login.php:15-20` | POST `username/password` → nội suy SQL ở dòng 19 → `query_one` → `query` → `mysqli_query`. Biểu thức SQL do người dùng đưa vào có thể thay điều kiện xác thực; có hàng kết quả thì handler gán session ở dòng 24. Không cần đăng nhập trước. | Dùng prepared statement với hai tham số. Sau khi chuyển mật khẩu plaintext sang hash, dùng `password_verify`; đổi session ID sau đăng nhập. |
| Security 2 — CWE-89 | `account_update.php:17-26` | POST `email` → nội suy SQL ở dòng 20 → `exec_write` → `mysqli_query`. Điều kiện đăng nhập và `intval($u['id'])` không bảo vệ phần `SET email`; chuỗi email có thể thay cấu trúc truy vấn. | Prepared statement cho email và ID; kiểm tra email, quyền cập nhật và CSRF. |

Semgrep 1.163.0 thực sự báo rule `php.lang.security.injection.tainted-sql-string.tainted-sql-string` mức `ERROR` ở `login.php:19` và `account_update.php:20`. Đây là bằng chứng SAST và đối chiếu source; chưa phải bằng chứng khai thác trên MariaDB đang chạy. Không suy severity High/Critical hoặc CVSS chỉ từ mức `ERROR` của scanner.

Các điểm SQLi ở sắp xếp vận đơn, tin tức, thêm/xóa bình luận cũng được giữ theo Draft. Không giới hạn phạm vi rủi ro của module ở hai lỗi trong bảng phân công. Community Build có thể không phát hiện cùng luồng SQLi như Semgrep; cần đọc riêng hai báo cáo.

## Kiểm tra đã thực hiện

Ngày kiểm tra: **22/10/2026**.

1. So sánh nội dung 7 file với Draft sau chuẩn hóa xuống dòng: giống nhau.
2. `python3 -m unittest discover -s tests -v`: **11/11 đạt**. Đây là test công cụ xuất báo cáo, không phải test nghiệp vụ ứng dụng.
3. Lint toàn bộ 16 file PHP hiện có trên nhánh bằng PHP **8.1.2** cục bộ: không lỗi cú pháp. Chưa thay thế lint PHP 8.2 trong CI.
4. Chạy Semgrep:

   ```bash
   semgrep scan --config p/php --config p/security-audit \
     --config ci/semgrep-local-rules.yml --metrics off \
     --disable-version-check --json --output /tmp/ptit-manhdx-semgrep.json InlaneWeb
   ```

   Scan 28 file, chạy 37 rule áp dụng, **17 findings**, không có lỗi phân tích được báo. Riêng 7 file của Mạnh có **7 findings**: SQLi tại `account.php:41`, `account_update.php:20`, `comment_add.php:19`, `comment_delete.php:18`, `login.php:19`, `news.php:17`, và `echoed-request` tại `comment_add.php:29`. Các số này là snapshot của các ruleset tải ở thời điểm kiểm tra, không phải tổng kết quả đầy đủ của cấu hình CI vốn còn chạy `p/owasp-top-ten` và `p/cwe-top-25`.
5. Docker Desktop Linux engine không kết nối được; chưa chạy PHP 8.2/MariaDB/SonarQube bằng container. Không tuyên bố đã có kết quả SonarQube hoặc runtime.

## Kiểm chứng sau khi tích hợp

Trong môi trường lab cục bộ đã khởi động bằng Docker Compose, dùng URL thực tế **http://localhost:8088** theo `InlaneWeb/docker-compose.yml`:

1. Khi chưa đăng nhập: mở `/login`, `/news`; xác nhận `/account` và các handler cần xác thực chuyển tới `/login`.
2. Thử mật khẩu sai rồi đăng nhập `jsmith / Spring2024!`; kiểm tra hồ sơ và danh sách vận đơn, cập nhật email bằng dữ liệu hợp lệ rồi khôi phục email ban đầu.
3. Thêm bình luận vào vận đơn có thật; xóa đúng bình luận vừa tạo và kiểm tra dữ liệu. Kiểm tra danh sách/chi tiết tin tức.
4. Đăng xuất rồi truy cập `/account`; phải quay lại đăng nhập. Trang `/` cần module logistics đã tích hợp.
5. Người phụ trách review và merge PR `manhdx` → `dev`. Workflow hiện chạy khi push vào `dev` hoặc `main`, không chạy chỉ vì mở PR hoặc push `manhdx`.
6. Đọc Summary và tải artifacts SonarQube/Semgrep của đúng commit merge; ghi nhận rule, severity, file/dòng thực tế cho bài báo cáo. Đối chiếu hai lỗi chất lượng mã ở trên với artifact SonarQube, không coi các mã rule dự kiến là kết quả đã quét.

Không push hoặc merge trực tiếp vào `main`; bước `dev` → `main` do Admin/Lead thực hiện theo quy trình repo.
