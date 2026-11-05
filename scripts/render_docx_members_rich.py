import docx
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

def add_code_box(doc, p_target, code_text):
    """Inserts a styled callout code box before p_target."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    
    # Background shading #F8F9FA
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F8F9FA"/>')
    cell._tc.get_or_add_tcPr().append(shd)
    
    # Borders: left border #0969DA (width 20 ~ 2.5pt), subtle top/right/bottom #D0D7DE
    borders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="4" w:space="0" w:color="E1E4E8"/>
            <w:left w:val="single" w:sz="20" w:space="0" w:color="0969DA"/>
            <w:bottom w:val="single" w:sz="4" w:space="0" w:color="E1E4E8"/>
            <w:right w:val="single" w:sz="4" w:space="0" w:color="E1E4E8"/>
        </w:tcBorders>
    ''')
    cell._tc.get_or_add_tcPr().append(borders)
    
    # Padding
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="120" w:type="dxa"/>
            <w:left w:w="180" w:type="dxa"/>
            <w:bottom w:w="120" w:type="dxa"/>
            <w:right w:w="180" w:type="dxa"/>
        </w:tcMar>
    ''')
    cell._tc.get_or_add_tcPr().append(tcMar)
    
    lines = code_text.strip().splitlines()
    for i, line in enumerate(lines):
        if i == 0:
            p = cell.paragraphs[0]
        else:
            p = cell.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.line_spacing = 1.05
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(line if line else " ")
        run.font.name = "Consolas"
        run.font.size = Pt(8.5)
        run.font.color.rgb = RGBColor(0x24, 0x29, 0x2E)
        
    p_target._element.addprevious(tbl._element)

def add_meta_line(p_target, label, value):
    """Adds a clean metadata line without double bullets."""
    p = p_target.insert_paragraph_before()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.left_indent = Inches(0.25)
    
    r1 = p.add_run(f"• {label}: ")
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(11)
    r1.font.bold = True
    r1.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
    
    r2 = p.add_run(value)
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(11)

def add_section_header(p_target, text, level=1):
    """Adds a clean section header."""
    p = p_target.insert_paragraph_before()
    if level == 1:
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
    elif level == 2:
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.left_indent = Inches(0.15)
        run = p.add_run(text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.italic = True
        run.font.color.rgb = RGBColor(0x1F, 0x23, 0x28)

def add_body_text(p_target, text, indent=False):
    """Adds body text with standard indentation."""
    p = p_target.insert_paragraph_before()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(3)
    if indent:
        p.paragraph_format.left_indent = Inches(0.25)
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(11)

def add_metrics_table(doc, p_target, rows_data):
    """Adds a beautiful 4-column SonarQube Metrics table."""
    tbl = doc.add_table(rows=len(rows_data), cols=4)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    col_widths = [Inches(2.6), Inches(1.3), Inches(1.4), Inches(1.2)]
    
    for r_idx, row in enumerate(tbl.rows):
        is_header = (r_idx == 0)
        for c_idx, cell in enumerate(row.cells):
            cell.width = col_widths[c_idx]
            
            # Shading
            if is_header:
                shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="003366"/>')
            elif r_idx % 2 == 1:
                shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="FFFFFF"/>')
            else:
                shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F8F9FA"/>')
            cell._tc.get_or_add_tcPr().append(shd)
            
            # Borders
            borders = parse_xml(f'''
                <w:tcBorders {nsdecls("w")}>
                    <w:top w:val="single" w:sz="4" w:space="0" w:color="D0D7DE"/>
                    <w:left w:val="single" w:sz="4" w:space="0" w:color="D0D7DE"/>
                    <w:bottom w:val="single" w:sz="4" w:space="0" w:color="D0D7DE"/>
                    <w:right w:val="single" w:sz="4" w:space="0" w:color="D0D7DE"/>
                </w:tcBorders>
            ''')
            cell._tc.get_or_add_tcPr().append(borders)
            
            # Padding
            tcMar = parse_xml(f'''
                <w:tcMar {nsdecls("w")}>
                    <w:top w:w="80" w:type="dxa"/>
                    <w:left w:w="120" w:type="dxa"/>
                    <w:bottom w:w="80" w:type="dxa"/>
                    <w:right w:w="120" w:type="dxa"/>
                </w:tcMar>
            ''')
            cell._tc.get_or_add_tcPr().append(tcMar)
            
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if (is_header or c_idx > 0) else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.line_spacing = 1.05
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            
            run = p.add_run(rows_data[r_idx][c_idx])
            run.font.name = "Times New Roman"
            run.font.size = Pt(9.5)
            if is_header:
                run.font.bold = True
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            else:
                run.font.color.rgb = RGBColor(0x24, 0x29, 0x2E)
                if c_idx == 3:
                    run.font.bold = True
                    
    p_target._element.addprevious(tbl._element)

def render_rich_docx():
    docx_path = "docs/05-Báo cáo bài tập lớn DevSecOps.docx"
    doc = docx.Document(docx_path)
    
    # 1. Update Table 11 (Bảng 4.1 summary)
    t11 = doc.tables[11]
    members_summary = [
        ("1. Nguyễn Giang Nam\n(Trưởng nhóm)", 
         "In-band UNION SQL Injection tại tra cứu cảng (ports.php:38) & Thiếu ID/Label trợ năng WCAG (ports.php:26)", 
         "Mã nguồn & Trợ năng\n(Code & Accessibility)", 
         "Pha Test / SAST & Quality Gate (Stage 2)", 
         "CS-03, CS-04\nGDPR: Art. 32\nNĐ 13/2023: Điều 9 K.2, Điều 26", 
         "Security as Code (Semgrep Taint) & SonarQube Quality Gate Rating A"),
        ("2. Nguyễn Đình Hải", 
         "Authentication Bypass SQL Injection tại đăng nhập (login.php:19) & Vi phạm PSR-12 khối lệnh rẽ nhánh (login.php:36)", 
         "Mã nguồn & Clean Code\n(Code Security & PSR-12)", 
         "Pha Test / SAST Gate (Stage 2)", 
         "CS-03, CS-08\nGDPR: Art. 32\nNĐ 13/2023: Điều 9 K.2, Điều 17", 
         "Security as Code (Prepared Statements) & SonarQube rule php:S121"),
        ("3. Đào Xuân Mạnh", 
         "Local File Inclusion Path Traversal tại cẩm nang (guide.php:54) & Lỗi độ tin cậy include_once (guide.php:56)", 
         "Mã nguồn & Reliability\n(Code Security & Reliability)", 
         "Pha Build / SAST Gate (Stage 2)", 
         "CS-05, CS-08\nGDPR: Art. 5(1)(f), 32\nNĐ 13/2023: Điều 13 K.2, Điều 26", 
         "Security as Code (Whitelist basename) & SonarQube rule php:S2003"),
        ("4. Lê Đức Anh", 
         "Order-By Clause SQL Injection tại hồ sơ (account.php:41) & Form Label thiếu liên kết ID trợ năng (account.php:28)", 
         "Mã nguồn & Trợ năng\n(Code Security & WCAG 2.1)", 
         "Pha Test / SAST Gate (Stage 2)", 
         "CS-03, CS-08\nGDPR: Art. 32\nNĐ 13/2023: Điều 9 K.2, Điều 26", 
         "Security as Code (Whitelist Order Column) & SonarQube Web:S6853"),
        ("5. Nguyễn Phương Mai", 
         "INSERT Statement SQL Injection tại bình luận (comment_add.php:19) & Admin Filter thiếu Label trợ năng (admin_dashboard.php:26)", 
         "Mã nguồn & Vận hành\n(Code Security & Accessibility)", 
         "Pha Test & Monitor (Stage 2 & Stage 4)", 
         "CS-03, CS-07, CS-08\nGDPR: Art. 32, 33\nNĐ 13/2023: Điều 9 K.2, Điều 17", 
         "Security as Code (Parameterized INSERT) & SonarQube Web:InputWithoutLabelCheck")
    ]
    for idx, (m_name, m_prob, m_cat, m_phase, m_legal, m_tech) in enumerate(members_summary, 1):
        t11.rows[idx].cells[0].text = m_name
        t11.rows[idx].cells[1].text = m_prob
        t11.rows[idx].cells[2].text = m_cat
        t11.rows[idx].cells[3].text = m_phase
        t11.rows[idx].cells[4].text = m_legal
        t11.rows[idx].cells[5].text = m_tech

    # Format Table 11 cells font
    for row in t11.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.name = "Times New Roman"
                    r.font.size = Pt(9.5)

    # 2. Locate p_start and p_end
    p_start = None
    p_end = None
    for p in doc.paragraphs:
        if p.style.name == "CTDT-H3" and "4.1.1. Nguyễn Giang Nam" in p.text:
            p_start = p
        elif p.style.name == "CTDT-H2" and "4.2. Diễn tập thực nghiệm" in p.text:
            p_end = p
            break

    print(f"p_start found: {p_start.text[:50]}")
    print(f"p_end found: {p_end.text[:50]}")

    # Full rich data definition for 5 members
    rich_members = [
        # --- MEMBER 1: NAM ---
        {
            "heading": "4.1.1. Nguyễn Giang Nam (Trưởng nhóm) — In-band UNION SQL Injection & Accessibility Code Quality",
            "role": "Là Trưởng nhóm và Kiến trúc sư DevSecOps (Lead Architect), sinh viên Nguyễn Giang Nam trực tiếp chỉ đạo thiết kế hệ thống đường ống CI/CD Dual-Gate và phụ trách phân hệ Tra cứu cảng biển (ports.php). Phân hệ ghi nhận 01 lỗ hổng bảo mật nghiêm trọng (SAST Semgrep) và 01 lỗi chất lượng mã nguồn (SonarQube Bug).",
            "vuln": {
                "title": "Phần A: CHI TIẾT LỖ HỔNG AN TOÀN BẢO MẬT (SAST — SEMGREP / OWASP / CWE)",
                "sub_title": "1. In-band UNION-based SQL Injection tại trang Tra cứu Cảng biển",
                "meta": [
                    ("Vị trí vi phạm", "InlaneWeb/web/src/pages/ports.php:38"),
                    ("Phân loại lỗi", "Mã nguồn (Application Code)"),
                    ("Pha trong DevSecOps", "Pha Test / SAST Gate (Stage 2 trong CI/CD Pipeline)"),
                    ("Mã định danh điểm yếu", "CWE-89: SQL Injection | OWASP Top 10:2021: A03:2021 — Injection"),
                    ("Quy tắc phát hiện", "Semgrep Rule php.lang.security.injection.tainted-sql-string.tainted-sql-string")
                ],
                "vuln_code_title": "a. Bằng chứng mã nguồn vi phạm (Vulnerable Code):",
                "vuln_code": """// Source: Dữ liệu người dùng nhập từ tham số GET không qua kiểm soát
