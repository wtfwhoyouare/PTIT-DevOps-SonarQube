# HƯỚNG DẪN CẤU HÌNH VÀ TRIỂN KHAI PRODUCTION (CD RUNBOOK)
**HỆ THỐNG CỔNG THÔNG TIN VẬN TẢI INLANEWEB**

---

| Thuộc tính | Chi tiết |
| :--- | :--- |
| **Mã tài liệu:** | SOP-DEPLOY-04 |
| **Dự án:** | InlaneWeb Logistics Portal |
| **Phân loại:** | Quy trình vận hành tiêu chuẩn (Standard Operating Procedure - Deployment Runbook) |
| **Phiên bản:** | 1.0.0 |
| **Ngày cập nhật:** | 23/10/2026 |
| **Trạng thái:** | Sẵn sàng áp dụng |

---

## 1. MỤC ĐÍCH VÀ PHẠM VI ÁP DỤNG

### 1.1. Mục đích
Tài liệu này đóng vai trò là Sổ tay vận hành kỹ thuật (Deployment Runbook), hướng dẫn chi tiết từng bước thiết lập môi trường máy chủ Production (VPS/Cloud Server), cấu hình các biến bảo mật trên GitHub Repository Secrets, và cơ chế chuyển giao liên tục (Continuous Deployment - CD) độc lập theo kiến trúc Decoupled Zero-Downtime của dự án InlaneWeb.

> [!TIP]
> **Dành riêng cho giai đoạn ban đầu (Chỉ Deploy Web & Database):**
> Nếu anh chỉ muốn deploy ứng dụng Web và Database trước (chưa cần khởi chạy cụm Monitoring Loki/Grafana), tài liệu này đã được tinh giản riêng một lộ trình **"Web-Only Deployment"** giúp triển khai nhanh trong vòng 5 phút mà không tốn RAM cho hệ thống giám sát.

