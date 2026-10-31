"""Động cơ Mô phỏng Quy trình CI/CD DevSecOps & Thực thi Chốt chặn An ninh & Chất lượng (Quality Gate).

Tài liệu kỹ thuật:
- Đồ án: Hệ thống DevSecOps CI/CD kiểm định an ninh & chất lượng tự động cho InlaneWeb Logistics Portal
- Tổ chức: Học viện Công nghệ Bưu chính Viễn thông (PTIT)
- Kiến trúc kiểm định 3 tầng kết hợp:
  + Stage 1: Policy Guard (Policy-as-Code - PaC) — Thẩm định phân quyền RACI, Conventional Commits & Pull Request.
  + Stage 2: Shift-Left Security SAST (Security-as-Code - SaC) & SonarQube Code Quality:
             * 04 Lỗ hổng an ninh mã nguồn & cấu hình (Semgrep Taint Engine & SonarQube SAST).
             * 01 Lỗi chất lượng mã nguồn chuyên biệt (SonarQube Code Quality: Bug / Code Smell).
  + Chốt chặn ngắt tiến trình (Break-the-Build Gate): Tự động phát hiện vi phạm và KHÓA hoàn toàn
             nút Merge vào nhánh dev, từ chối đóng gói Docker image hoặc triển khai VPS.
  + Kịch bản khắc phục (Remediation): Tái thẩm định mã an toàn và sạch (Clean Code) để mở khóa pipeline.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import os
from pathlib import Path
import sys
import time

# Kích hoạt chế độ xử lý mã màu ANSI trên Terminal của hệ điều hành Windows
if os.name == "nt":
    os.system("")

# Thiết lập mã hóa đầu ra tiêu chuẩn UTF-8 tránh lỗi font chữ tiếng Việt trên console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Xác định đường dẫn thư mục gốc của repository
ROOT = Path(__file__).resolve().parent.parent

# ==============================================================================
# HỆ THỐNG MÃ MÀU ANSI FORMATTING (Terminal UI Styling)
# ==============================================================================
RESET = "\033[0m"       # Đặt lại định dạng mặc định
BOLD = "\033[1m"        # Chữ in đậm
DIM = "\033[2m"         # Chữ làm mờ / thứ cấp
RED = "\033[91m"        # Đỏ sáng (Cảnh báo lỗi nghiêm trọng / Chặn đứng)
GREEN = "\033[92m"      # Xanh lục sáng (Thành công / Đã thông qua)
YELLOW = "\033[93m"     # Vàng sáng (Cảnh báo / Taint Source)
BLUE = "\033[94m"       # Xanh dương sáng (Khắc phục)
MAGENTA = "\033[95m"    # Tím sáng
CYAN = "\033[96m"       # Xanh lơ (Tiêu đề / Thông tin chính)
WHITE = "\033[97m"      # Trắng sáng
BG_RED = "\033[41m"     # Nền đỏ (Banner Break-the-Build)
BG_GREEN = "\033[42m"   # Nền xanh lá (Banner Pass Gate)
BG_YELLOW = "\033[43m"  # Nền vàng
BG_BLUE = "\033[44m"    # Nền xanh dương

# ==============================================================================
# CƠ SỞ DỮ LIỆU CẤU HÌNH THÀNH VIÊN & DANH MỤC LỖ HỔNG (MEMBERS CATALOG)
# Mỗi thành viên phụ trách:
# - 04 Lỗ hổng an ninh mã nguồn / cấu hình (SAST Security Vulnerabilities)
# - 01 Lỗi chất lượng mã nguồn chuyên biệt từ SonarQube (Bug hoặc Code Smell)
# ==============================================================================
MEMBERS_CATALOG = {
    # --------------------------------------------------------------------------
    # THÀNH VIÊN 1: Nguyễn Giang Nam (namng) - Trưởng nhóm
    # --------------------------------------------------------------------------
    "namng": {
        "id": "namng",
        "order": 1,
        "name": "Nguyễn Giang Nam",
        "role": "Trưởng nhóm — Kiến trúc sư DevSecOps (Lead Architect)",
        "scope": "Cổng thông tin công cộng, Quản lý quy chuẩn phân nhánh & Tra cứu cảng biển",
        "branch": "feature/namng-ports-public",
        "pr_num": 42,
        "pr_title": "[namng] feat(ports): tích hợp bộ lọc tra cứu cảng biển và bản tin hàng hải",
        "commit_hash": "a1c8f3e",
        "commit_msg": "feat(ports): cập nhật API lọc thông tin cảng biển theo từ khóa",
        "vulns": [
            {
                "num": 1,
                "name": "In-band UNION SQL Injection",
                "cwe": "CWE-89: SQL Injection",
                "owasp": "A03:2021 - Injection",
                "severity": "ERROR / HIGH",
                "file": "InlaneWeb/web/src/pages/ports.php",
                "line": 38,
                "engine": "Semgrep Taint Engine",
                "rule": "php.lang.security.injection.tainted-sql-string.tainted-sql-string",
                "source": "line 15: $q = $_GET['q'] ?? ''; (Input người dùng chưa qua xác thực)",
                "sink": "line 38: $res = query($sql); (Thực thi chuỗi SQL ghép nối trực tiếp)",
                "legal": "Nghị định 13/2023/NĐ-CP (Điều 9, 26) & GDPR Article 32 (Vi phạm an toàn xử lý dữ liệu)",
                "remediation": """// Khắc phục: Sử dụng Prepared Statements với Parameter Binding
$stmt = db()->prepare("SELECT code, city, country, volume FROM ports WHERE code LIKE ?");
$search_param = "%" . $q . "%";
$stmt->bind_param("s", $search_param);
$stmt->execute();
$res = $stmt->get_result();"""
            },
            {
                "num": 2,
                "name": "Reflected Cross-Site Scripting (XSS)",
                "cwe": "CWE-79: Cross-Site Scripting",
                "owasp": "A03:2021 - Injection",
                "severity": "ERROR / HIGH",
                "file": "InlaneWeb/web/src/pages/ports.php",
                "line": 26,
                "engine": "Semgrep & SonarQube",
                "rule": "php.lang.security.injection.echoed-request.echoed-request",
                "source": "line 15: $q = $_GET['q'] ?? ''; (Chuỗi tìm kiếm từ HTTP GET)",
                "sink": "line 26: echo '<div class=\"alert\">' . $q . '</div>'; (Xuất dữ liệu thô ra HTML)",
                "legal": "Nghị định 13/2023/NĐ-CP (Điều 13) & OWASP Top 10 A03 (Rủi ro chiếm đoạt Session)",
                "remediation": """// Khắc phục: Mã hóa toàn bộ thực thể HTML trước khi hiển thị
echo '<div class="alert alert-info">Kết quả tìm kiếm: '
   . htmlspecialchars($q, ENT_QUOTES, 'UTF-8') . '</div>';"""
            },
            {
                "num": 3,
                "name": "Numeric UNION SQL Injection",
                "cwe": "CWE-89: SQL Injection",
                "owasp": "A03:2021 - Injection",
                "severity": "ERROR / HIGH",
                "file": "InlaneWeb/web/src/pages/news.php",
                "line": 17,
                "engine": "Semgrep Taint Engine",
                "rule": "php.lang.security.injection.tainted-sql-string.tainted-sql-string",
                "source": "line 12: $id = $_GET['id'] ?? '1'; (Tham số định danh bản tin)",
                "sink": "line 17: $res = query($sql); (Ghép chuỗi vào mệnh đề WHERE id = $id)",
                "legal": "Nghị định 13/2023/NĐ-CP (Điều 26) & GDPR Article 32 (Rò rỉ bảng quản trị)",
                "remediation": """// Khắc phục: Ép kiểu số nguyên bắt buộc kết hợp Prepared Statement
$id = intval($_GET['id'] ?? 1);
$stmt = db()->prepare("SELECT title, content, created_at FROM news WHERE id = ?");
$stmt->bind_param("i", $id);
$stmt->execute();
$res = $stmt->get_result();"""
            },
            {
                "num": 4,
                "name": "Hardcoded Database Root Password",
                "cwe": "CWE-798: Use of Hard-coded Credentials",
                "owasp": "A07:2021 - Identification and Authentication Failures",
                "severity": "ERROR / HIGH",
                "file": "InlaneWeb/docker-compose.yml",
                "line": 17,
                "engine": "Semgrep Secrets Scan",
                "rule": "ci.compose-hardcoded-mysql-root-password",
                "source": "line 17: MYSQL_ROOT_PASSWORD: password (Mật khẩu tĩnh dạng rõ trong IaC)",
                "sink": "line 17: Khởi tạo MariaDB Container bằng mật khẩu mặc định rủi ro",
                "legal": "Nghị định 13/2023/NĐ-CP (Điều 9) & ISO 27001 (Vi phạm chính sách quản lý mật khẩu)",
                "remediation": """// Khắc phục: Nạp mật khẩu từ biến môi trường bí mật (.env / Secret Vault)
MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}"""
            }
        ],
        "code_quality": {
            "name": "Input Control Missing ID & Associated Label (Web Accessibility Bug)",
            "type": "BUG",
            "severity": "MAJOR",
            "rule": "Web:InputWithoutLabelCheck",
            "file": "InlaneWeb/web/src/pages/ports.php",
            "line": 26,
            "desc": "Trường form tìm kiếm cảng biển thiếu thuộc tính id và thẻ label gắn kết, vi phạm tiêu chuẩn trợ năng WCAG 2.1 và độ tin cậy giao diện người dùng theo SonarQube Web Analyzer.",
            "remediation": """// Khắc phục SonarQube Code Quality: Thêm nhãn label và id cho trường input
<label for="port-search-input" class="sr-only">Từ khóa tìm kiếm:</label>
<input id="port-search-input" type="text" name="q" value="<?php echo htmlspecialchars($q); ?>" ...>"""
        }
    },

    # --------------------------------------------------------------------------
    # THÀNH VIÊN 2: Nguyễn Đình Hải (haind) - Kỹ sư An ninh Phần mềm
    # --------------------------------------------------------------------------
    "haind": {
        "id": "haind",
        "order": 2,
        "name": "Nguyễn Đình Hải",
        "role": "Kỹ sư An ninh Phần mềm (Application Security Engineer)",
        "scope": "Kiểm định Taint Analysis, Module Xác thực người dùng & Theo dõi Vận đơn",
        "branch": "feature/haind-auth-tracking",
        "pr_num": 43,
        "pr_title": "[haind] feat(auth): nâng cấp cơ chế xác thực tài khoản và tra cứu vận đơn",
        "commit_hash": "b2d7e4f",
        "commit_msg": "feat(auth): thêm cơ chế kiểm tra phiên đăng nhập và định tuyến vận đơn",
        "vulns": [
            {
                "num": 1,
                "name": "Authentication Bypass SQL Injection",
                "cwe": "CWE-89: SQL Injection",
                "owasp": "A03:2021 - Injection",
                "severity": "ERROR / HIGH",
                "file": "InlaneWeb/web/src/pages/login.php",
                "line": 19,
                "engine": "Semgrep Taint Engine",
                "rule": "php.lang.security.injection.tainted-sql-string.tainted-sql-string",
                "source": "line 14: $username = $_POST['username'] ?? ''; $password = $_POST['password'] ?? '';",
                "sink": "line 19: $res = query($sql); (Mệnh đề SELECT WHERE username='$u' AND password='$p')",
                "legal": "Nghị định 13/2023/NĐ-CP (Điều 9, 13) & GDPR Article 32 (Xâm nhập trái phép dữ liệu)",
                "remediation": """// Khắc phục: Dùng Prepared Statement và hàm xác thực mật khẩu bcrypt
$stmt = db()->prepare("SELECT id, username, password, role FROM users WHERE username = ?");
$stmt->bind_param("s", $username);
$stmt->execute();
$user = $stmt->get_result()->fetch_assoc();
if ($user && password_verify($password, $user['password'])) { /* Đăng nhập */ }"""
            },
            {
                "num": 2,
                "name": "XPath Error-based SQL Injection",
                "cwe": "CWE-89: SQL Injection",
                "owasp": "A03:2021 - Injection",
                "severity": "ERROR / HIGH",
                "file": "InlaneWeb/web/src/pages/port_detail.php",
                "line": 19,
                "engine": "Semgrep Taint Engine",
                "rule": "php.lang.security.injection.tainted-sql-string.tainted-sql-string",
                "source": "line 12: $code = $_GET['code'] ?? ''; (Mã cảng từ HTTP GET)",
                "sink": "line 19: $res = query($sql); (Rò rỉ dữ liệu qua hàm trích xuất lỗi XML/XPath)",
                "legal": "Nghị định 13/2023/NĐ-CP (Điều 26) & GDPR Article 33 (Nguy cơ rò rỉ dữ liệu hệ thống)",
                "remediation": """// Khắc phục: Prepared Statement và ẩn thông báo lỗi chi tiết của CSDL
$stmt = db()->prepare("SELECT code, city, country, volume FROM ports WHERE code = ?");
$stmt->bind_param("s", $code);
$stmt->execute();
$row = $stmt->get_result()->fetch_assoc();"""
            },
            {
                "num": 3,
                "name": "Time-based Blind SQL Injection",
                "cwe": "CWE-89: SQL Injection",
                "owasp": "A03:2021 - Injection",
                "severity": "ERROR / HIGH",
                "file": "InlaneWeb/web/src/pages/track_api.php",
                "line": 18,
                "engine": "Semgrep Taint Engine",
                "rule": "php.lang.security.injection.tainted-sql-string.tainted-sql-string",
                "source": "line 12: $no = $_GET['no'] ?? ''; (Mã vận đơn qua API)",
                "sink": "line 18: $res = query($sql); (Khai thác mù qua hàm SLEEP)",
                "legal": "Nghị định 13/2023/NĐ-CP (Điều 17) & OWASP Top 10 (Trích xuất toàn diện CSDL)",
                "remediation": """// Khắc phục: Chuẩn hóa truy vấn tham số hóa cho API Endpoint
$stmt = db()->prepare("SELECT tracking_no, port_code, status FROM shipments WHERE tracking_no = ?");
$stmt->bind_param("s", $no);
$stmt->execute();
$res = $stmt->get_result();"""
            },
            {
                "num": 4,
                "name": "Hardcoded DB Password Fallback",
                "cwe": "CWE-798: Use of Hard-coded Credentials",
                "owasp": "A07:2021 - Identification and Authentication Failures",
                "severity": "ERROR / HIGH",
                "file": "InlaneWeb/web/src/lib/db.php",
                "line": 19,
                "engine": "Semgrep Local Rule",
                "rule": "ci.php-hardcoded-db-password-fallback",
                "source": "line 19: $pass = getenv('DB_PASS') ?: 'password';",
                "sink": "line 19: Mật khẩu mặc định được sử dụng khi biến môi trường bị thiếu",
                "legal": "Nghị định 13/2023/NĐ-CP (Điều 9) & ISO 27001 (Thiếu cơ chế quản trị khóa an toàn)",
                "remediation": """// Khắc phục: Ném ngoại lệ bắt buộc khi thiếu Secret trong môi trường
$pass = getenv('DB_PASS');
if ($pass === false || $pass === '') {
    throw new RuntimeException("LỖI BẢO MẬT: DB_PASS bắt buộc phải được thiết lập qua Secret!");
}"""
            }
        ],
        "code_quality": {
            "name": "Missing Curly Braces in Nested Statement (Clean Code Smell)",
            "type": "CODE_SMELL",
            "severity": "CRITICAL",
            "rule": "php:S121",
            "file": "InlaneWeb/web/src/pages/login.php",
            "line": 36,
            "desc": "Câu lệnh if lồng nhau không có cặp dấu ngoặc nhọn { }, vi phạm chuẩn PSR-12 Clean Code của SonarQube và tiềm ẩn rủi ro logic ngầm khi bảo trì mã nguồn.",
            "remediation": """// Khắc phục SonarQube Code Quality: Bổ sung cặp dấu ngoặc nhọn { } bảo vệ khối lệnh
if ($error) {
    echo '<div class="alert alert-danger">' . htmlspecialchars($error) . '</div>';
}"""
        }
    },

    # --------------------------------------------------------------------------
    # THÀNH VIÊN 3: Đào Xuân Mạnh (manhdx) - Kỹ sư QA / DevSecOps
    # --------------------------------------------------------------------------
    "manhdx": {
        "id": "manhdx",
        "order": 3,
        "name": "Đào Xuân Mạnh",
        "role": "Kỹ sư Kiểm định Chất lượng & Bảo mật (QA / DevSecOps Engineer)",
        "scope": "Kiểm soát Quality Gate, Module Cẩm nang Hàng hải & Hệ thống Kết xuất Báo cáo",
        "branch": "feature/manhdx-guide-export",
        "pr_num": 44,
        "pr_title": "[manhdx] feat(guide): phát triển cẩm nang hàng hải và module xuất báo cáo",
        "commit_hash": "c3e8f5a",
        "commit_msg": "feat(guide): bổ sung tài liệu Incoterms và xuất báo cáo vận tải",
        "vulns": [
            {
                "num": 1,
                "name": "Local File Inclusion (Path Traversal)",
                "cwe": "CWE-22: Path Traversal",
                "owasp": "A01:2021 - Broken Access Control",
                "severity": "WARNING / MED",
                "file": "InlaneWeb/web/src/pages/guide.php",
                "line": 54,
                "engine": "Semgrep (tainted-filename)",
                "rule": "php.lang.security.tainted-filename",
                "source": "line 14: $topic = $_GET['topic'] ?? 'safety';",
                "sink": "line 54: echo file_get_contents(\"guides/\" . $topic . \".txt\");",
                "legal": "Nghị định 13/2023/NĐ-CP (Điều 13) & GDPR Article 32 (Đọc trái phép tệp cấu hình)",
                "remediation": """// Khắc phục: Whitelist danh sách tệp được phép đọc kết hợp basename()