$q = $_GET['q'] ?? '';

// Sink: Nối chuỗi trực tiếp vào câu lệnh SQL
$sql = "SELECT code, city, country, volume FROM ports WHERE code LIKE '%$q%'";
echo '<div class="query-box">' . htmlspecialchars($sql) . '</div>';
$res = query($sql);""",
                "detection_title": "b. Cơ chế phát hiện & Trích xuất mã nguồn (Detection Mechanism):",
                "detection_text": "Quy tắc Semgrep quét phát hiện (Rule Definition Code) với chế độ phân tích luồng ô nhiễm mode: taint theo dõi tham số từ nguồn $_GET chảy vào điểm chìm query():",
                "semgrep_rule": """rules:
  - id: php.lang.security.injection.tainted-sql-string.tainted-sql-string
    languages: [php]
    severity: ERROR
    mode: taint
    pattern-sources:
      - pattern: $_GET[...]
      - pattern: $_POST[...]
    pattern-sinks:
      - pattern: query("...$X...", ...)
      - pattern: mysqli_query($CONN, "...$X...", ...)
    pattern-sanitizers:
      - pattern: $DB->prepare(...)
      - pattern: intval(...)""",
                "source_sink_text": "Cơ chế phân tích luồng ô nhiễm (Taint / AST Analysis) tự động trích xuất qua ci/semgrep_report.py:",
                "source_code": "// 🟡 SOURCE: Dòng 21 (InlaneWeb/web/src/pages/ports.php):\n$q = $_GET['q'] ?? '';",
                "sink_code": "// 🔴 SINK: Dòng 38-41 (InlaneWeb/web/src/pages/ports.php):\n$sql = \"SELECT code, city, country, volume FROM ports WHERE code LIKE '%$q%'\";\n$res = query($sql);",
                "poc_title": "c. Kịch bản khai thác thực tế (PoC):",
                "poc_text": "Kẻ tấn công gửi tải trọng trích xuất tên cơ sở dữ liệu và phiên bản MariaDB:",
                "poc_code": "GET /ports?q=' UNION SELECT 1, @@version, user(), 4-- -",
                "poc_impact": "Hậu quả: Kẻ tấn công trích xuất được toàn bộ tài khoản quản trị, mật khẩu băm và dữ liệu khách hàng trong CSDL.",
                "remediation_title": "d. Cách thức xử lý & Khắc phục (Remediation):",
                "remediation_text": "Chuyển đổi hoàn toàn sang Prepared Statements tham số hóa, triệt tiêu khả năng mã SQL bị diễn giải sai lệch:",
                "remediation_code": """// Mã nguồn sau khi vá an toàn bằng Prepared Statement:
$stmt = db()->prepare("SELECT code, city, country, volume FROM ports WHERE code LIKE ?");
$search_param = "%" . $q . "%";
$stmt->bind_param("s", $search_param);
$stmt->execute();
$res = $stmt->get_result();""",
                "sac_title": "e. Đánh giá Vi phạm Chính sách & Bài toán Security-as-Code (SaC):",
                "sac_text": "• Pha DevSecOps: Pha Test / SAST Gate (Stage 2). Lỗi phát sinh trong quá trình lập trình chức năng tra cứu cảng biển. Nếu không có chốt chặn SAST tại Stage 2, mã nguồn ô nhiễm sẽ vượt qua kiểm định và đưa lên máy chủ sản xuất.\n• Căn cứ pháp lý: Nghị định 13/2023/NĐ-CP (Điều 9 K.2, Điều 26) về bảo vệ an toàn dữ liệu cá nhân; GDPR (Article 32 — Security of Processing).\n• Hiện thực hóa Bài toán SaC: Mã hóa tiêu chuẩn bảo mật thành quy tắc chặn trong pipeline .github/workflows/devsecops-pipeline.yml kết hợp cờ --error và chốt chặn ci/semgrep_gate.py kích hoạt cơ chế ngắt build (Break-the-Build):",
                "sac_code": """# .github/workflows/devsecops-pipeline.yml (Stage 2: Semgrep Security SAST)
