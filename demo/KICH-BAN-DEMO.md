# Kịch bản quay video demo DevSecOps

Nguyễn Đình Hải, B26CHAT010, nhóm 11.
Mọi lệnh chạy từ thư mục gốc của kho.

```bash
cd /mnt/d/Master_PTIT/DevSecops/devsec-btl/PTIT-DevOps-SonarQube
```

---

## Màn 0. Chuẩn bị, chỉ làm một lần trước khi quay

Hai bản sửa đường ống đang nằm trên nhánh `haind`, phải đưa lên `main` thì mới dùng được.

```bash
gh pr create --base dev --head haind \
  --title "[haind] ci(pipeline): siet Production Gate va cho phep chay thu cong Stage 4" \
  --body "Hai thay doi dieu kien job cua duong ong."
gh pr merge --merge

gh pr create --base main --head dev \
  --title "release: v1.2.2 - siet Production Gate va cho phep chay thu cong Stage 4" \
  --body "Phat hanh ban sua dieu kien job."
gh pr merge --merge
```

Cú merge thứ hai tự chạy một lượt `[PROD DEPLOY]` và triển khai thật. Chờ nó xong rồi hãy bắt đầu quay.

Kiểm tra bản sửa đã lên `main` chưa:

```bash
git fetch origin main
git show origin/main:.github/workflows/devsecops-pipeline.yml | grep -n "workflow_dispatch" | head
```

---

## Màn 1. Cổng kiểm định chặn build

Nói: đây là lượt chạy bình thường, cổng chất lượng bật.

```bash
gh workflow run devsecops-pipeline.yml --ref main
python demo/demo_live_ci.py --watch
```

Màn hình sẽ cho thấy:

```
Stage 1 Policy Guard              THÀNH CÔNG
Stage 2 SonarQube SAST            THẤT BẠI
Stage 2 Semgrep Security SAST     THẤT BẠI
Stage 3 Production Gate           BỎ QUA
Stage 4 Deploy Web Workload       BỎ QUA
Stage 4 Deploy Observability      BỎ QUA
```

Nhấn `Ctrl+C` để thoát theo dõi, rồi xổ bảng lỗi của mình:

```bash
python demo/demo_live_ci.py --errors -m 2
```

Quay cảnh này để chỉ vào từng lỗi, vị trí tệp, dòng, mã CWE và điều khoản pháp lý.

---

## Màn 2. Thả cổng, đi hết đường ống lên production

Nói: giờ chuyển sang chế độ chỉ báo cáo, công cụ vẫn quét nhưng không chặn.

```bash
gh workflow run devsecops-pipeline.yml --ref main -f enforce_quality_gate=false
python demo/demo_live_ci.py --watch
```

Lần này đủ sáu job xanh, Stage 4 triển khai thật lên máy chủ. Mất khoảng ba tới năm phút.

Mở trang web thật để xác nhận đã lên:

```
https://inlaneweb.ecotools.online
```

---

## Màn 3. Bắn payload và soi nhật ký trên Grafana

Demo đúng **một lỗ hổng**: `V2`, ép lỗi đọc dữ liệu tại trang chi tiết cảng.

### 3.1 Làm tay trên trình duyệt

Gõ thẳng vào thanh địa chỉ:

```
https://inlaneweb.ecotools.online/ports/CN SHA' AND extractvalue(1,concat(0x7e,(SELECT database())))-- -
```

Trang trả về thông báo lỗi XPath của MariaDB, trong đó lộ tên cơ sở dữ liệu là `ilfreight`.
Quay cận cảnh dòng lỗi này.

Giải thích: tham số mã cảng được nối thẳng vào câu lệnh SQL. Hàm `extractvalue` bị ép nhận
một chuỗi sai cú pháp, và MariaDB in luôn chuỗi đó ra thông báo lỗi, kèm kết quả của
`SELECT database()`. Ứng dụng lại hiển thị nguyên thông báo lỗi ra trình duyệt.

### 3.2 Tạo đỉnh trên biểu đồ

Gõ tay một lần thì đường biểu đồ chỉ nhích rất nhẹ. Chạy lệnh sau để thấy rõ:

```bash
python scripts/simulate_telemetry.py --mem haind --cases V2 \
  --base-url https://inlaneweb.ecotools.online \
  --repeat 5 --delay 0.6
```

Lệnh này chỉ chạy `V2`, không đụng hai kịch bản còn lại, và in ra:

```
DIỄN TẬP KIỂM THỬ AN NINH  ·  Nguyễn Đình Hải  (B26CHAT010)
Mã định danh : MEM_HAIND
```

### 3.3 Soi trên Grafana

```
https://grafana.ecotools.online/d/inlaneweb-observability/425fff55-303d-52d8-894c-c30238eeef1f
admin / keTMheOR73x3vrijcLDCmMfJ
```

Đặt khung `Last 15 minutes`, tự làm mới `10s`.

Lọc đúng dấu vết của mình bằng một chuỗi:

```
{container="ilfreight_web"} |= "MEM_HAIND"
```

Tách riêng hai luồng nhật ký để cho thấy cùng một mã định danh đi vào cả hai:

```
{container="ilfreight_web"} |= "MEM_HAIND" |= "apache_http_traffic"
{container="ilfreight_web"} |= "MEM_HAIND" |= "APP-EXCEPTION"
```

Ba phân vùng sẽ phản ứng:

| Phân vùng | Thấy gì |
|---|---|
| SQL Injection trong lưu lượng HTTP | Yêu cầu GET mang chuỗi `extractvalue` và `SELECT database()` |
| Rò rỉ lỗi và mã phản hồi 5xx | Chuỗi `XPATH syntax error` kèm trường `failed_query` |
| Security Telemetry by Team Members | Đúng một đường mang tên `[HAIND] Nguyễn Đình Hải` |

Chỉ vào chuỗi `MEM_HAIND` được Grafana tô sáng để chứng minh truy được về đúng người chạy.

## Lời dẫn gợi ý cho ba màn

Màn 1: tiêu chuẩn an toàn được viết thành quy tắc máy đọc được, nên lỗi bị chặn ngay lúc hợp nhất chứ không chờ tới môi trường thật.

Màn 2: khi chuyển sang chế độ chỉ báo cáo, đường ống đi hết bốn chặng và triển khai, cho thấy chặn hay không chặn là một công tắc chính sách chứ không phải sửa mã.

Màn 3: phân tích tĩnh chỉ khẳng định mẫu cú pháp nguy hiểm. Phải bắn payload thật và soi nhật ký mới chứng minh được hệ thống nhận ra bị tấn công, và nhận ra bằng quy tắc nào.

---

## Phòng khi trục trặc

Xem lại lượt chạy gần nhất mà không kích hoạt mới:

```bash
python demo/demo_live_ci.py --latest
```

Xem bảng lỗi của cả năm người:

```bash
python demo/demo_live_ci.py --errors --all
```

Nếu chữ tiếng Việt bị vỡ trên Windows, thêm `-X utf8`:

```bash
python -X utf8 demo/demo_live_ci.py --watch
```