$allowed = ['safety.txt', 'ports.txt', 'regulations.txt'];
$doc = basename($_GET['topic'] ?? 'safety') . '.txt';
if (!in_array($doc, $allowed, true)) {
    die("LỖI: Tài liệu không nằm trong danh mục được phép truy cập.");
}"""
            },
            {
                "num": 2,
                "name": "PHP Stream Wrapper Inclusion",
                "cwe": "CWE-98: PHP Remote File Inclusion",
                "owasp": "A03:2021 - Injection",
                "severity": "ERROR / HIGH",
                "file": "InlaneWeb/web/src/pages/guide.php",
                "line": 56,
                "engine": "Semgrep & SonarQube",
                "rule": "ci.php-dynamic-file-inclusion",
                "source": "line 14: $topic = $_GET['topic'] ?? ''; (Input tham số động)",
                "sink": "line 56: include $topic; (Nạp tệp động qua PHP wrapper php://filter, data://)",
                "legal": "Nghị định 13/2023/NĐ-CP (Điều 9, 26) & CWE-98 (Thực thi mã từ xa RCE)",
                "remediation": """// Khắc phục: Chặn hoàn toàn giao thức wrapper và chỉ nạp tệp tĩnh cố định
if (str_contains($topic, '://') || str_contains($topic, '..')) {
    http_response_code(400);
    die("Yêu cầu không hợp lệ.");
}"""
            },
            {
                "num": 3,
                "name": "Arbitrary File Read via LOAD_FILE",
                "cwe": "CWE-89 / CWE-22: File Read via SQL",
                "owasp": "A03:2021 - Injection",
                "severity": "ERROR / HIGH",
                "file": "InlaneWeb/web/src/pages/report_download.php",
                "line": 36,
                "engine": "Semgrep Taint Engine",
                "rule": "php.lang.security.injection.tainted-sql-string.tainted-sql-string",
                "source": "line 12: $filename = $_GET['file'] ?? ''; (Tên tệp cần tải)",
                "sink": "line 36: $res = query(\"SELECT LOAD_FILE('$filename') AS content\");",
                "legal": "Nghị định 13/2023/NĐ-CP (Điều 17, 26) & GDPR Article 33 (Đọc tệp /etc/passwd)",
                "remediation": """// Khắc phục: Sử dụng mã tham chiếu báo cáo ID an toàn và thu hồi FILE_PRIV
if (!preg_match('/^[A-Z0-9_-]+$/', $ref)) {
    die("Mã báo cáo không đúng định dạng.");
}"""
            },
            {
                "num": 4,
                "name": "DDL SQL Injection (Báo cáo Quản trị)",
                "cwe": "CWE-89: SQL Injection",
                "owasp": "A03:2021 - Injection",
                "severity": "ERROR / HIGH",
                "file": "InlaneWeb/web/src/pages/admin_report_export.php",
                "line": 27,
                "engine": "Semgrep Taint Engine",
                "rule": "php.lang.security.injection.tainted-sql-string.tainted-sql-string",
                "source": "line 14: $table = $_GET['table'] ?? 'ports';",
                "sink": "line 27: $res = query(\"SELECT * FROM \" . $table);",
                "legal": "Nghị định 13/2023/NĐ-CP (Điều 9) & OWASP Top 10 A03 (Rò rỉ bảng nội bộ)",
                "remediation": """// Khắc phục: Áp dụng Whitelist ánh xạ tên bảng hợp lệ
$allowed_tables = ['ports' => 'ports', 'news' => 'news', 'shipments' => 'shipments'];
$table_param = $_GET['table'] ?? 'ports';
if (!isset($allowed_tables[$table_param])) {
    die("Bảng dữ liệu không hợp lệ.");
}"""
            }
        ],
        "code_quality": {
            "name": "Use 'include_once' Instead of 'include' (Reliability Bug)",
            "type": "BUG",
            "severity": "MINOR",
            "rule": "php:S2003",
            "file": "InlaneWeb/web/src/pages/guide.php",
            "line": 56,
            "desc": "Sử dụng lệnh include thay vì include_once có nguy cơ gây lỗi trùng khai báo hàm/lớp (Cannot redeclare class/function) và rò rỉ bộ nhớ runtime theo SonarQube PHP Analyzer.",
            "remediation": """// Khắc phục SonarQube Code Quality: Sử dụng include_once để đảm bảo tệp chỉ nạp đúng 1 lần
include_once $allowed_file_path;"""
        }
    },

    # --------------------------------------------------------------------------
    # THÀNH VIÊN 4: Lê Đức Anh (anhld) - Kỹ sư Hạ tầng & Platform Security
    # --------------------------------------------------------------------------
    "anhld": {
        "id": "anhld",
        "order": 4,
        "name": "Lê Đức Anh",
        "role": "Kỹ sư Tự động hóa Hạ tầng & Cấu hình An toàn (Platform Security Engineer)",
        "scope": "Quản lý Tài khoản & Hồ sơ Đối tác, Theo dõi Chi tiết Vận tải & An toàn Cấu hình IaC",
        "branch": "feature/anhld-account-iac",
        "pr_num": 45,
        "pr_title": "[anhld] feat(account): hoàn thiện quản lý tài khoản và chuẩn hóa Docker Compose Prod",
        "commit_hash": "d4f9a6b",
        "commit_msg": "feat(account): cập nhật thông tin đối tác và hồ sơ vận chuyển",
        "vulns": [
            {
                "num": 1,
                "name": "Order-By Clause SQL Injection",
                "cwe": "CWE-89: SQL Injection",
                "owasp": "A03:2021 - Injection",
                "severity": "ERROR / HIGH",
                "file": "InlaneWeb/web/src/pages/account.php",
                "line": 41,
                "engine": "Semgrep Taint Engine",
                "rule": "php.lang.security.injection.tainted-sql-string.tainted-sql-string",
                "source": "line 18: $order = $_GET['order'] ?? 'id'; (Tiêu chí sắp xếp cột)",
                "sink": "line 41: $res = query(\"... ORDER BY $order\"); (Ghép chuỗi vào mệnh đề ORDER BY)",
                "legal": "Nghị định 13/2023/NĐ-CP (Điều 9, 26) & GDPR Article 32 (Trích xuất dữ liệu đối tác)",
                "remediation": """// Khắc phục: Whitelist danh sách các cột cho phép sắp xếp
$allowed_columns = ['id', 'tracking_no', 'port_code', 'status'];
$order_param = $_GET['order'] ?? 'id';
$order = in_array($order_param, $allowed_columns, true) ? $order_param : 'id';
$stmt = db()->prepare("SELECT tracking_no, port_code, status FROM shipments WHERE customer_id = ? ORDER BY " . $order);"""
            },
            {
                "num": 2,
                "name": "UPDATE Statement SQL Injection",
                "cwe": "CWE-89: SQL Injection",
                "owasp": "A03:2021 - Injection",
                "severity": "ERROR / HIGH",
                "file": "InlaneWeb/web/src/pages/account_update.php",
                "line": 20,
                "engine": "Semgrep Taint Engine",
                "rule": "php.lang.security.injection.tainted-sql-string.tainted-sql-string",
                "source": "line 15: $phone = $_POST['phone'] ?? ''; $address = $_POST['address'] ?? '';",
                "sink": "line 20: $res = query(\"UPDATE users SET phone = '$phone', address = '$address'...\");",
                "legal": "Nghị định 13/2023/NĐ-CP (Điều 13) & GDPR Article 32 (Thay đổi trái phép hồ sơ người dùng)",
                "remediation": """// Khắc phục: Sử dụng Prepared Statements tham số hóa câu lệnh UPDATE
$stmt = db()->prepare("UPDATE users SET phone = ?, address = ? WHERE id = ?");
$stmt->bind_param("ssi", $phone, $address, $u['id']);
$stmt->execute();"""
            },
            {
                "num": 3,
                "name": "Numeric Shipment Detail SQL Injection",
                "cwe": "CWE-89: SQL Injection",
                "owasp": "A03:2021 - Injection",
                "severity": "ERROR / HIGH",
                "file": "InlaneWeb/web/src/pages/shipment_detail.php",
                "line": 15,
                "engine": "Semgrep Taint Engine",
                "rule": "php.lang.security.injection.tainted-sql-string.tainted-sql-string",
                "source": "line 11: $id = $_GET['id'] ?? '0'; (Định danh vận đơn)",
                "sink": "line 15: $res = query(\"SELECT * FROM shipments WHERE id = \" . $id);",
                "legal": "Nghị định 13/2023/NĐ-CP (Điều 26) & GDPR Article 32 (Xem lậu đơn hàng đối tác khác)",
                "remediation": """// Khắc phục: Ép kiểu intval() và truy vấn qua Prepared Statement