- name: Run Semgrep SAST
  run: |
    pipx run semgrep scan \\
      --config "p/owasp-top-ten" \\
      --config "ci/semgrep-local-rules.yml" \\
      --error --json -o reports/semgrep/semgrep.json \\
      InlaneWeb"""
            },
            "cq": {
                "title": "Phần B: KIỂM ĐỊNH CHẤT LƯỢNG MÃ NGUỒN (SONARQUBE CODE QUALITY)",
                "sub_title": "CQ-01: Input Control Missing ID & Associated Label (Web Accessibility Bug)",
                "intro": "Trong mô hình DevSecOps hiện đại, dự án triển khai quy chuẩn kiểm soát kép Dual-Gate (Security Gate + Quality Gate). Công cụ SonarQube Scanner được kích hoạt tại Stage 2 để kiểm tra toàn diện chuẩn Clean Code PSR, độ tin cậy và khả năng tiếp cận (Accessibility - WCAG 2.1).",
                "meta": [
                    ("Vị trí vi phạm", "InlaneWeb/web/src/pages/ports.php:26"),
                    ("Quy tắc SonarQube", "Web:InputWithoutLabelCheck (Major Bug)"),
                    ("Phân loại & Mức độ", "🐞 BUG | 🟠 MAJOR"),
                    ("Tiêu chuẩn vi phạm", "WCAG 2.1 Level A (Criteria 1.3.1, 4.1.2) / ISO/IEC 40500:2012")
                ],
                "bad_code_title": "Bằng chứng mã nguồn vi phạm (Non-compliant Code):",
                "bad_code": """<!-- Dòng 25-28 (InlaneWeb/web/src/pages/ports.php) - MÃ NGUỒN VI PHẠM -->
<form class="searchbar" action="/ports" method="get">
    <input type="text" name="q" value="<?= $q ?>" placeholder="Mã cảng hoặc tên thành phố...">
    <button class="btn" type="submit">Tra cứu</button>
</form>""",
                "analysis_title": "Cơ chế phân tích của SonarQube:",
                "analysis_text": "Bộ phân tích sonar-html-plugin duyệt DOM Tree và phát hiện ô input tìm kiếm không có thuộc tính id gắn kết với thẻ <label>, khiến trình đọc màn hình (Screen Readers) không nhận diện được đối tượng nhập liệu.",
                "clean_code_title": "Phương án khắc phục chuẩn hóa (Clean Code Refactoring):",
                "clean_code": """<!-- Dòng 25-29 (InlaneWeb/web/src/pages/ports.php) - MÃ NGUỒN ĐÃ KHẮC PHỤC -->
<form class="searchbar" action="/ports" method="get">
    <label for="port-search-input" class="sr-only">Từ khóa tra cứu cảng biển:</label>
    <input id="port-search-input" type="text" name="q" value="<?= htmlspecialchars($q, ENT_QUOTES, 'UTF-8') ?>" placeholder="Mã cảng hoặc tên thành phố...">
    <button class="btn" type="submit">Tra cứu</button>
</form>""",
                "metrics": [
                    ["Chỉ số Chất lượng (Metrics)", "Trước khi Sửa (Dirty State)", "Sau khi Sửa (Clean Code)", "Trạng thái Thẩm định"],
                    ["New Bugs", "3 (2 Major, 1 Minor)", "0", "✅ ĐẠT CHUẨN (= 0)"],
                    ["Reliability Rating", "C", "A", "✅ ĐẠT MỨC A"],
                    ["Accessibility Compliance", "Vi phạm WCAG 2.1", "Đạt chuẩn ISO/IEC 40500", "✅ ĐẠT TRỢ NĂNG"],
                    ["SonarQube Quality Gate", "FAILED (Chặn Build)", "PASSED (Cho phép Merge)", "✅ HOÀN THÀNH"]
                ]
            }
        },

        # --- MEMBER 2: HAI ---
        {
            "heading": "4.1.2. Nguyễn Đình Hải — Authentication Bypass SQL Injection & Clean Code PSR-12",
            "role": "Sinh viên Nguyễn Đình Hải đảm nhiệm vai trò Kỹ sư An ninh Phần mềm (Security Engineer), chịu trách nhiệm phân hệ Xác thực người dùng (login.php) và kỹ thuật phân tích luồng ô nhiễm Taint Analysis. Phân hệ ghi nhận 01 lỗ hổng bảo mật nghiêm trọng và 01 lỗi chất lượng mã nguồn.",
            "vuln": {
                "title": "Phần A: CHI TIẾT LỖ HỔNG AN TOÀN BẢO MẬT (SAST — SEMGREP / OWASP / CWE)",
                "sub_title": "1. Authentication Bypass SQL Injection tại trang Đăng nhập",
                "meta": [
                    ("Vị trí vi phạm", "InlaneWeb/web/src/pages/login.php:19"),
                    ("Phân loại lỗi", "Mã nguồn (Application Code)"),
                    ("Pha trong DevSecOps", "Pha Test / SAST Gate (Stage 2 trong CI/CD Pipeline)"),
                    ("Mã định danh điểm yếu", "CWE-89: SQL Injection | OWASP Top 10:2021: A03:2021 — Injection"),
                    ("Quy tắc phát hiện", "Semgrep Rule php.lang.security.injection.tainted-sql-string.tainted-sql-string")
                ],
                "vuln_code_title": "a. Bằng chứng mã nguồn vi phạm (Vulnerable Code):",
                "vuln_code": """// Nguồn dữ liệu nhận trực tiếp từ form POST
$username = $_POST['username'] ?? '';
$password = $_POST['password'] ?? '';