### 1.2. Phạm vi áp dụng
* Áp dụng trực tiếp cho các kỹ sư DevOps, SecOps và System Administrator phụ trách môi trường Production của hệ thống InlaneWeb.
* Áp dụng khi chuẩn bị hạ tầng mới, đưa hệ thống lên môi trường thật hoặc tích hợp máy chủ vào luồng tự động của GitHub Actions Workflow [`.github/workflows/devsecops-pipeline.yml`](file:///d:/ThS/DevOpsSec/PTIT-DevOps-SonarQube/.github/workflows/devsecops-pipeline.yml).

---

## 2. KIẾN TRÚC TRIỂN KHAI VÀ LUỒNG DỮ LIỆU TỰ ĐỘNG

Hệ thống triển khai áp dụng mô hình phân tách độc lập (Decoupled CD) giữa hạ tầng giám sát tập trung và tải làm việc nghiệp vụ web nhằm đảm bảo việc cập nhật mã nguồn diễn ra nhanh chóng, không gián đoạn luồng log giám sát:

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 │           KIẾN TRÚC TRIỂN KHAI TỰ ĐỘNG PRODUCTION (STAGE 3 & 4)        │
 └────────────────────────────────────────────────────────────────────────┘

 [ GITHUB ACTIONS RUNNER ]
      │
      ├─► STAGE 3: Production Gate (Smoke Test & E2E Validation)
      │     ├─ Validate cấu hình YAML / Python
      │     ├─ Build Docker Image InlaneWeb (PHP 8.2 Apache)
      │     ├─ Chạy Ephemeral Stack (App + MariaDB + Loki + Promtail + Grafana)
      │     ├─ Healthcheck /health (HTTP 200) & E2E Smoke Test
      │     └─ Push Image đã kiểm định lên GitHub Container Registry (GHCR)
      │        └── Tag: ghcr.io/<owner>/inlaneweb:<sha> & :latest
      │
      └─► STAGE 4: Production CD (SSH Over Target VPS)
            │
            ├─► Job 1: Deploy Observability Platform (Loki, Promtail, Grafana, Autoheal)
            │     └── Lệnh: docker compose -f docker-compose.monitoring.yml up -d
            │
            └─► Job 2: Deploy Web Workload (Self-contained Image từ GHCR)
                  └── Lệnh: INLANEWEB_IMAGE=<ghcr_uri> docker compose -f docker-compose.prod.yml up -d --no-deps web
```

---

## 3. CÁC THÀNH PHẦN CẦN CHUẨN BỊ (CHECKLIST TIỀN TRIỂN KHAI)

| STT | Thành phần | Trạng thái hiện tại | Mô tả yêu cầu |
| :---: | :--- | :---: | :--- |
| **1** | Kịch bản CI/CD (`devsecops-pipeline.yml`) | ✅ Đã sẵn sàng | Tích hợp sẵn 4 Stage: Guard, SAST, Smoke Test, Production CD. |
| **2** | File Compose Production (`docker-compose.prod.yml`) | ✅ Đã sẵn sàng | Chạy Web từ Image GHCR + DB với Volume dữ liệu độc lập. |
| **3** | File Compose Monitoring (`docker-compose.monitoring.yml`) | ✅ Đã sẵn sàng | Cụm Loki, Promtail, Grafana và Autoheal container. |
| **4** | Hạ tầng máy chủ Production (VPS/Server) | ⏳ **Cần cấu hình** | Cài Docker Engine, Docker Compose V2, cấu hình Firewall. |
| **5** | Khóa xác thực SSH (Deploy Key) | ⏳ **Cần cấu hình** | Cặp Public/Private Key dùng riêng cho CI/CD Runner kết nối VPS. |
| **6** | Biến GitHub Repository Secrets | ⏳ **Cần cấu hình** | Khai báo `PROD_HOST`, `PROD_USER`, `PROD_SSH_KEY`,... |
| **7** | Quyền truy cập GitHub Container Registry (GHCR) | ⏳ **Cần cấu hình** | Chuyển Visibility Package sang Public hoặc cấp Token đọc Image. |

---

## 4. CHI TIẾT CÁC BƯỚC CẤU HÌNH VÀ THỰC THI

### BƯỚC 1: Khởi tạo Cặp Khóa SSH và Phân quyền trên VPS

Để GitHub Actions Runner có thể kết nối vào máy chủ VPS thông qua SSH mà không cần mật khẩu tương tác, kỹ sư cần tạo một cặp SSH Key chuyên dụng:

#### 1.1. Sinh cặp khóa SSH chuyên dụng
Mở terminal trên máy quản trị hoặc trực tiếp trên VPS và chạy lệnh:
```bash
ssh-keygen -t ed25519 -C "github-actions-cd@inlaneweb" -f ~/.ssh/id_ed25519_inlaneweb -N ""
```
* Kết quả sinh ra 2 tệp:
  * Private Key: `~/.ssh/id_ed25519_inlaneweb` (Dùng để đưa vào GitHub Secret).
  * Public Key: `~/.ssh/id_ed25519_inlaneweb.pub` (Đưa vào VPS).

#### 1.2. Thêm Public Key vào VPS
Đăng nhập vào VPS với user triển khai (ví dụ: `deploy` hoặc `ubuntu`):
```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
cat ~/.ssh/id_ed25519_inlaneweb.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

---

### BƯỚC 2: Chuẩn bị Hạ tầng Môi trường trên VPS

#### 2.1. Cài đặt Docker & Docker Compose V2
Nếu máy chủ chưa có Docker, tiến hành cài đặt:
```bash
# Gỡ bỏ các bản cũ (nếu có)
sudo apt update && sudo apt remove -y docker docker-engine docker.io containerd runc || true

# Cài đặt Docker Engine chính thức
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Cấp quyền chạy docker không cần sudo cho user
sudo usermod -aG docker $USER
newgrp docker
```

Kiểm tra xác nhận:
```bash
docker --version
docker compose version
```

#### 2.2. Mở cổng Firewall (UFW)
Đảm bảo máy chủ mở các cổng cần thiết cho dịch vụ:
```bash
sudo ufw allow 22/tcp     # SSH Port
sudo ufw allow 8088/tcp   # Cổng Web InlaneWeb (hoặc port reverse proxy 80/443)
sudo ufw allow 3000/tcp   # Cổng Grafana Dashboard (hoặc chỉ mở nội bộ qua VPN/SSH Tunnel)
sudo ufw reload
```

#### 2.3. Khởi tạo Thư mục Ứng dụng & Nạp duy nhất tệp docker-compose.prod.yml
Theo đúng chuẩn **Self-contained Image** (mã nguồn ứng dụng đã được đóng gói 100% trong Docker Image từ GHCR), máy chủ VPS **tuyệt đối KHÔNG cần cài Git và KHÔNG cần clone mã nguồn**. 

Trên VPS, chỉ cần tạo thư mục và lưu duy nhất tệp [`docker-compose.prod.yml`](file:///d:/ThS/DevOpsSec/PTIT-DevOps-SonarQube/InlaneWeb/docker-compose.prod.yml):
```bash
sudo mkdir -p /opt/inlaneweb
sudo chown -R $USER:$USER /opt/inlaneweb
cd /opt/inlaneweb

# Cách 1: Tải trực tiếp file compose prod từ GitHub (hoặc scp từ máy dev sang)
curl -fsSL https://raw.githubusercontent.com/wtfwhoyouare/PTIT-DevOps-SonarQube/main/InlaneWeb/docker-compose.prod.yml -o docker-compose.prod.yml
```

#### 2.4. Khởi tạo Docker Network Dùng chung
Khởi tạo bridge network `inlaneweb_net` cho container kết nối nội bộ:
```bash
docker network create inlaneweb_net || true
```

---

### BƯỚC 3: Cấu hình GitHub Actions Repository Secrets

Truy cập vào kho lưu trữ GitHub của dự án:
👉 **Settings** > **Secrets and variables** > **Actions** > Nhấn **New repository secret**.

Thiết lập các Secrets sau:

| Tên Secret | Bắt buộc | Giá trị mẫu | Giải thích chi tiết |
| :--- | :---: | :--- | :--- |
| `PROD_HOST` | **Có** | `103.176.179.88` (hoặc domain VPS) | Địa chỉ IP Public hoặc FQDN của máy chủ Production. |
| `PROD_USER` | **Có** | `ubuntu` hoặc `deploy` | Tên tài khoản Linux trên VPS có quyền thực thi Docker. |
| `PROD_SSH_KEY` | **Có** | `-----BEGIN OPENSSH PRIVATE KEY-----...` | Toàn bộ nội dung Private Key (`~/.ssh/id_ed25519_inlaneweb`). Copy từ dòng đầu đến dòng cuối. |
| `PROD_PORT` | Không | `22` (Mặc định: 22) | Cổng dịch vụ SSH nếu VPS đổi cổng tùy biến. |
| `PROD_PATH` | Không | `/opt/inlaneweb` (Mặc định) | Đường dẫn thư mục gốc chứa dự án trên máy chủ VPS. |

> [!CAUTION]
> Tuyệt đối không commit Private Key lên Git. Toàn bộ thông tin kết nối phải được lưu trữ trong GitHub Secrets.

---

### BƯỚC 4: Cấu hình Quyền Truy cập GitHub Container Registry (GHCR)

Quy trình triển khai của InlaneWeb sử dụng mô hình **Self-contained Image**: Image được build và test hoàn tất ở Stage 3 rồi push lên GHCR, sau đó máy chủ VPS chỉ cần `docker pull` về chạy mà không phải tốn tài nguyên build trên VPS.

Tùy theo anh muốn để Image dạng **Public** hay **Private**, thực hiện cấu hình tương ứng:

#### Cách 1: Đổi Package sang Public (Khuyên dùng — Không cần login gì trên VPS)
Nếu repository và package để chế độ Public:
1. Truy cập: `https://github.com/users/<username>/packages/container/package/inlaneweb`
2. Chọn **Package settings** (ở cột bên phải).
3. Cuộn xuống mục **Danger Zone** > chọn **Change visibility** > Chọn **Public** và xác nhận.
4. **Kết quả:** Trên VPS có thể kéo trực tiếp `docker pull ghcr.io/<username>/inlaneweb:latest` mà **không cần chạy bất kỳ lệnh `docker login` nào**!

---

#### Cách 2: Giữ Private và Đăng nhập bằng Personal Access Token (PAT)
Nếu muốn giữ Image Private, cần cấp quyền xác thực cho VPS:

##### 1. Khởi tạo Token trên GitHub (Giao diện mới nhất):
* **Truy cập nhanh:** Mở trực tiếp liên kết `https://github.com/settings/tokens`
  *(Hoặc từ Avatar cá nhân > **Settings** > ở menu trái mục **Access** chọn **Credentials** > click vào dòng **Personal access tokens (classic)**).*
* Nhấn nút **Generate new token** (góc trên bên phải) > Chọn **Generate new token (classic)**.
* **Note:** Đặt tên nhận diện, ví dụ `vps-ghcr-token`.
* **Expiration:** Chọn `90 days` hoặc `No expiration`.
* **Scopes:** Tích duy nhất vào ô:
  * ✅ **`read:packages`** *(Download packages from GitHub Package Registry)*.
* Nhấn nút xanh **Generate token** ở cuối trang và **copy chuỗi token** vừa tạo (`ghp_...`).

##### 2. Đăng nhập Docker trên VPS (Lưu ý tránh bị treo lệnh):
> [!WARNING]
> Tuyệt đối không gõ `docker login ... --password-stdin` mà không pipe dữ liệu vào, lệnh sẽ bị treo vô tận vì Docker đứng chờ input từ bàn phím.

* **Cách A (Nhập tương tác - An toàn và Dễ nhất):**
  ```bash
  docker login ghcr.io -u <github_username>
  ```
  Khi terminal hiện `Password:`, dán mã token vừa copy vào rồi gõ **Enter**.
* **Cách B (Lệnh 1 dòng qua Pipe):**
  ```bash
  echo "ghp_xxxx..." | docker login ghcr.io -u <github_username> --password-stdin
  ```
  *(Thay `ghp_xxxx...` bằng token thật và `<github_username>` bằng tài khoản GitHub của anh).*
* Khi thấy thông báo `Login Succeeded!` là hoàn tất. Giờ đây VPS đã có quyền pull image.

---

### BƯỚC 5: Khởi tạo Dịch vụ Lần đầu trên VPS (Bootstrap Môi trường)

Tùy vào nhu cầu thực tế của anh, có thể chọn **Phương án A (Chỉ chạy Web & Database)** hoặc **Phương án B (Chạy đầy đủ cả Monitoring)**:

#### 👉 Phương án A: Chỉ Deploy Web & Database (Khuyên dùng khi bắt đầu / Tiết kiệm RAM)
Với phương án này, máy chủ VPS chỉ chạy 2 container nhẹ nhàng: `ilfreight_web` (Apache PHP 8.2) và `ilfreight_db` (MariaDB):
```bash
cd /opt/inlaneweb

# 1. Kéo Image InlaneWeb từ GHCR
docker pull ghcr.io/wtfwhoyouare/inlaneweb:latest

# 2. Khởi chạy MariaDB để nạp database init.sql
docker compose -f docker-compose.prod.yml up -d db

# 3. Chờ DB khởi tạo (khoảng 10-15s), kiểm tra xem db đã "healthy" chưa
docker compose -f docker-compose.prod.yml ps

# 4. Khởi chạy Web InlaneWeb
docker compose -f docker-compose.prod.yml up -d web

# 5. Kiểm tra sức khỏe web ngay trên VPS
curl -f -s http://localhost:8088/health
# Hoặc mở trình duyệt truy cập: http://<IP_VPS>:8088/
```
*(Khi pipeline tự động chạy qua GitHub Actions, lệnh deploy web cũng chỉ cập nhật container `web` qua `docker compose -f docker-compose.prod.yml up -d --no-deps web`, hoàn toàn độc lập và không đòi hỏi container monitoring phải bật).*

---

#### 👉 Phương án B: Chạy Toàn diện (Web + DB + Giám sát Monitoring)
Nếu sau này muốn bật thêm cụm giám sát tập trung FOSS (Loki, Promtail, Grafana, Autoheal):
```bash
cd /opt/inlaneweb

# Tải thêm file compose monitoring nếu cần
curl -fsSL https://raw.githubusercontent.com/wtfwhoyouare/PTIT-DevOps-SonarQube/main/InlaneWeb/docker-compose.monitoring.yml -o docker-compose.monitoring.yml

# Khởi chạy thêm cụm giám sát
docker compose -f docker-compose.monitoring.yml up -d

# Kiểm tra sức khỏe của Loki và Grafana
curl -s http://localhost:3100/ready
curl -s http://localhost:3000/api/health
```

---

## 5. QUY TRÌNH KÍCH HOẠT TRIỂN KHAI PRODUCTION TỰ ĐỘNG

Sau khi đã hoàn tất 5 bước cấu hình trên, quy trình deploy lên Production sẽ tuân thủ tuyệt đối quy định phân nhánh đã đề ra trong [Tài liệu Quy tắc triển khai](file:///d:/ThS/DevOpsSec/PTIT-DevOps-SonarQube/docs/02-Quy%20t%E1%BA%AFc%20tri%E1%BB%83n%20khai.md):

```mermaid
flowchart TD
    A["Dev nhánh cá nhân (vd: namng)"] -->|"PR đạt chuẩn [branch] type(scope): desc"| B("Nhánh dev")
    B -->|"Kích hoạt STAGE 1 & 2"| C{"SAST & Policy Gates"}
    C -->|"Pass (Quality Gate OK)"| D["Merge vào nhánh dev"]
    D -->|"Tạo PR phát hành: release: vX.Y.Z - ..."| E("Nhánh main")
    E -->|"Kích hoạt STAGE 3"| F{"Production Smoke Test"}
    F -->|"Pass & Push GHCR"| G["Merge PR vào main"]
    G -->|"Kích hoạt STAGE 4"| H["SSH Rollout VPS Tự Động"]
    H --> I["✅ Production Online 100%"]
```

### Các bước thực tế trên Git:
1. **Tạo Release PR từ `dev` vào `main`:**
   * Tiêu đề PR bắt buộc theo đúng regex của `policy_guard.py`:
     ```text
     release: v1.0.0 - Triển khai chính thức hệ thống InlaneWeb
     ```
2. **Kích hoạt Stage 3 (Pre-Merge Production Gate):**
   * GitHub Actions tự động kiểm thử build image, dựng stack tạm thời, gọi `/health`, xác nhận Loki nhận log và tag sẵn image GHCR.
3. **Phê duyệt & Merge PR vào `main`:**
   * Ngay khi PR được merge (sự kiện `push` vào nhánh `main`), Stage 4 được kích hoạt.
   * `production_deploy_monitoring` kiểm tra diff: nếu có cập nhật monitoring sẽ rollout Loki/Grafana.
   * `production_deploy_web` SSH vào máy chủ VPS, thực thi kéo image mới nhất từ GHCR và kích hoạt:
     ```bash
     INLANEWEB_IMAGE=ghcr.io/wtfwhoyouare/inlaneweb:<commit_sha> docker compose -f docker-compose.prod.yml up -d --no-deps web
     ```
   * Tự động kiểm tra nhịp tim endpoint `http://localhost:8088/health` trên VPS. Nếu trả về HTTP 200, hoàn tất triển khai thành công!

---

## 6. SỔ TAY XỬ LÝ SỰ CỐ TRIỂN KHAI (TROUBLESHOOTING RUNBOOK)

### 6.1. Lỗi SSH: Connection timed out hoặc Permission denied
* **Biểu hiện:** Step `Rollout Web Application` báo lỗi timeout hoặc không thể xác thực SSH key.
* **Biện pháp khắc phục:**
  1. Kiểm tra lại IP máy chủ trong Secret `PROD_HOST` và port trong `PROD_PORT`.
  2. Đảm bảo Firewall/Security Group của nhà cung cấp VPS cho phép traffic SSH từ dải IP GitHub Actions (hoặc cho phép port SSH public).
  3. Kiểm tra định dạng `PROD_SSH_KEY` trong Secrets: Đảm bảo có cả header `-----BEGIN ...` và footer `-----END ...`, không bị thừa hoặc thiếu khoảng trắng hay ký tự xuống dòng.

### 6.2. Lỗi GHCR: unauthorized / pull access denied
* **Biểu hiện:** Step trên VPS báo lỗi `docker: Error response from daemon: unauthorized`.
* **Biện pháp khắc phục:**
  1. Kiểm tra Visibility của Package trên GitHub đã chuyển sang `Public` chưa.
  2. Nếu là Private, đảm bảo lệnh `docker login ghcr.io` đã được thực thi thành công trên máy chủ với Personal Access Token hợp lệ.

### 6.3. Lỗi Healthcheck: Endpoint /health không phản hồi HTTP 200
* **Biểu hiện:** Step kiểm tra `curl -f -s http://localhost:8088/health` trả về lỗi HTTP 500 hoặc không kết nối được.
* **Biện pháp khắc phục:**
  1. Đăng nhập vào VPS và kiểm tra trạng thái container:
     ```bash
     cd /opt/inlaneweb/InlaneWeb
     docker compose -f docker-compose.prod.yml ps
     docker compose -f docker-compose.prod.yml logs web
     docker compose -f docker-compose.prod.yml logs db
     ```
  2. Xác nhận cơ sở dữ liệu `ilfreight_db` đã hoàn tất khởi tạo schema và báo trạng thái `healthy`.
  3. Kiểm tra biến môi trường kết nối database trong file `docker-compose.prod.yml`.

### 6.4. Rollback nhanh khi có sự cố nghiêm trọng
Nếu phiên bản triển khai mới gặp lỗi, kỹ sư vận hành có thể rollback tức thì về phiên bản ổn định trước đó ngay trên VPS:
```bash
cd /opt/inlaneweb/InlaneWeb

# Rollback về commit sha ổn định trước đó
INLANEWEB_IMAGE=ghcr.io/wtfwhoyouare/inlaneweb:<sha_on_dinh> docker compose -f docker-compose.prod.yml up -d --no-deps web
```
Hoặc trên GitHub: Tạo Pull Request revert commit lỗi trên nhánh `main`, pipeline sẽ tự động deploy lại commit trước đó.