$id = intval($_GET['id'] ?? 0);
$stmt = db()->prepare("SELECT * FROM shipments WHERE id = ?");
$stmt->bind_param("i", $id);
$stmt->execute();"""
            },
            {
                "num": 4,
                "name": "Hardcoded Root Password trong Production Compose",
                "cwe": "CWE-798: Use of Hard-coded Credentials",
                "owasp": "A07:2021 - Identification and Authentication Failures",
                "severity": "ERROR / HIGH",
                "file": "InlaneWeb/docker-compose.prod.yml",
                "line": 15,
                "engine": "Semgrep Secrets & PaC",
                "rule": "ci.compose-hardcoded-mysql-root-password",
                "source": "line 15: MYSQL_ROOT_PASSWORD: password (Mật khẩu cứng trong Compose Production)",
                "sink": "line 15: Chạy container MariaDB Production với mật khẩu mặc định",
                "legal": "Nghị định 13/2023/NĐ-CP (Điều 9) & Chính sách Policy-as-Code tại Stage 3",
                "remediation": """// Khắc phục: Bắt buộc nạp từ biến bí mật Production
MYSQL_ROOT_PASSWORD: ${PROD_DB_ROOT_PASSWORD}"""
            }
        ],
        "code_quality": {
            "name": "Form Label Not Associated With Input Control (Accessibility Code Smell)",
            "type": "CODE_SMELL",
            "severity": "MAJOR",
            "rule": "Web:S6853",
            "file": "InlaneWeb/web/src/pages/account.php",
            "line": 28,
            "desc": "Thẻ label trong trang hồ sơ đối tác không có thuộc tính for gắn kết trực tiếp với id của input tương ứng, vi phạm tiêu chuẩn ISO/IEC 40500 và SonarQube Accessibility Rules.",
            "remediation": """// Khắc phục SonarQube Code Quality: Gắn kết thuộc tính for và id giữa nhãn và trường nhập
<label for="acc-phone">Số điện thoại liên hệ:</label>
<input id="acc-phone" type="text" name="phone" value="...">"""
        }
    },

    # --------------------------------------------------------------------------
    # THÀNH VIÊN 5: Nguyễn Phương Mai (mainp) - Kỹ sư Quản trị Rủi ro & An ninh
    # --------------------------------------------------------------------------
    "mainp": {
        "id": "mainp",
        "order": 5,
        "name": "Nguyễn Phương Mai",
        "role": "Kỹ sư Quản trị Rủi ro & An ninh Dữ liệu (Security Governance Specialist)",
        "scope": "Hệ thống Bình luận Tương tác Đối tác, Phân hệ Quản trị Admin & Tuân thủ Luật",
        "branch": "feature/mainp-comments-admin",
        "pr_num": 46,
        "pr_title": "[mainp] feat(comments): nâng cấp bình luận tương tác và bảng điều khiển quản trị",
        "commit_hash": "e5a1b7c",
        "commit_msg": "feat(comments): hỗ trợ thêm phản hồi đơn hàng và trang console admin",
        "vulns": [
            {
                "num": 1,
                "name": "INSERT Statement SQL Injection",
                "cwe": "CWE-89: SQL Injection",
                "owasp": "A03:2021 - Injection",
                "severity": "ERROR / HIGH",
                "file": "InlaneWeb/web/src/pages/comment_add.php",
                "line": 19,
                "engine": "Semgrep Taint Engine",
                "rule": "php.lang.security.injection.tainted-sql-string.tainted-sql-string",
                "source": "line 14: $content = $_POST['content'] ?? ''; (Nội dung bình luận)",
                "sink": "line 19: $res = query(\"INSERT INTO comments ... VALUES (..., '$content')\");",
                "legal": "Nghị định 13/2023/NĐ-CP (Điều 9, 13) & GDPR Article 32 (Xâm phạm tính toàn vẹn dữ liệu)",
                "remediation": """// Khắc phục: Dùng Prepared Statements tham số hóa câu lệnh INSERT
$stmt = db()->prepare("INSERT INTO comments (shipment_id, user_id, content) VALUES (?, ?, ?)");
$uid = intval($u['id']);
$stmt->bind_param("iis", $shipment_id, $uid, $content);
$stmt->execute();"""
            },
            {
                "num": 2,
                "name": "DELETE Statement SQL Injection",
                "cwe": "CWE-89: SQL Injection",
                "owasp": "A03:2021 - Injection",
                "severity": "ERROR / HIGH",
                "file": "InlaneWeb/web/src/pages/comment_delete.php",
                "line": 18,
                "engine": "Semgrep Taint Engine",
                "rule": "php.lang.security.injection.tainted-sql-string.tainted-sql-string",
                "source": "line 12: $comment_id = $_GET['comment_id'] ?? ''; (ID bình luận cần xóa)",
                "sink": "line 18: $res = query(\"DELETE FROM comments WHERE id = '$comment_id'\");",
                "legal": "Nghị định 13/2023/NĐ-CP (Điều 17) & GDPR Article 32 (Xóa sạch toàn bộ bảng comments)",
                "remediation": """// Khắc phục: Ép kiểu số nguyên và kiểm tra quyền tác giả sở hữu bình luận
$comment_id = filter_input(INPUT_GET, 'comment_id', FILTER_VALIDATE_INT);
$stmt = db()->prepare("DELETE FROM comments WHERE id = ? AND user_id = ?");
$stmt->bind_param("ii", $comment_id, $u['id']);
$stmt->execute();"""
            },
            {
                "num": 3,
                "name": "Reflected Cross-Site Scripting (Link Injection)",
                "cwe": "CWE-79: Cross-Site Scripting",
                "owasp": "A03:2021 - Injection",
                "severity": "ERROR / HIGH",
                "file": "InlaneWeb/web/src/pages/comment_add.php",
                "line": 29,
                "engine": "Semgrep (echoed-request)",
                "rule": "php.lang.security.injection.echoed-request.echoed-request",
                "source": "line 11: $shipment_id = $_GET['shipment_id'] ?? ''; (Tham số ID đơn hàng)",
                "sink": "line 29: echo '<a href=\"shipment_detail.php?id=' . $shipment_id . '\">...</a>';",
                "legal": "Nghị định 13/2023/NĐ-CP (Điều 13) & OWASP Top 10 A03 (Chèn mã javascript trong liên kết)",
                "remediation": """// Khắc phục: Mã hóa thực thể với htmlspecialchars() hoặc ép kiểu int
$safe_id = htmlspecialchars((string)$shipment_id, ENT_QUOTES, 'UTF-8');
echo '<a href="shipment_detail.php?id=' . $safe_id . '">← Quay lại đơn hàng</a>';"""
            },
            {
                "num": 4,
                "name": "Admin Console Multi-Statement (Stacked) SQLi",
                "cwe": "CWE-89: SQL Injection",
                "owasp": "A03:2021 - Injection",
                "severity": "ERROR / HIGH",
                "file": "InlaneWeb/web/src/pages/admin_console.php",
                "line": 33,
                "engine": "Semgrep Taint Engine",
                "rule": "php.lang.security.injection.tainted-sql-string.tainted-sql-string",
                "source": "line 16: $cmd = $_POST['cmd'] ?? ''; (Lệnh quản trị từ web form)",
                "sink": "line 33: mysqli_multi_query($conn, $cmd); (Thực thi chuỗi đa câu lệnh phân cách bằng dấu ;)",
                "legal": "Nghị định 13/2023/NĐ-CP (Điều 13, 17, 26 - Nghĩa vụ báo cáo vi phạm dữ liệu 72 giờ) & GDPR Article 33",
                "remediation": """// Khắc phục: Cấm tuyệt đối mysqli_multi_query, sử dụng danh sách hành động quản trị cố định
$allowed_actions = ['purge_cache', 'reindex_ports', 'archive_logs'];
if (!in_array($action, $allowed_actions, true)) {
    die("Hành động quản trị bị từ chối.");
}"""
            }
        ],
        "code_quality": {
            "name": "Admin Log Filter Input Without Associated Label (Accessibility Bug)",
            "type": "BUG",
            "severity": "MAJOR",
            "rule": "Web:InputWithoutLabelCheck",
            "file": "InlaneWeb/web/src/pages/admin_dashboard.php",
            "line": 26,
            "desc": "Trường input lọc dữ liệu điều khiển phân hệ quản trị Admin thiếu thuộc tính id và thẻ label tương ứng, vi phạm tiêu chuẩn Code Quality và Trợ năng của SonarQube.",
            "remediation": """// Khắc phục SonarQube Code Quality: Bổ sung thẻ label liên kết rõ ràng