// Điểm chìm: Nối chuỗi vào truy vấn xác thực
$sql = "SELECT id, username, role FROM users WHERE username = '$username' AND password = '$password'";
$row = query_one($sql);
if ($row) {
    $_SESSION['uid'] = $row['id'];
    header('Location: /account');
    exit;
}""",
                "detection_title": "b. Cơ chế phát hiện & Trích xuất mã nguồn (Detection Mechanism):",
                "detection_text": "Quy tắc Semgrep quét phát hiện nhận diện dữ liệu $_POST chảy thẳng vào câu lệnh xác thực SQL qua hàm bao query_one():",
                "semgrep_rule": """rules:
  - id: php.lang.security.injection.tainted-sql-string.tainted-sql-string
    languages: [php]
    severity: ERROR
    mode: taint
    pattern-sources:
      - pattern: $_POST[...]
    pattern-sinks:
      - pattern: query_one("... WHERE username = '$U' AND password = '$P'", ...)""",
                "source_sink_text": "Cơ chế phân tích luồng ô nhiễm (Taint / AST Analysis) tự động trích xuất qua ci/semgrep_report.py:",
                "source_code": "// 🟡 SOURCE: Dòng 15-16 (InlaneWeb/web/src/pages/login.php):\n$username = $_POST['username'] ?? '';\n$password = $_POST['password'] ?? '';",
                "sink_code": "// 🔴 SINK: Dòng 19-20 (InlaneWeb/web/src/pages/login.php):\n$sql = \"SELECT id, username, role FROM users WHERE username = '$username' AND password = '$password'\";\n$row = query_one($sql);",
                "poc_title": "c. Kịch bản khai thác thực tế (PoC):",
                "poc_text": "Kẻ tấn công gửi tải trọng đăng nhập vượt qua xác thực:",
                "poc_code": "POST /login\nusername=admin' -- -\npassword=anything",
                "poc_impact": "Hậu quả: Kẻ tấn công bỏ qua hoàn toàn cơ chế kiểm tra mật khẩu, chiếm đoạt tài khoản Quản trị viên cao nhất mà không cần mật khẩu hợp lệ.",
                "remediation_title": "d. Cách thức xử lý & Khắc phục (Remediation):",
                "remediation_text": "Tách biệt hoàn toàn việc kiểm tra người dùng và băm mật khẩu bảo mật qua hàm chuẩn Bcrypt/Argon2:",
                "remediation_code": """// 1. Dùng Prepared Statement tìm tài khoản
$stmt = db()->prepare("SELECT id, username, password, role FROM users WHERE username = ?");
$stmt->bind_param("s", $username);
$stmt->execute();
$user = $stmt->get_result()->fetch_assoc();

// 2. So khớp mật khẩu bằng hàm băm an toàn Bcrypt
if ($user && password_verify($password, $user['password'])) {
    session_regenerate_id(true); // Chống Session Fixation
    $_SESSION['uid'] = $user['id'];
    header('Location: /account');
    exit;
}""",
                "sac_title": "e. Đánh giá Vi phạm Chính sách & Bài toán Security-as-Code (SaC):",
                "sac_text": "• Pha DevSecOps: Pha Test / SAST Gate (Stage 2). Lỗi nằm tại module xác thực đăng nhập, tạo nguy cơ chiếm đoạt phiên quản trị viên.\n• Căn cứ pháp lý: Nghị định 13/2023/NĐ-CP (Điều 9 K.2, Điều 17) về an ninh xác thực người dùng; GDPR (Article 32 — Security of Processing).\n• Hiện thực hóa Bài toán SaC: Thiết lập quy tắc kiểm tra cú pháp truy vấn đăng nhập bắt buộc phải sử dụng Prepared Statement tham số hóa, ngắt build nếu phát hiện nối chuỗi:",
                "sac_code": """# Kiểm định SaC bắt buộc tham số hóa câu truy vấn xác thực
- id: php.lang.security.injection.tainted-sql-string.tainted-sql-string
  languages: [php]
  severity: ERROR
  mode: taint
  pattern-sources: [pattern: $_POST['username']]
  pattern-sinks: [pattern: query_one("... WHERE username = '$U' AND password = '$P'", ...)]"""
            },
            "cq": {
                "title": "Phần B: KIỂM ĐỊNH CHẤT LƯỢNG MÃ NGUỒN (SONARQUBE CODE QUALITY)",
                "sub_title": "CQ-01: Missing Curly Braces in Nested Statement (Clean Code Smell)",
                "intro": "SonarQube Scanner được kích hoạt tại Stage 2 để kiểm tra toàn diện chuẩn Clean Code PSR, độ tin cậy và khả năng bảo trì mã nguồn (Maintainability). Vi phạm Critical Code Smell sẽ đánh rớt Quality Gate.",
                "meta": [
                    ("Vị trí vi phạm", "InlaneWeb/web/src/pages/login.php:36"),
                    ("Quy tắc SonarQube", "php:S121 (Critical Code Smell)"),
                    ("Phân loại & Mức độ", "🧹 CODE_SMELL | 🔴 CRITICAL"),
                    ("Tiêu chuẩn vi phạm", "PSR-12 Control Structures Standard / SonarQube Clean Code")
                ],
                "bad_code_title": "Bằng chứng mã nguồn vi phạm (Non-compliant Code):",
                "bad_code": """<!-- Dòng 35-37 (InlaneWeb/web/src/pages/login.php) - MÃ NGUỒN VI PHẠM -->
<h1>Đăng nhập</h1>
<?php if ($error) flash($error, 'error'); ?>
<form action="/login" method="post">""",
                "analysis_title": "Cơ chế phân tích của SonarQube:",
                "analysis_text": "Khối lệnh if lồng nhau không sử dụng cặp dấu ngoặc nhọn { } để bao bọc phạm vi thực thi. Quy chuẩn mã nguồn sạch PSR-12 và SonarQube Clean Code yêu cầu tất cả các khối điều khiển rẽ nhánh phải có dấu ngoặc bảo vệ, tránh các lỗi logic ngầm nguy hiểm khi mở rộng mã.",
                "clean_code_title": "Phương án khắc phục chuẩn hóa (Clean Code Refactoring):",
                "clean_code": """<!-- Dòng 35-39 (InlaneWeb/web/src/pages/login.php) - MÃ NGUỒN ĐÃ KHẮC PHỤC -->
<h1>Đăng nhập</h1>
<?php if ($error) {
    flash($error, 'error');
} ?>
<form action="/login" method="post">""",
                "metrics": [
                    ["Chỉ số Chất lượng (Metrics)", "Trước khi Sửa (Dirty State)", "Sau khi Sửa (Clean Code)", "Trạng thái Thẩm định"],
                    ["New Critical Code Smells", "1 (php:S121)", "0", "✅ ĐẠT CHUẨN (= 0)"],
                    ["New Bugs", "1 (Major)", "0", "✅ ĐẠT CHUẨN (= 0)"],
                    ["Maintainability Rating", "B", "A", "✅ ĐẠT MỨC A"],
                    ["SonarQube Quality Gate", "FAILED (Chặn Build)", "PASSED (Cho phép Merge)", "✅ HOÀN THÀNH"]
                ]
            }
        },

        # --- MEMBER 3: MANH ---
        {
            "heading": "4.1.3. Đào Xuân Mạnh — Local File Inclusion & Include Reliability Bug",
            "role": "Sinh viên Đào Xuân Mạnh đảm nhiệm vai trò Kỹ sư Kiểm định Chất lượng và Bảo mật (QA / DevSecOps Engineer), chịu trách nhiệm thiết lập tiêu chuẩn an toàn cho phân hệ Cẩm nang Quy chuẩn logistics (guide.php) và SonarQube Quality Gate. Phân hệ ghi nhận 01 lỗ hổng bảo mật và 01 lỗi chất lượng mã nguồn.",
            "vuln": {
                "title": "Phần A: CHI TIẾT LỖ HỔNG AN TOÀN BẢO MẬT (SAST — SEMGREP / OWASP / CWE)",
                "sub_title": "1. Local File Inclusion (Path Traversal) tại Cẩm nang Quy chuẩn",
                "meta": [
                    ("Vị trí vi phạm", "InlaneWeb/web/src/pages/guide.php:54"),
                    ("Phân loại lỗi", "Mã nguồn (Application Code)"),
                    ("Pha trong DevSecOps", "Pha Build & Quality Gate (Stage 2 trong CI/CD Pipeline)"),
                    ("Mã định danh điểm yếu", "CWE-22: Path Traversal | OWASP Top 10:2021: A01:2021 — Broken Access Control"),
                    ("Quy tắc phát hiện", "Semgrep Rule php.lang.security.injection.tainted-filename.tainted-filename & SonarQube php:S2083")
                ],
                "vuln_code_title": "a. Bằng chứng mã nguồn vi phạm (Vulnerable Code):",
                "vuln_code": """$doc = $_GET['doc'] ?? 'incoterms2020.html';
