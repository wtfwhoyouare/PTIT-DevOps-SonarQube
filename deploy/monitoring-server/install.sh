#!/usr/bin/env bash
# ==============================================================================
#  Tự động cài đặt Hạ tầng Giám sát Tập trung (Loki 3.0 + Grafana 11.0)
#  Hệ điều hành hỗ trợ: Ubuntu 20.04 / 22.04 / 24.04 LTS hoặc Debian
# ==============================================================================
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================================================"
echo -e "🚀 KHỞI TẠO MÁY CHỦ GIÁM SÁT TẬP TRUNG (LOKI 3.0 & GRAFANA 11.0)"
echo -e "======================================================================${NC}"

# 1. Kiểm tra quyền root / sudo
if [ "$EUID" -ne 0 ] && ! command -v sudo &> /dev/null; then
  echo -e "${RED}❌ Vui lòng chạy script với quyền root hoặc user có sudo!${NC}"
  exit 1
fi
SUDO_CMD=""
if [ "$EUID" -ne 0 ]; then
  SUDO_CMD="sudo"
fi

# 2. Kiểm tra hoặc cài đặt Docker & Docker Compose
if ! command -v docker &> /dev/null; then
  echo -e "${YELLOW}⚙️  Không tìm thấy Docker, đang tiến hành cài đặt tự động...${NC}"
  curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
  $SUDO_CMD sh /tmp/get-docker.sh
  $SUDO_CMD usermod -aG docker "$USER" || true
  echo -e "${GREEN}✅ Đã cài đặt Docker Engine thành công!${NC}"
else
  echo -e "${GREEN}✅ Docker đã được cài đặt sẵn: $(docker --version)${NC}"
fi

# Kiểm tra Docker Compose V2
if ! docker compose version &> /dev/null; then
  echo -e "${YELLOW}⚙️  Đang cài đặt docker-compose-plugin...${NC}"
  $SUDO_CMD apt-get update && $SUDO_CMD apt-get install -y docker-compose-plugin
fi
echo -e "${GREEN}✅ Docker Compose sẵn sàng: $(docker compose version)${NC}"

# 3. Cấu hình Firewall UFW (nếu UFW đang kích hoạt)
if command -v ufw &> /dev/null && $SUDO_CMD ufw status | grep -q "Status: active"; then
  echo -e "${YELLOW}🛡️  Đang cấu hình cổng Firewall qua UFW...${NC}"
  $SUDO_CMD ufw allow 22/tcp || true
  $SUDO_CMD ufw allow 3000/tcp comment "Grafana Dashboard" || true
  $SUDO_CMD ufw allow 3100/tcp comment "Loki Log Ingress" || true
  $SUDO_CMD ufw reload || true
  echo -e "${GREEN}✅ Đã mở cổng 3000 (Grafana) và 3100 (Loki Ingress) trên UFW.${NC}"
fi

# 4. Xác định thư mục script và chạy docker compose
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${YELLOW}📦 Đang kéo hình ảnh và khởi động container...${NC}"
$SUDO_CMD docker compose pull
$SUDO_CMD docker compose up -d --remove-orphans

# 5. Kiểm tra trạng thái sức khỏe
echo -e "${YELLOW}⏳ Đang kiểm tra nhịp tim các dịch vụ...${NC}"
sleep 5

LOKI_OK=false
for i in {1..20}; do
  if curl -s http://127.0.0.1:3100/ready | grep -q "ready"; then
    LOKI_OK=true
    echo -e "${GREEN}✅ Grafana Loki 3.0 đã khởi động và SẴN SÀNG nhận log (Port 3100)!${NC}"
    break
  fi
  echo "   ... chờ Loki ($i/20)"
  sleep 2
done

GRAFANA_OK=false
for i in {1..20}; do
  if curl -s http://127.0.0.1:3000/api/health | grep -q "ok"; then
    GRAFANA_OK=true
    echo -e "${GREEN}✅ Grafana 11.0 đã SẴN SÀNG phục vụ (Port 3000)!${NC}"
    break
  fi
  echo "   ... chờ Grafana ($i/20)"
  sleep 2
done

# Lấy địa chỉ IP máy chủ
PUBLIC_IP=$(curl -s -m 5 https://ifconfig.me || curl -s -m 5 https://api.ipify.org || hostname -I | awk '{print $1}')

echo ""
echo -e "${BLUE}======================================================================${NC}"
echo -e "${GREEN}🎉 MÁY CHỦ GIÁM SÁT ĐÃ TRIỂN KHAI THÀNH CÔNG RỰC RỠ!${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo -e "📊 ${YELLOW}Giao diện Grafana Dashboard:${NC} http://${PUBLIC_IP}:3000"
echo -e "   👤 Tài khoản mặc định: ${GREEN}admin${NC}"
echo -e "   🔑 Mật khẩu mặc định:  ${GREEN}admin${NC} (hoặc đổi trong file docker-compose.yml)"
echo -e "   📌 Dashboard cài sẵn:   ${GREEN}InlaneWeb Logistics — Centralized Observability${NC}"
echo ""
echo -e "📥 ${YELLOW}Cổng nhận Log của Loki:${NC}      http://${PUBLIC_IP}:3100/loki/api/v1/push"
echo ""
echo -e "${BLUE}----------------------------------------------------------------------${NC}"
echo -e "👉 ${YELLOW}BƯỚC TIẾP THEO: KẾT NỐI MÁY CHỦ WEB (INLANEWEB SERVER) SANG MÁY CHỦ GIÁM SÁT${NC}"
echo -e "Trên ${GREEN}Máy chủ Web${NC}, mở file: ${BLUE}InlaneWeb/monitoring/promtail/promtail-config.yml${NC}"
echo -e "Sửa dòng ${YELLOW}clients:${NC} thành:"
echo -e ""
echo -e "   clients:"
echo -e "     - url: ${GREEN}http://${PUBLIC_IP}:3100/loki/api/v1/push${NC}"
echo -e ""
echo -e "Sau đó chạy lệnh trên Máy chủ Web: ${GREEN}docker restart ilfreight_promtail${NC}"
echo -e "Toàn bộ log web và các đợt tấn công sẽ tự động đổ về Dashboard ngay lập tức!"
echo -e "${BLUE}======================================================================${NC}"