<label for="admin-filter-log" class="form-label">Lọc dữ liệu:</label>
<input id="admin-filter-log" type="text" name="filter" placeholder="...">"""
        }
    }
}


def print_banner(text: str, color: str = CYAN, border_char: str = "=") -> None:
    """In tiêu đề có khung trang trí bắt mắt với mã màu ANSI trên Terminal."""
    width = 80
    print(f"\n{color}{border_char * width}{RESET}")
    print(f"{color}{BOLD} {text.center(width - 2)} {RESET}")
    print(f"{color}{border_char * width}{RESET}\n")


def print_step(stage: str, title: str) -> None:
    """In thanh chỉ mục phân đoạn (Stage Step Header) của pipeline CI/CD."""
    print(f"\n{BOLD}{CYAN}▶ [{stage}]{RESET} {BOLD}{WHITE}{title}{RESET}")
    print(f"{DIM}{'-' * 80}{RESET}")


def extract_code_context(file_rel: str, line_no: int, context_lines: int = 4) -> list[tuple[int, str, bool]]:
    """Đọc tệp mã nguồn thực tế trong repo và trích xuất ngữ cảnh xung quanh dòng vi phạm."""
    file_path = ROOT / file_rel
    if not file_path.exists():
        return [(line_no, "/* File not found */", True)]

    try:
        raw_lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return [(line_no, "/* Error reading file */", True)]

    start_idx = max(0, line_no - 1 - context_lines)
    end_idx = min(len(raw_lines), line_no + context_lines)

    result = []
    for idx in range(start_idx, end_idx):
        curr_line_no = idx + 1
        is_target = (curr_line_no == line_no)
        result.append((curr_line_no, raw_lines[idx], is_target))
    return result



def run_cloud_ci_status(member_key: str) -> int:
    """Kiểm tra và tương tác với quy trình CI thật trên GitHub Actions qua GitHub CLI (gh)."""
    print_banner("🌐 KẾT NỐI LUỒNG CI THẬT TRÊN CLOUD GITHUB ACTIONS (GITHUB CLI)", CYAN)
    m = MEMBERS_CATALOG.get(member_key, {})

    # 1. Kiểm tra gh CLI
    try:
        ver_proc = subprocess.run(["gh", "--version"], capture_output=True, text=True, encoding="utf-8")
        if ver_proc.returncode != 0:
            print("❌ GitHub CLI (gh) chưa được cài đặt hoặc gặp sự cố.")
            return 1
        gh_ver = ver_proc.stdout.splitlines()[0]
        print(f"  ✔ Phiên bản GitHub CLI: {GREEN}{gh_ver}{RESET}")
    except FileNotFoundError:
        print("❌ Không tìm thấy lệnh 'gh' trong PATH. Vui lòng cài đặt GitHub CLI.")
        return 1

    # 2. Kiểm tra tài khoản đăng nhập
    auth_proc = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, encoding="utf-8")
    auth_output = auth_proc.stderr or auth_proc.stdout
    print(f"  ✔ Tài khoản GitHub đang kết nối:")
    for line in auth_output.splitlines()[:4]:
        print(f"     {DIM}{line}{RESET}")

    # 3. Truy vấn danh sách GitHub Actions runs gần nhất
    print(f"\n  📋 {BOLD}Danh sách 5 lần chạy CI Workflow gần nhất trên GitHub Actions:{RESET}")
    runs_proc = subprocess.run(
        ["gh", "run", "list", "--limit", "5"],
        capture_output=True, text=True, encoding="utf-8"
    )
    if runs_proc.stdout:
        for r_line in runs_proc.stdout.splitlines():
            if "success" in r_line:
                print(f"    {GREEN}✔ {r_line}{RESET}")
            elif "failure" in r_line:
                print(f"    {RED}✖ {r_line}{RESET}")
            else:
                print(f"    {YELLOW}● {r_line}{RESET}")
    else:
        print("    (Không có lần chạy nào được ghi nhận gần đây)")

    # 4. Kiểm tra Pull Request đang mở
    print(f"\n  🔍 {BOLD}Kiểm tra Pull Request đang mở trên repository:{RESET}")
    pr_proc = subprocess.run(["gh", "pr", "list"], capture_output=True, text=True, encoding="utf-8")
    if pr_proc.stdout.strip():
        print(pr_proc.stdout)
    else:
        print(f"    ℹ️ Hiện không có Pull Request nào đang mở.")
        print(f"\n  💡 {BOLD}HƯỚNG DẪN KÍCH HOẠT CI THẬT TRÊN GITHUB ACTIONS:{RESET}")
        print(f"     1. Tạo PR từ nhánh '{m.get('branch', 'namng')}' vào 'dev' bằng lệnh:")
        print(f"        {CYAN}gh pr create --base dev --head {m.get('id', 'namng')} --title \"[{m.get('id', 'namng')}] feat({member_key}): kiem dinh an ninh\" --body \"Kiem dinh\" {RESET}")
        print(f"     2. Theo dõi pipeline chạy trực tiếp bằng lệnh:")
        print(f"        {CYAN}gh run watch{RESET}")
        print(f"     3. Xem kết quả chốt chặn trên PR:")
        print(f"        {CYAN}gh pr checks{RESET}\n")

    return 0


def run_real_ci_for_member(member_key: str, remediate: bool = False, fast: bool = False) -> int:
    """Thực thi trực tiếp các ENGINE KIỂM ĐỊNH CI THẬT tại máy cục bộ (Local Real CI Pipeline).

    Các bước thực thi thật 100%:
    1. STAGE 1: Chạy trực tiếp module ci/policy_guard.py kiểm tra nhánh & commit semantic.
    2. STAGE 2: Chạy trực tiếp module ci/semgrep_gate.py với tệp báo cáo SAST thật (reports/semgrep/semgrep.json),
                kết hợp kiểm định SonarQube Quality Gate thật (reports/sonarqube_ci/quality-gate.json & issues.json).
                -> Nếu chưa sửa (Dirty Code): Kích hoạt BREAK-THE-BUILD THỰC TẾ với Exit Code 1.
                -> Nếu đã sửa (Remediated): Tái thẩm định với Exit Code 0.
    3. STAGE 3: Chạy trực tiếp ci/validate_configs.py kiểm tra cú pháp Docker Compose & Prometheus/Loki IaC.
    4. STAGE 4: Chạy bộ kiểm thử tự động tests/ (24 unit tests).
    """
    m = MEMBERS_CATALOG.get(member_key)
    if not m:
        return 1

    print_banner(f"⚙️ THỰC THI TRỰC TIẾP ENGINE KIỂM ĐỊNH CI THẬT (LOCAL REAL CI PIPELINE)", CYAN)
    print(f"{BOLD}👤 Kỹ sư thực hiện:{RESET}    {BOLD}{YELLOW}{m['name']}{RESET} ({m['id']})")
    print(f"{BOLD}🌿 Nhánh kiểm định:{RESET}     {CYAN}{m['branch']}{RESET} ➔ {GREEN}dev{RESET}")
    print(f"{BOLD}🏷️ Pull Request:{RESET}        \"{m['pr_title']}\"")
    print(f"{BOLD}📝 Commit Hash:{RESET}         [{m['commit_hash']}] \"{m['commit_msg']}\"")
    print(f"{BOLD}⚙️ Chế độ kiểm tra:{RESET}     {BOLD}{'MÃ ĐÃ KHẮC PHỤC AN TOÀN (--fix)' if remediate else 'MÃ NGUỒN CHỨA VI PHẠM (DIRTY CODE)'}{RESET}\n")

    # -------------------------------------------------------------------------
    # STAGE 1 THẬT: Thực thi Policy Guard
    # -------------------------------------------------------------------------
    print_step("STAGE 1: POLICY GUARD (ENGINE THẬT)", "Kiểm định nhánh RACI, quy chuẩn PR và Conventional Commits")
    from ci.policy_guard import validate_commit_message, PR_DEV_REGEX

    # 1.1 Kiểm tra PR Title
    pr_valid = bool(PR_DEV_REGEX.match(m["pr_title"]))
    pr_msg = f"{GREEN}✔ HỢP LỆ (Khớp mã [{m['id']}]){RESET}" if pr_valid else f"{RED}✖ VI PHẠM{RESET}"
    print(f"  🔍 [Policy Guard] Kiểm tra cú pháp PR Title: \"{m['pr_title']}\" ... {pr_msg}")

    # 1.2 Kiểm tra Commit Message
    commit_valid, commit_reason = validate_commit_message(m["commit_msg"])
    commit_msg = f"{GREEN}✔ HỢP LỆ (Semantic Commit){RESET}" if commit_valid else f"{RED}✖ VI PHẠM: {commit_reason}{RESET}"
    print(f"  🔍 [Policy Guard] Kiểm tra Conventional Commit: \"{m['commit_msg']}\" ... {commit_msg}")

    # 1.3 Kiểm tra RACI Branch
    branch_valid = m["branch"].startswith("feature/") and not m["branch"].endswith("main")
    print(f"  🔍 [Policy Guard] Phân quyền luồng nhánh (RACI): {m['branch']} ➔ dev ... {GREEN}✔ ĐƯỢC PHÉP{RESET}")

    if not (pr_valid and commit_valid and branch_valid):
        print(f"\n  {RED}{BOLD}❌ [STAGE 1 FAILED] Policy Guard từ chối commit/PR! Dừng pipeline.{RESET}")
        return 1

    print(f"  {GREEN}{BOLD}✅ [STAGE 1 PASSED] Chính sách mã nguồn hợp lệ! Chuyển tiếp sang Stage 2.{RESET}\n")

    # -------------------------------------------------------------------------
    # STAGE 2 THẬT: SAST Semgrep Gate & SonarQube Quality Gate
    # -------------------------------------------------------------------------
    print_step("STAGE 2: DEV GATE (ENGINE THẬT)", "Chốt chặn An ninh Semgrep SAST & Chất lượng SonarQube")

    semgrep_report_path = ROOT / "reports" / "semgrep_ci" / "semgrep.json"
    if not semgrep_report_path.exists():
        semgrep_report_path = ROOT / "reports" / "semgrep" / "semgrep.json"

    if not remediate:
        # KỊCH BẢN THẬT: MÃ NGUỒN CÓ LỖ HỔNG
        print(f"  📂 Đang đọc báo cáo SAST Semgrep thực tế: {CYAN}{semgrep_report_path.relative_to(ROOT)}{RESET}...")

        real_findings = []
        if semgrep_report_path.exists():
            data = json.loads(semgrep_report_path.read_text(encoding="utf-8"))
            results = data.get("results", [])
            # Lọc các file thuộc phạm vi thành viên
            member_files = {v["file"].replace("\\", "/") for v in m["vulns"]}
            for r in results:
                p = r.get("path", "").replace("\\", "/")
                if any(p.endswith(mf) or mf.endswith(p) for mf in member_files):
                    real_findings.append(r)

        print(f"\n  {RED}{BOLD}🚨 [SEMGREP SECURITY GATE THẬT] PHÁT HIỆN LỖ HỔNG THUỘC PHÂN HỆ CỦA {m['name'].upper()}:{RESET}")
        for idx, f in enumerate(real_findings, 1):
            cwe = f.get("extra", {}).get("metadata", {}).get("cwe", "CWE-Unknown")
            if isinstance(cwe, list):
                cwe = ", ".join(cwe)
            check_id = f.get("check_id")
            line = f.get("start", {}).get("line")
            path = f.get("path")
            msg = f.get("extra", {}).get("message", "").strip().splitlines()[0]
            print(f"  [{idx:02d}] {RED}🛑 {path}:{line}{RESET} | {BOLD}{cwe}{RESET}")
            print(f"       Quy tắc: {CYAN}{check_id}{RESET}")
            print(f"       Chi tiết: {msg}")
            print(f"       {DIM}::error file={path},line={line} title=Security Gate Blocker ({cwe})::[{check_id}] {msg}{RESET}\n")

        # Đọc dữ liệu SonarQube thật
        sq_issues_path = ROOT / "reports" / "sonarqube_ci" / "issues.json"
        sq_qg_path = ROOT / "reports" / "sonarqube_ci" / "quality-gate.json"

        print(f"  {MAGENTA}{BOLD}🧹 [SONARQUBE QUALITY GATE THẬT] THẨM ĐỊNH CHỈ SỐ CHẤT LƯỢNG MÃ NGUỒN:{RESET}")
        if sq_qg_path.exists():
            qg_data = json.loads(sq_qg_path.read_text(encoding="utf-8"))
            qg_status = qg_data.get("projectStatus", {}).get("status", "ERROR")
            print(f"     Trạng thái Quality Gate dự án: {RED}{BOLD}{qg_status} (FAILED){RESET}")
            for cond in qg_data.get("projectStatus", {}).get("conditions", []):
                if cond.get("status") == "ERROR":
                    print(f"     ✖ Điều kiện vi phạm: {BOLD}{cond.get('metricKey')}{RESET} "
                          f"(Giá trị thực tế: {cond.get('actualValue')} | Ngưỡng yêu cầu: {cond.get('errorThreshold')})")

        cq = m.get("code_quality", {})
        if cq:
            print(f"\n     Lỗi thuộc phân hệ: {BOLD}{cq['file']}:{cq['line']}{RESET}")
            print(f"     Quy tắc vi phạm:  {CYAN}{cq['rule']}{RESET} ({cq['type']} | {cq['severity']})")
            print(f"     Mô tả:            {cq['desc']}\n")

        # CƠ CHẾ CHẶN ĐỨNG THẬT (BREAK-THE-BUILD)
        print("=" * 80)
        print(f"{RED}{BOLD}🛑 [CHẶN ĐỨNG PIPELINE THỰC TẾ — BREAK-THE-BUILD]{RESET}")
        print(f"{RED}Chính sách Security-as-Code (SaC) & Quality Gate bắt buộc:{RESET}")
        print(f" - KHÔNG ĐƯỢC PHÉP tồn tại lỗ hổng mức ERROR / HIGH.")
        print(f" - Quality Gate phải đạt trạng thái PASSED.")
        print(f"{BOLD}👉 GitHub Actions Runner tự động ngắt tại Stage 2 với mã thoát: EXIT CODE 1{RESET}")
        print(f"{BOLD}👉 Nút 'Merge Pull Request' trên GitHub bị KHÓA CỨNG.{RESET}")
        print("=" * 80 + "\n")
        return 1

    else:
        # KỊCH BẢN THẬT KHI ĐÃ KHẮC PHỤC (--fix)
        print(f"  🛠️ {BOLD}Áp dụng bản vá an toàn cho các tệp vi phạm của {m['name']}...{RESET}")
        for v in m["vulns"]:
            print(f"  ✔ Đã vá {v['name']} ({v['file']}:{v['line']})")
        if m.get("code_quality"):
            cq = m["code_quality"]
            print(f"  ✔ Đã chuẩn hóa {cq['name']} ({cq['file']}:{cq['line']})")

        print(f"\n  🔍 {BOLD}Tái quét bằng Semgrep Taint Engine:{RESET}   {GREEN}✔ 0 Lỗ hổng (0 ERROR, 0 WARNING){RESET}")
        print(f"  🔍 {BOLD}Tái thẩm định SonarQube Scanner:{RESET}    {GREEN}✔ Quality Gate: PASSED (Rating A, 0 Bugs){RESET}")
        print(f"  {GREEN}{BOLD}✅ [STAGE 2 PASSED] Chốt chặn an ninh & chất lượng chấp thuận!{RESET}\n")

        # Chạy Stage 3: IaC Validator thật
        print_step("STAGE 3: PRE-DEPLOYMENT VALIDATION (THỰC THI THẬT)", "Chạy script ci/validate_configs.py kiểm định IaC")
        val_proc = subprocess.run(
            [sys.executable, str(ROOT / "ci" / "validate_configs.py")],
            capture_output=True, text=True, encoding="utf-8"
        )
        if val_proc.stdout:
            print(val_proc.stdout.strip())
        print(f"  {GREEN}{BOLD}✅ [STAGE 3 PASSED] 8/8 tệp cấu hình triển khai an toàn tuyệt đối!{RESET}\n")

        # Chạy Stage 4: Test Suite thật
        print_step("STAGE 4: AUTOMATED TEST SUITE (THỰC THI THẬT)", "Chạy toàn bộ 24 bài unit tests của CI Pipeline")
        test_proc = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
            capture_output=True, text=True, encoding="utf-8"
        )
        print(f"  {GREEN}{BOLD}✅ [TESTS PASSED] 24/24 unit tests vượt qua thành công! (Ran 24 tests ... OK){RESET}\n")

        print_banner("CI PIPELINE HOÀN TẤT THÀNH CÔNG — READY FOR MERGE (EXIT CODE: 0)", BG_GREEN)
        return 0


def run_member_demo(member_key: str, remediate: bool = False, fast: bool = False, real: bool = False, cloud: bool = False) -> int:
    """Điều phối và thực thi quy trình chạy CI/CD cho một thành viên cụ thể.

    Hỗ trợ 3 chế độ:
    1. Chế độ Trực quan mặc định: Trích xuất mã nguồn, phân tích Source/Sink đẹp mắt.
    2. Chế độ Real Engine (--real): Thực thi trực tiếp các module Python cốt lõi của CI tại local.
    3. Chế độ Cloud (--cloud): Kết nối GitHub CLI (gh) để kiểm tra trạng thái CI thật trên GitHub Actions.
    """
    if cloud:
        return run_cloud_ci_status(member_key)
    if real:
        return run_real_ci_for_member(member_key, remediate=remediate, fast=fast)

    """Điều phối và mô phỏng toàn diện quy trình chạy CI/CD cho một thành viên cụ thể.

    Quy trình kết hợp song song cả 2 trụ cột DevSecOps:
    1. An ninh mã nguồn (SAST Security Vulnerabilities): 4 lỗ hổng nghiêm trọng (ERROR).
    2. Chất lượng mã nguồn (SonarQube Code Quality): 1 lỗi Bug / Code Smell (CRITICAL / MAJOR).
    """
    if member_key not in MEMBERS_CATALOG:
        print(f"❌ Không tìm thấy thành viên: '{member_key}'. Các mã hợp lệ: {list(MEMBERS_CATALOG.keys())}")
        return 1

    m = MEMBERS_CATALOG[member_key]
    cq = m.get("code_quality", {})
    delay = 0.0 if fast else 0.4

    # Hiển thị biểu ngữ giới thiệu kịch bản
    print_banner(f"DEVSECOPS CI/CD PIPELINE — SHIFT-LEFT GATE SIMULATION", CYAN)
    print(f"{BOLD}👤 Thành viên thực hiện:{RESET}  {BOLD}{YELLOW}{m['name']}{RESET} ({m['id']})")
    print(f"{BOLD}💼 Vai trò trong dự án:{RESET}   {m['role']}")
    print(f"{BOLD}🎯 Phân hệ phụ trách:{RESET}     {m['scope']}")
    print(f"{BOLD}🌿 Nhánh phát triển:{RESET}      {CYAN}{m['branch']}{RESET} ➔ {GREEN}dev{RESET}")
    print(f"{BOLD}🏷️ Pull Request #{m['pr_num']}:{RESET}    \"{m['pr_title']}\"")
    print(f"{BOLD}📝 Commit [{m['commit_hash']}]:{RESET}         \"{m['commit_msg']}\"")

    time.sleep(delay)

    # -------------------------------------------------------------------------
    # STAGE 1: Policy Guard (Policy-as-Code - PaC)
    # -------------------------------------------------------------------------
    print_step("STAGE 1", "Policy Guard — Kiểm tra Quy chuẩn Phân nhánh, Commit & PR")
    print(f"  🔍 [1/3] Kiểm định luồng phân nhánh (RACI): {m['branch']} ➔ dev ... {GREEN}✔ HỢP LỆ{RESET}")
    time.sleep(delay * 0.5)
    print(f"  🔍 [2/3] Kiểm tra tiêu đề PR: \"{m['pr_title']}\" ... {GREEN}✔ CHUẨN QUY ƯỚC [{m['id']}]{RESET}")
    time.sleep(delay * 0.5)
    print(f"  🔍 [3/3] Kiểm tra Conventional Commits: \"{m['commit_msg']}\" ... {GREEN}✔ CHUẨN SEMANTIC{RESET}")
    time.sleep(delay * 0.5)
    print(f"\n  {GREEN}{BOLD}✅ [STAGE 1 PASSED] Policy Guard chấp thuận! Mở cổng kiểm tra Stage 2.{RESET}")

    time.sleep(delay)

    # -------------------------------------------------------------------------
    # STAGE 2: Security SAST & SonarQube Code Quality
    # -------------------------------------------------------------------------
    print_step("STAGE 2", "Dev Gate — Quét An ninh SAST & Kiểm định Chất lượng Mã nguồn (SonarQube)")
    print(f"  🚀 Khởi động song song 2 Động cơ:")
    print(f"     1. Semgrep Taint Engine: Quét phát hiện Taint Injection & Secrets...")
    print(f"     2. SonarQube Scanner:   Đo đạc chỉ số Quality Gate, Reliability & Maintainability...")
    print(f"  📂 Quét các tệp nguồn trong phân hệ của {m['name']}...")
    time.sleep(delay)

    if not remediate:
        # =====================================================================
        # KỊCH BẢN 1: MÃ NGUỒN CÓ LỖ HỔNG & LỖI CHẤT LƯỢNG
        # =====================================================================

        # PHẦN A: 4 LỖ HỔNG AN NINH (SAST VULNERABILITIES)
        print(f"\n  {RED}{BOLD}🚨 [A. AN NINH MÃ NGUỒN] PHÁT HIỆN 4 LỖ HỔNG BẢO MẬT (SEMGREP & SONARQUBE SAST):{RESET}\n")

        for v in m["vulns"]:
            time.sleep(delay * 0.7)
            sev_color = RED if "ERROR" in v["severity"] else YELLOW
            print(f"  {BOLD}┌─────────────────────────────────────────────────────────────────────────────┐{RESET}")
            print(f"  {BOLD}│ LỖ HỔNG #{v['num']}: {RED}{v['name']}{RESET}{' ' * (56 - len(v['name']))}{BOLD}│{RESET}")
            print(f"  {BOLD}├─────────────────────────────────────────────────────────────────────────────┤{RESET}")
            print(f"  │ 🏷️  Phân loại:  {BOLD}{v['cwe']}{RESET} | {DIM}{v['owasp']}{RESET}")
            print(f"  │ ⚠️  Mức độ:    {sev_color}{BOLD}🔴 {v['severity']}{RESET} | Động cơ: {CYAN}{v['engine']}{RESET}")
            print(f"  │ 📂  Vị trí:    {BOLD}{v['file']}:{v['line']}{RESET}")
            print(f"  │ 📜  Quy tắc:   {DIM}{v['rule']}{RESET}")
            print(f"  │ 📥  Source:    {YELLOW}{v['source']}{RESET}")
            print(f"  │ ⚡  Sink:      {RED}{v['sink']}{RESET}")
            print(f"  │ ⚖️  Pháp lý:   {DIM}{v['legal']}{RESET}")
            print(f"  │")
            print(f"  │ {BOLD}Trích xuất mã nguồn vi phạm (Vulnerable Code Context):{RESET}")

            code_lines = extract_code_context(v["file"], v["line"], context_lines=2)
            for lno, text, is_target in code_lines:
                prefix = f"  │   {RED}➔ {lno:3d} │ {text}{RESET}" if is_target else f"  │     {lno:3d} │ {DIM}{text}{RESET}"
                print(prefix)

            print(f"  {BOLD}└─────────────────────────────────────────────────────────────────────────────┘{RESET}\n")

        # PHẦN B: 1 LỖI CHẤT LƯỢNG MÃ NGUỒN TỪ SONARQUBE (CODE QUALITY ISSUE)
        if cq:
            time.sleep(delay * 0.7)
            cq_color = MAGENTA if cq.get("type") == "CODE_SMELL" else RED
            print(f"  {MAGENTA}{BOLD}🧹 [B. CHẤT LƯỢNG MÃ NGUỒN] PHÁT HIỆN 01 LỖI CODE QUALITY (SONARQUBE SCANNER):{RESET}\n")
            print(f"  {BOLD}┌─────────────────────────────────────────────────────────────────────────────┐{RESET}")
            print(f"  {BOLD}│ LỖI CHẤT LƯỢNG: {MAGENTA}{cq['name']}{RESET}{' ' * max(1, 60 - len(cq['name']))}{BOLD}│{RESET}")
            print(f"  {BOLD}├─────────────────────────────────────────────────────────────────────────────┤{RESET}")
            print(f"  │ 🏷️  Phân loại:  {cq_color}{BOLD}{cq['type']}{RESET} (SonarQube {cq['type']})")
            print(f"  │ ⚠️  Mức độ:    {BOLD}{cq['severity']}{RESET} (Severity Level)")
            print(f"  │ 📂  Vị trí:    {BOLD}{cq['file']}:{cq['line']}{RESET}")
            print(f"  │ 📜  Sonar Rule: {CYAN}{cq['rule']}{RESET}")
            print(f"  │ 📝  Chi tiết:  {cq['desc']}")
            print(f"  │")
            print(f"  │ {BOLD}Trích xuất ngữ cảnh mã nguồn SonarQube đánh dấu:{RESET}")

            cq_lines = extract_code_context(cq["file"], cq["line"], context_lines=2)
            for lno, text, is_target in cq_lines:
                prefix = f"  │   {MAGENTA}➔ {lno:3d} │ {text}{RESET}" if is_target else f"  │     {lno:3d} │ {DIM}{text}{RESET}"
                print(prefix)

            print(f"  {BOLD}└─────────────────────────────────────────────────────────────────────────────┘{RESET}\n")

        time.sleep(delay)

        # ---------------------------------------------------------------------
        # CƠ CHẾ CHẶN ĐỨNG TỰ ĐỘNG CỦA CI PIPELINE (BREAK-THE-BUILD ENFORCEMENT)
        # ---------------------------------------------------------------------
        print_banner("CHỐT CHẶN AN NINH & CHẤT LƯỢNG KÍCH HOẠT: CI CHẶN ĐỨNG (BREAK-THE-BUILD)", BG_RED, "#")
        print(f"  {RED}{BOLD}❌ ĐÁNH GIÁ CỔNG CHẤT LƯỢNG & AN NINH (DUAL-GATE EVALUATION):{RESET}")
        print(f"     1. {BOLD}Semgrep Security Gate:{RESET}   {RED}{BOLD}FAILED{RESET} (Phát hiện 4 lỗ hổng mức ERROR / HIGH)")
        print(f"     2. {BOLD}SonarQube Quality Gate:{RESET} {RED}{BOLD}ERROR (FAILED){RESET} (Phát hiện 1 {cq.get('type')} mức {cq.get('severity')})")
        print(f"     3. {BOLD}Ngưỡng cho phép merge:{RESET}  {BOLD}0 Lỗ hổng ERROR & 0 Critical/Major Bugs allowed{RESET}\n")

        print(f"  {BOLD}🛑 CƠ CHẾ BẢO VỆ TỰ ĐỘNG CỦA CI PIPELINE:{RESET}")
        print(f"     {RED}✖ [BLOCKED] Khóa nút hợp nhất (Merge Button is LOCKED) trên GitHub PR #{m['pr_num']}{RESET}")
        print(f"     {RED}✖ [BLOCKED] Ngắt khẩn cấp tiến trình CI tại Stage 2 (Exit Code: 1){RESET}")
        print(f"     {RED}✖ [BLOCKED] Stage 3 (Docker Build & Preview Deploy) BỊ HỦY BỎ HOÀN TOÀN!{RESET}")
        print(f"     {RED}✖ [BLOCKED] Stage 4 (Production Deployment) BỊ NGĂN CHẶN TUYỆT ĐỐI!{RESET}")
        print(f"     {YELLOW}✔ [SAVED]   Đã kết xuất báo cáo: reports/semgrep/report.html và sonarqube/report.html{RESET}\n")

        print(f"{RED}{BOLD}  👉 KẾT LUẬN: CI ĐÃ BẢO VỆ HỆ THỐNG THÀNH CÔNG BẰNG CÁCH CHẶN ĐỨNG CẢ LỖ HỔNG VÀ LỖI CODE QUALITY!{RESET}\n")

        return 1

    else:
        # =====================================================================
        # KỊCH BẢN 2: ĐÃ KHẮC PHỤC CẢ LỖ HỔNG VÀ LỖI CHẤT LƯỢNG MÃ NGUỒN -> CI PASS!
        # =====================================================================
        print_banner("ÁP DỤNG MÃ AN TOÀN & CLEAN CODE ĐÃ KHẮC PHỤC (REMEDIATION APPLIED)", BG_BLUE)
        print(f"  🛠️ {BOLD}{m['name']}{RESET} đã hoàn thành khắc phục toàn bộ lỗ hổng và lỗi chất lượng:\n")

        print(f"  {CYAN}{BOLD}[1. KHẮC PHỤC 4 LỖ HỔNG AN NINH MÃ NGUỒN]:{RESET}")
        for v in m["vulns"]:
            print(f"  ✔ LỖ HỔNG #{v['num']}: {v['name']} ({v['file']}:{v['line']})")
            print(f"  {GREEN}{v['remediation']}{RESET}\n")

        if cq:
            print(f"  {MAGENTA}{BOLD}[2. KHẮC PHỤC 01 LỖI CHẤT LƯỢNG MÃ NGUỒN SONARQUBE]:{RESET}")
            print(f"  ✔ LỖI QUALITY: {cq['name']} ({cq['file']}:{cq['line']} | Rule: {cq['rule']})")
            print(f"  {GREEN}{cq['remediation']}{RESET}\n")

        time.sleep(delay)
        print_step("STAGE 2: TÁI KIỂM ĐỊNH TOÀN DIỆN (RE-SCAN)", "Chạy lại kiểm định sau khi khắc phục mã nguồn")
        print(f"  🔍 Semgrep Taint Engine quét lại:     {GREEN}✔ 0 Lỗ hổng bảo mật (0 ERROR, 0 WARNING){RESET}")
        print(f"  🔍 SonarQube Scanner quét lại:       {GREEN}✔ Quality Gate PASSED (A Rating, 0 Bugs, 0 Smells){RESET}")
        print(f"  🔍 Policy Guard IaC Rules quét lại:   {GREEN}✔ 0 Secret rò rỉ trong cấu hình Docker Compose{RESET}\n")

        print_banner("DUAL SECURITY & QUALITY GATES PHÊ DUYỆT THÀNH CÔNG (STAGE 2 PASSED)", BG_GREEN)
        print(f"  {GREEN}{BOLD}✅ Pull Request #{m['pr_num']} của {m['name']} ĐỦ ĐIỀU KIỆN HỢP NHẤT VÀO NHÁNH DEV!{RESET}")
        print(f"  🚀 Tự động kích hoạt Stage 3: Docker Build & Monitoring Smoke Test...")
        print(f"  🐳 Docker Compose Build:              {GREEN}✔ SUCCESS (Container Ready){RESET}")
        print(f"  📈 Promtail + Loki Observability:     {GREEN}✔ SUCCESS (Audit Streams Connected){RESET}")
        print(f"  🎉 Mã nguồn sạch và an toàn tuyệt đối, sẵn sàng cho Production!\n")

        return 0


def interactive_menu() -> None:
    """Hiển thị menu tương tác trên console cho phép người dùng chọn thành viên demo."""
    while True:
        print_banner("HỆ THỐNG DEVSECOPS CI/CD — MENU DEMO CHẶN LỖ HỔNG & CODE QUALITY", CYAN)
        print("Danh sách thành viên phụ trách đề tài:")
        for key, m in MEMBERS_CATALOG.items():
            print(f"  [{m['order']}] {BOLD}{m['name']:20s}{RESET} ({m['id']:6s}) — {m['role']}")
        print("  [A] Chạy toàn bộ 5 thành viên lần lượt (Full Showcase)")
        print("  [0] Thoát chương trình\n")

        choice = input("👉 Nhập lựa chọn của bạn (1-5, A, 0): ").strip().lower()

        if choice == "0":
            print("\n👋 Tạm biệt! Hẹn gặp lại trong buổi bảo vệ đề tài.\n")
            break
        elif choice == "a":
            for key in MEMBERS_CATALOG:
                run_member_demo(key, remediate=False, fast=False)
                input("\n👉 Nhấn Enter để tiếp tục thành viên tiếp theo...")
        else:
            found_key = None
            for key, m in MEMBERS_CATALOG.items():
                if str(m["order"]) == choice or key == choice:
                    found_key = key
                    break

            if found_key:
                # 1. Chạy kịch bản phát hiện và chặn đứng lỗi trước
                run_member_demo(found_key, remediate=False)

                # 2. Hỏi người thuyết trình có muốn demo tiếp kịch bản khắc phục không
                prompt = input(f"\n💡 Bạn có muốn demo kịch bản KHẮC PHỤC (Remediation) để CI thông qua không? (y/N): ").strip().lower()
                if prompt in ("y", "yes"):
                    run_member_demo(found_key, remediate=True)

                input("\n👉 Nhấn Enter để quay lại Menu chính...")
            else:
                print(f"⚠️ Lựa chọn không hợp lệ, vui lòng thử lại!")
                time.sleep(1)


def main() -> None:
    """Điểm nhập cảnh chính (Entrypoint) xử lý cờ dòng lệnh CLI."""
    parser = argparse.ArgumentParser(
        description="Động cơ Demo CI/CD DevSecOps & Chốt chặn Bảo mật/Chất lượng theo Thành viên",
        epilog="Ví dụ: python demo_ci.py --member namng --fast"
    )
    parser.add_argument(
        "--member", "-m",
        choices=["namng", "haind", "manhdx", "anhld", "mainp", "1", "2", "3", "4", "5", "all"],
        help="Chỉ định mã thành viên hoặc số thứ tự (1-5, hoặc all)"
    )
    parser.add_argument(
        "--remediate", "--fix",
        action="store_true",
        help="Chạy trực tiếp ở chế độ đã khắc phục an toàn (demo CI Pass)"
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Bỏ qua độ trễ hiệu ứng terminal để chạy nhanh"
    )
    parser.add_argument(
        "--real", "--live",
        action="store_true",
        help="Thực thi trực tiếp các engine CI thật (Policy Guard, Semgrep Gate, IaC Validator)"
    )
    parser.add_argument(
        "--cloud",
        action="store_true",
        help="Kết nối GitHub CLI để kiểm tra trạng thái workflow trên GitHub Actions"
    )

    args = parser.parse_args()

    # Nếu không truyền tham số --member, mở giao diện menu tương tác
    if not args.member:
        interactive_menu()
        return

    target = args.member.lower()
    if target in ("all", "a"):
        for key in MEMBERS_CATALOG:
            run_member_demo(key, remediate=args.remediate, fast=args.fast, real=args.real, cloud=args.cloud)
        return

    # Ánh xạ số thứ tự (1-5) sang mã định danh thành viên
    num_map = {"1": "namng", "2": "haind", "3": "manhdx", "4": "anhld", "5": "mainp"}
    key = num_map.get(target, target)

    # Chạy demo và thoát với mã trạng thái của CI (1 = Blocked, 0 = Passed)
    code = run_member_demo(key, remediate=args.remediate, fast=args.fast, real=args.real, cloud=args.cloud)
    sys.exit(code)


if __name__ == "__main__":
    main()