$target_file = __DIR__ . '/../guides/' . $doc;

// Điểm chìm kích hoạt nạp tệp không giới hạn
if (@file_exists($target_file) || str_contains($doc, '..')) {
    include $target_file; // Thực thi nạp tệp
}""",
                "detection_title": "b. Cơ chế phát hiện & Trích xuất mã nguồn (Detection Mechanism):",
                "detection_text": "Quy tắc Semgrep quét phát hiện theo dõi biến $doc nhận từ URL chảy trực tiếp vào lệnh nạp tệp động include $target_file:",
                "semgrep_rule": """rules:
  - id: php.lang.security.injection.tainted-filename.tainted-filename
    languages: [php]
    severity: WARNING
    mode: taint
    pattern-sources:
      - pattern: $_GET[...]
    pattern-sinks:
      - pattern: file_exists($PATH)
      - pattern: is_file($PATH)""",
                "source_sink_text": "Cơ chế phân tích luồng ô nhiễm (Taint / AST Analysis) tự động trích xuất qua ci/semgrep_report.py:",
                "source_code": "// 🟡 SOURCE: Dòng 22 (InlaneWeb/web/src/pages/guide.php):\n$doc = $_GET['doc'] ?? 'incoterms2020.html';",
                "sink_code": "// 🔴 SINK: Dòng 54 (InlaneWeb/web/src/pages/guide.php):\ninclude $target_file;",
                "poc_title": "c. Kịch bản khai thác thực tế (PoC):",
                "poc_text": "Kẻ tấn công gửi yêu cầu đọc trộm tệp hệ thống hoặc trích xuất mã nguồn PHP qua wrapper:",
                "poc_code": "GET /guide?doc=../../../../etc/passwd\nGET /guide?doc=php://filter/convert.base64-encode/resource=../lib/db.php",
                "poc_impact": "Hậu quả: Kẻ tấn công đọc trích xuất toàn bộ tệp cấu hình chứa mật khẩu CSDL MariaDB và các tệp nhạy cảm trên máy chủ hệ thống.",
                "remediation_title": "d. Cách thức xử lý & Khắc phục (Remediation):",
                "remediation_text": "Sử dụng hàm lọc tên tệp basename() kết hợp với Whitelist danh mục tài liệu cho phép:",
                "remediation_code": """$allowed_docs = [
    'incoterms2020.html', 'bill_of_lading.html', 
    'customs_procedure.html', 'dangerous_goods.html'
];
$doc = basename($_GET['doc'] ?? 'incoterms2020.html');
if (!in_array($doc, $allowed_docs, true)) {
    die('<div class="sql-error">LỖI: Tài liệu không nằm trong danh mục cho phép!</div>');
}
include_once __DIR__ . '/../guides/' . $doc;""",
                "sac_title": "e. Đánh giá Vi phạm Chính sách & Bài toán Security-as-Code (SaC):",
                "sac_text": "• Pha DevSecOps: Pha Build & Quality Gate (Stage 2). Lỗi nằm ở module cẩm nang quy chuẩn, cho phép kẻ tấn công đọc tệp nhạy cảm ngoài phạm vi.\n• Căn cứ pháp lý: Nghị định 13/2023/NĐ-CP (Điều 13 K.2, Điều 26); GDPR (Article 5(1)(f) — Integrity & Confidentiality).\n• Hiện thực hóa Bài toán SaC: Tích hợp quy tắc SonarQube php:S2083 vào Quality Gate Rating A (ci/sonarqube.py check), từ chối đóng gói Docker image nếu phát hiện Path Traversal:",
                "sac_code": """// ci/sonarqube-quality-gate.json: Chặn đứng khi phát hiện lỗ hổng mức Blocker/Critical
{
  "conditions": [
    {"metric": "new_blocker_violations", "op": "GT", "error": "0"},
    {"metric": "new_critical_violations", "op": "GT", "error": "0"}
  ]
}"""
            },
            "cq": {
                "title": "Phần B: KIỂM ĐỊNH CHẤT LƯỢNG MÃ NGUỒN (SONARQUBE CODE QUALITY)",
                "sub_title": "CQ-01: Use 'include_once' Instead of 'include' (Reliability Bug)",
                "intro": "SonarQube Scanner được kích hoạt tại Stage 2 để kiểm soát độ tin cậy vận hành (Reliability), tiêu chuẩn định dạng mã nguồn sạch PSR-12 và an toàn thực thi tệp. Bất kỳ lỗi Bug nào đều sẽ kích hoạt cơ chế ngắt tiến trình (Break-the-Build).",
                "meta": [
                    ("Vị trí vi phạm", "InlaneWeb/web/src/pages/guide.php:56"),
                    ("Quy tắc SonarQube", "php:S2003 (Minor Bug)"),
                    ("Phân loại & Mức độ", "🐞 BUG | 🟡 MINOR"),
                    ("Tiêu chuẩn vi phạm", "SonarQube PHP Reliability Standard")
                ],
                "bad_code_title": "Bằng chứng mã nguồn vi phạm (Non-compliant Code):",
                "bad_code": """// Dòng 55-57 (InlaneWeb/web/src/pages/guide.php) - LỖI INCLUDE NẠP LẶP
include $doc;""",
                "analysis_title": "Cơ chế phân tích của SonarQube:",
                "analysis_text": "Bộ phân tích sonar-php-plugin phát hiện việc dùng câu lệnh include nạp tệp tài liệu thay vì include_once. Nếu tài liệu chứa các hàm trợ giúp hoặc hằng số được định nghĩa trong luồng xử lý trước đó, việc nạp lại sẽ gây lỗi Cannot redeclare function khiến tiến trình xử lý request bị gián đoạn.",
                "clean_code_title": "Phương án khắc phục chuẩn hóa (Clean Code Refactoring):",
                "clean_code": """// Dòng 55-57 (InlaneWeb/web/src/pages/guide.php) - MÃ NGUỒN ĐÃ KHẮC PHỤC
include_once __DIR__ . '/../guides/' . $doc;""",
                "metrics": [
                    ["Chỉ số Chất lượng (Metrics)", "Trước khi Sửa (Dirty State)", "Sau khi Sửa (Clean Code)", "Trạng thái Thẩm định"],
                    ["New Bugs", "1 (Minor)", "0", "✅ ĐẠT CHUẨN (= 0)"],
                    ["Reliability Rating", "B", "A", "✅ ĐẠT MỨC A"],
                    ["Maintainability Rating", "A", "A", "✅ DUY TRÌ MỨC A"],
                    ["SonarQube Quality Gate", "FAILED (Chặn Build)", "PASSED (Cho phép Merge)", "✅ HOÀN THÀNH"]
                ]
            }
        },

        # --- MEMBER 4: DUC ANH ---
        {
            "heading": "4.1.4. Lê Đức Anh — Order-By SQL Injection & Web Accessibility Form Smell",
            "role": "Sinh viên Lê Đức Anh đảm nhiệm vai trò Kỹ sư Tự động hóa Hạ tầng (Infrastructure Automation Engineer), chịu trách nhiệm phân hệ Quản lý hồ sơ vận đơn (account.php) và Kiểm định hạ tầng an toàn IaC. Phân hệ ghi nhận 01 lỗ hổng bảo mật và 01 lỗi chất lượng mã nguồn.",
            "vuln": {
                "title": "Phần A: CHI TIẾT LỖ HỔNG AN TOÀN BẢO MẬT (SAST — SEMGREP / OWASP / CWE)",
                "sub_title": "1. Order-By Clause SQL Injection tại trang Quản lý Hồ sơ & Vận đơn",
                "meta": [
                    ("Vị trí vi phạm", "InlaneWeb/web/src/pages/account.php:41"),
                    ("Phân loại lỗi", "Mã nguồn (Application Code)"),
                    ("Pha trong DevSecOps", "Pha Test / SAST Gate (Stage 2 trong CI/CD Pipeline)"),
                    ("Mã định danh điểm yếu", "CWE-89: SQL Injection | OWASP Top 10:2021: A03:2021 — Injection"),
                    ("Quy tắc phát hiện", "Semgrep Rule php.lang.security.injection.tainted-sql-string.tainted-sql-string")
                ],
                "vuln_code_title": "a. Bằng chứng mã nguồn vi phạm (Vulnerable Code):",
                "vuln_code": """// Source: Tham số ?order= được người dùng kiểm soát trên URL
$order = $_GET['order'] ?? 'id';

// Sink: Nối trực tiếp chuỗi vào mệnh đề ORDER BY mà không qua kiểm tra danh sách trắng
$sql = "SELECT tracking_no, port_code, status FROM shipments WHERE customer_id = "
     . intval($u['id']) . " ORDER BY $order";
echo '<div class="query-box">' . htmlspecialchars($sql) . '</div>';
$res = query($sql);""",
                "detection_title": "b. Cơ chế phát hiện & Trích xuất mã nguồn (Detection Mechanism):",
                "detection_text": "Quy tắc Semgrep quét phát hiện tham số URL $_GET['order'] được nối thẳng vào mệnh đề ORDER BY:",
                "semgrep_rule": """rules:
  - id: php.lang.security.injection.tainted-sql-string.tainted-sql-string
    languages: [php]
    severity: ERROR
    mode: taint
    pattern-sources:
      - pattern: $_GET[...]
    pattern-sinks:
      - pattern: query("... ORDER BY $ORDER", ...)""",
                "source_sink_text": "Cơ chế phân tích luồng ô nhiễm (Taint / AST Analysis) tự động trích xuất qua ci/semgrep_report.py:",
                "source_code": "// 🟡 SOURCE: Dòng 39 (InlaneWeb/web/src/pages/account.php):\n$order = $_GET['order'] ?? 'id';",
                "sink_code": "// 🔴 SINK: Dòng 41-45 (InlaneWeb/web/src/pages/account.php):\n$sql = \"SELECT tracking_no, port_code, status FROM shipments WHERE customer_id = \"\n     . intval($u['id']) . \" ORDER BY $order\";\n$res = query($sql);",
                "poc_title": "c. Kịch bản khai thác thực tế (PoC):",
                "poc_text": "Kẻ tấn công gửi tải trọng Boolean Blind hoặc trích xuất lỗi qua hàm extractvalue():",
                "poc_code": "GET /account?order=(CASE+WHEN+(SELECT+SUBSTR(password,1,1)+FROM+users+WHERE+username='admin')='a'+THEN+id+ELSE+port_code+END)\nGET /account?order=extractvalue(1,concat(0x7e,(SELECT+user())))",
                "poc_impact": "Hậu quả: Kẻ tấn công đoán từng ký tự mật khẩu băm của quản trị viên hệ thống hoặc trích xuất thông tin CSDL nội bộ.",
                "remediation_title": "d. Cách thức xử lý & Khắc phục (Remediation):",
                "remediation_text": "Áp dụng kỹ thuật Whitelist danh mục cột sắp xếp hợp lệ:",
                "remediation_code": """$allowed_columns = [
    'id'          => 'id',
    'tracking_no' => 'tracking_no',
    'port_code'   => 'port_code',
    'status'      => 'status'
];
$order_param = $_GET['order'] ?? 'id';
$safe_order = $allowed_columns[$order_param] ?? 'id';

$stmt = db()->prepare("SELECT tracking_no, port_code, status FROM shipments WHERE customer_id = ? ORDER BY " . $safe_order);
$stmt->bind_param("i", $u['id']);
$stmt->execute();
$res = $stmt->get_result();""",
                "sac_title": "e. Đánh giá Vi phạm Chính sách & Bài toán Security-as-Code (SaC):",
                "sac_text": "• Pha DevSecOps: Pha Test / SAST Gate (Stage 2). Mệnh đề ORDER BY không hỗ trợ dấu ? trong Prepared Statements, đòi hỏi cơ chế kiểm tra riêng biệt.\n• Căn cứ pháp lý: Nghị định 13/2023/NĐ-CP (Điều 9 K.2, Điều 26); GDPR (Article 32 — Security of Processing).\n• Hiện thực hóa Bài toán SaC: Xây dựng quy tắc Semgrep Taint phân tích riêng mệnh đề ORDER BY, ép buộc lập trình viên phải sử dụng danh mục whitelist tĩnh.",
                "sac_code": """# ci/semgrep-local-rules.yml (SaC kiểm tra ORDER BY)
- id: php-sqli-taint-order-by
  languages: [php]
  severity: ERROR
  mode: taint
  pattern-sources: [pattern: $_GET['order']]
  pattern-sinks: [pattern: query("... ORDER BY $ORDER", ...)]"""
            },
            "cq": {
                "title": "Phần B: KIỂM ĐỊNH CHẤT LƯỢNG MÃ NGUỒN (SONARQUBE CODE QUALITY)",
                "sub_title": "CQ-01: Form Label Not Associated With Input Control (Accessibility Code Smell)",
                "intro": "SonarQube Scanner được kích hoạt tại Stage 2 để kiểm soát toàn diện tiêu chuẩn trợ năng quốc tế WCAG 2.1 và chuẩn Clean Code. Lỗi trợ năng cấp Major được đánh giá là rào cản truy cập đối với thiết bị ngoại vi.",
                "meta": [
                    ("Vị trí vi phạm", "InlaneWeb/web/src/pages/account.php:28"),
                    ("Quy tắc SonarQube", "Web:S6853 (Major Code Smell)"),
                    ("Phân loại & Mức độ", "🧹 CODE_SMELL | 🟠 MAJOR"),
                    ("Tiêu chuẩn vi phạm", "WCAG 2.1 Level A (Criteria 1.3.1, 4.1.2) / ISO/IEC 40500:2012")
                ],
                "bad_code_title": "Bằng chứng mã nguồn vi phạm (Non-compliant Code):",
                "bad_code": """<!-- Dòng 27-30 (InlaneWeb/web/src/pages/account.php) - MÃ NGUỒN VI PHẠM -->
<div class="form-row">
    <label>Email</label>
    <input type="text" name="email" value="<?= htmlspecialchars($u['email']) ?>">
</div>""",
                "analysis_title": "Cơ chế phân tích của SonarQube:",
                "analysis_text": "Thẻ <label> không chứa thuộc tính for liên kết tới id của ô nhập liệu và cũng không bọc trực tiếp phần tử điều khiển. Điều này vi phạm nghiêm trọng tiêu chuẩn trợ năng quốc tế ISO/IEC 40500:2012.",
                "clean_code_title": "Phương án khắc phục chuẩn hóa (Clean Code Refactoring):",
                "clean_code": """<!-- Dòng 27-30 (InlaneWeb/web/src/pages/account.php) - MÃ NGUỒN ĐÃ KHẮC PHỤC -->
<div class="form-row">
    <label for="acc-email">Email</label>
    <input id="acc-email" type="text" name="email" value="<?= htmlspecialchars($u['email']) ?>">
</div>""",
                "metrics": [
                    ["Chỉ số Chất lượng (Metrics)", "Trước khi Sửa (Dirty State)", "Sau khi Sửa (Clean Code)", "Trạng thái Thẩm định"],
                    ["New Code Smells", "1 (Major)", "0", "✅ ĐẠT CHUẨN (= 0)"],
                    ["Accessibility Violations", "1", "0", "✅ ĐẠT ISO/IEC 40500"],
                    ["Maintainability Rating", "B", "A", "✅ ĐẠT MỨC A"],
                    ["SonarQube Quality Gate", "FAILED (Chặn Build)", "PASSED (Cho phép Merge)", "✅ HOÀN THÀNH"]
                ]
            }
        },

        # --- MEMBER 5: MAI ---
        {
            "heading": "4.1.5. Nguyễn Phương Mai — INSERT SQL Injection & Admin Dashboard Accessibility Bug",
            "role": "Sinh viên Nguyễn Phương Mai đảm nhiệm vai trò Kỹ sư Giám sát & Vận hành (Monitoring & SecOps Engineer), chịu trách nhiệm phân hệ Bình luận vận đơn (comment_add.php), Bảng điều khiển quản trị (admin_dashboard.php) và Cụm SIEM tập trung. Phân hệ ghi nhận 01 lỗ hổng bảo mật và 01 lỗi chất lượng mã nguồn.",
            "vuln": {
                "title": "Phần A: CHI TIẾT LỖ HỔNG AN TOÀN BẢO MẬT (SAST — SEMGREP / OWASP / CWE)",
                "sub_title": "1. INSERT Statement SQL Injection tại Module Thêm Bình luận Vận đơn",
                "meta": [
                    ("Vị trí vi phạm", "InlaneWeb/web/src/pages/comment_add.php:19"),
                    ("Phân loại lỗi", "Mã nguồn (Application Code)"),
                    ("Pha trong DevSecOps", "Pha Test / SAST Gate (Stage 2 trong CI/CD Pipeline)"),
                    ("Mã định danh điểm yếu", "CWE-89: SQL Injection | OWASP Top 10:2021: A03:2021 — Injection"),
                    ("Quy tắc phát hiện", "Semgrep Rule php.lang.security.injection.tainted-sql-string.tainted-sql-string")
                ],
                "vuln_code_title": "a. Bằng chứng mã nguồn vi phạm (Vulnerable Code):",
                "vuln_code": """$shipment_id = intval($_GET['shipment_id'] ?? 0);
$content     = $_POST['content'] ?? '';

// Sink: Nối thẳng chuỗi $content từ người dùng vào mệnh đề VALUES(...)
$sql = "INSERT INTO comments (shipment_id, user_id, content) VALUES "
     . "($shipment_id, " . intval($u['id']) . ", '$content')";

render_header('Thêm bình luận');
echo '<div class="card"><h1>Thêm bình luận</h1>';
echo '<div class="query-box">' . htmlspecialchars($sql) . '</div>';

if (exec_write($sql)) {
    flash('Đã thêm bình luận.', 'success');
}""",
                "detection_title": "b. Cơ chế phát hiện & Trích xuất mã nguồn (Detection Mechanism):",
                "detection_text": "Quy tắc Semgrep quét phát hiện nhận diện dữ liệu $content từ biểu mẫu POST nối trực tiếp vào mệnh đề VALUES(...) của lệnh INSERT INTO:",
                "semgrep_rule": """rules:
  - id: php.lang.security.injection.tainted-sql-string.tainted-sql-string
    languages: [php]
    severity: ERROR
    mode: taint
    pattern-sources:
      - pattern: $_POST[...]
    pattern-sinks:
      - pattern: exec_write("INSERT INTO ... VALUES (..., '$CONTENT')", ...)""",
                "source_sink_text": "Cơ chế phân tích luồng ô nhiễm (Taint / AST Analysis) tự động trích xuất qua ci/semgrep_report.py:",
                "source_code": "// 🟡 SOURCE: Dòng 15-16 (InlaneWeb/web/src/pages/comment_add.php):\n$shipment_id = intval($_GET['shipment_id'] ?? 0);\n$content     = $_POST['content'] ?? '';",
                "sink_code": "// 🔴 SINK: Dòng 19-20, 26 (InlaneWeb/web/src/pages/comment_add.php):\n$sql = \"INSERT INTO comments (shipment_id, user_id, content) VALUES \"\n     . \"($shipment_id, \" . intval($u['id']) . \", '$content')\";\nif (exec_write($sql)) {",
                "poc_title": "c. Kịch bản khai thác thực tế (PoC):",
                "poc_text": "Kẻ tấn công đóng sớm mệnh đề VALUES để chèn thêm Subquery trích xuất mật khẩu quản trị:",
                "poc_code": "POST /shipments/1/comments\ncontent=test', 1), (1, 1, (SELECT password FROM users WHERE username='admin'))-- -",
                "poc_impact": "Hậu quả: Mật khẩu quản trị viên bị chèn thẳng vào bảng bình luận và hiển thị công khai trên giao diện chi tiết vận đơn.",
                "remediation_title": "d. Cách thức xử lý & Khắc phục (Remediation):",
                "remediation_text": "Chuyển đổi sang Prepared Statement cho thao tác ghi dữ liệu bảo đảm an toàn tuyệt đối:",
                "remediation_code": """$stmt = db()->prepare("INSERT INTO comments (shipment_id, user_id, content) VALUES (?, ?, ?)");
$uid = intval($u['id']);
$stmt->bind_param("iis", $shipment_id, $uid, $content);
if ($stmt->execute()) {
    flash('Đã thêm bình luận thành công.', 'success');
}""",
                "sac_title": "e. Đánh giá Vi phạm Chính sách & Bài toán Security-as-Code (SaC):",
                "sac_text": "• Pha DevSecOps: Pha Test / SAST Gate (Stage 2). Lỗi chèn dữ liệu không kiểm soát dẫn đến rò rỉ thông tin cá nhân và tài khoản trên giao diện công cộng.\n• Căn cứ pháp lý: Nghị định 13/2023/NĐ-CP (Điều 9 K.2, Điều 17); GDPR (Article 32 & Article 33 về nghĩa vụ thông báo vi phạm dữ liệu trong 72 giờ).\n• Hiện thực hóa Bài toán SaC: Chốt chặn Semgrep quét phát hiện mọi câu lệnh INSERT INTO chứa biến chuỗi không qua tham số hóa, ngắt pipeline ngay từ Stage 2:",
                "sac_code": """# Chốt chặn SaC phát hiện INSERT SQL Injection
- id: php.lang.security.injection.tainted-sql-string.tainted-sql-string
  languages: [php]
  severity: ERROR
  mode: taint
  pattern-sources: [pattern: $_POST['content']]
  pattern-sinks: [pattern: exec_write("INSERT INTO ... VALUES ($SINK)", ...)]"""
            },
            "cq": {
                "title": "Phần B: KIỂM ĐỊNH CHẤT LƯỢNG MÃ NGUỒN (SONARQUBE CODE QUALITY)",
                "sub_title": "CQ-01: Admin Log Filter Input Without Associated Label (Accessibility Bug)",
                "intro": "SonarQube Scanner được kích hoạt tại Stage 2 để kiểm soát chất lượng mã nguồn và tiêu chuẩn trợ năng giao diện quản trị WCAG 2.1.",
                "meta": [
                    ("Vị trí vi phạm", "InlaneWeb/web/src/pages/admin_dashboard.php:26"),
                    ("Quy tắc SonarQube", "Web:InputWithoutLabelCheck (Major Bug)"),
                    ("Phân loại & Mức độ", "🐞 BUG | 🟠 MAJOR"),
                    ("Tiêu chuẩn vi phạm", "WCAG 2.1 Level A (Criteria 1.3.1, 4.1.2) / ISO/IEC 40500:2012")
                ],
                "bad_code_title": "Bằng chứng mã nguồn vi phạm (Non-compliant Code):",
                "bad_code": """<!-- Dòng 25-27 (InlaneWeb/web/src/pages/admin_dashboard.php) - MÃ NGUỒN VI PHẠM -->
<form method="get" action="/admin">
    <input type="text" name="filter" value="<?= htmlspecialchars($filter) ?>" placeholder="Lọc theo hành động hoặc username...">
    <button class="btn" type="submit">Lọc nhật ký</button>
</form>""",
                "analysis_title": "Cơ chế phân tích của SonarQube:",
                "analysis_text": "Ô nhập liệu tìm kiếm log trên dashboard quản trị thiếu hoàn toàn thuộc tính id và nhãn <label>, vi phạm nguyên tắc trợ năng WCAG 2.1.",
                "clean_code_title": "Phương án khắc phục chuẩn hóa (Clean Code Refactoring):",
                "clean_code": """<!-- Dòng 25-28 (InlaneWeb/web/src/pages/admin_dashboard.php) - MÃ NGUỒN ĐÃ KHẮC PHỤC -->
<form method="get" action="/admin">
    <label for="admin-filter-log" class="form-label sr-only">Lọc nhật ký quản trị:</label>
    <input id="admin-filter-log" type="text" name="filter" value="<?= htmlspecialchars($filter) ?>" placeholder="Lọc theo hành động hoặc username...">
    <button class="btn" type="submit">Lọc nhật ký</button>
</form>""",
                "metrics": [
                    ["Chỉ số Chất lượng (Metrics)", "Trước khi Sửa (Dirty State)", "Sau khi Sửa (Clean Code)", "Trạng thái Thẩm định"],
                    ["New Bugs", "1 (Major)", "0", "✅ ĐẠT CHUẨN (= 0)"],
                    ["Accessibility Violations", "1", "0", "✅ ĐẠT ISO/IEC 40500"],
                    ["Reliability Rating", "A", "A", "✅ DUY TRÌ MỨC A"],
                    ["SonarQube Quality Gate", "FAILED (Chặn Build)", "PASSED (Cho phép Merge)", "✅ HOÀN THÀNH"]
                ]
            }
        }
    ]

    # Insert structured content for all 5 members before p_end
    for m in rich_members:
        # Heading CTDT-H3
        p_target_h3 = p_end.insert_paragraph_before(m["heading"], style="CTDT-H3")
        
        # Role text
        add_body_text(p_end, m["role"])
        
        # --- Part A: Vuln ---
        v = m["vuln"]
        add_section_header(p_end, v["title"], level=1)
        add_section_header(p_end, v["sub_title"], level=2)
        
        for k, val in v["meta"]:
            add_meta_line(p_end, k, val)
            
        add_section_header(p_end, v["vuln_code_title"], level=2)
        add_code_box(doc, p_end, v["vuln_code"])
        
        add_section_header(p_end, v["detection_title"], level=2)
        add_body_text(p_end, v["detection_text"], indent=True)
        add_code_box(doc, p_end, v["semgrep_rule"])
        
        add_body_text(p_end, v["source_sink_text"], indent=True)
        add_code_box(doc, p_end, v["source_code"])
        add_code_box(doc, p_end, v["sink_code"])
        
        add_section_header(p_end, v["poc_title"], level=2)
        add_body_text(p_end, v["poc_text"], indent=True)
        add_code_box(doc, p_end, v["poc_code"])
        add_body_text(p_end, v["poc_impact"], indent=True)
        
        add_section_header(p_end, v["remediation_title"], level=2)
        add_body_text(p_end, v["remediation_text"], indent=True)
        add_code_box(doc, p_end, v["remediation_code"])
        
        add_section_header(p_end, v["sac_title"], level=2)
        add_body_text(p_end, v["sac_text"], indent=True)
        add_code_box(doc, p_end, v["sac_code"])
        
        # --- Part B: Code Quality ---
        cq = m["cq"]
        add_section_header(p_end, cq["title"], level=1)
        add_body_text(p_end, cq["intro"])
        add_section_header(p_end, cq["sub_title"], level=2)
        
        for k, val in cq["meta"]:
            add_meta_line(p_end, k, val)
            
        add_section_header(p_end, cq["bad_code_title"], level=2)
        add_code_box(doc, p_end, cq["bad_code"])
        
        add_section_header(p_end, cq["analysis_title"], level=2)
        add_body_text(p_end, cq["analysis_text"], indent=True)
        
        add_section_header(p_end, cq["clean_code_title"], level=2)
        add_code_box(doc, p_end, cq["clean_code"])
        
        add_section_header(p_end, "Kết quả Thẩm định Chất lượng SonarQube Trước & Sau Khắc phục:", level=2)
        add_metrics_table(doc, p_end, cq["metrics"])
        
        # Empty separator line
        add_body_text(p_end, "")

    # Now delete old paragraphs that were between p_start and the newly inserted content
    # Find all paragraphs from p_start up to the new start
    to_remove = []
    collecting = False
    for p in doc.paragraphs:
        if p == p_start:
            collecting = True
        if p.style.name == "CTDT-H3" and "4.1.1. Nguyễn Giang Nam (Trưởng nhóm) — In-band UNION SQL Injection & Accessibility" in p.text:
            break
        if collecting:
            to_remove.append(p)
            
    print(f"Removing {len(to_remove)} old paragraphs...")
    for p in to_remove:
        p._element.getparent().remove(p._element)

    doc.save(docx_path)
    print("Successfully saved rich docx document!")

if __name__ == "__main__":
    render_rich_docx()
