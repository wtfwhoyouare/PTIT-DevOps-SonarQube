import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_presentation():
    prs = pptx.Presentation()
    # 16:9 Widescreen layout
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    blank_layout = prs.slide_layouts[6]
    
    # Color palette
    NAVY = RGBColor(0, 51, 102)        # #003366 - PTIT Primary Navy
    CRIMSON = RGBColor(192, 57, 43)    # #C0392B - PTIT Red Accent
    DARK = RGBColor(33, 37, 41)        # #212529 - Text Dark
    MUTED = RGBColor(108, 117, 125)    # #6C757D - Muted Gray
    LIGHT_BG = RGBColor(248, 249, 250) # #F8F9FA - Card Background
    BORDER = RGBColor(222, 226, 230)   # #DEE2E6 - Border
    WHITE = RGBColor(255, 255, 255)
    BLUE_ACCENT = RGBColor(9, 105, 218)
    GREEN = RGBColor(40, 167, 69)

    def add_header(slide, title, category="HỌC PHẦN DEVSECOPS (SEC4342) — NHÓM 11"):
        # Category label
        tb_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
        tf_cat = tb_cat.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.name = "Arial"
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = CRIMSON
        
        # Main Title
        tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.6))
        tf_title = tb_title.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title
        p_title.font.name = "Arial"
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = NAVY
        
        # Bottom divider
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.35), Inches(11.733), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = BORDER
        line.line.color.rgb = BORDER

    def add_card(slide, left, top, width, height, bg_color=LIGHT_BG, border_color=BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1)
        return card

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    # Background full navy
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = NAVY
    bg1.line.color.rgb = NAVY
    
    # Accent top banner
    top_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.15))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = CRIMSON
    top_bar.line.color.rgb = CRIMSON
    
    tb1 = s1.shapes.add_textbox(Inches(1.2), Inches(1.5), Inches(11.0), Inches(4.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "HỌC VIỆN CÔNG NGHỆ BƯU CHÍNH VIỄN THÔNG — KHOA AN TOÀN THÔNG TIN"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.space_after = Pt(24)
    
    p = tf1.add_paragraph()
    p.text = "BÁO CÁO BÀI TẬP LỚN DEVSECOPS"
    p.font.name = "Arial"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.space_after = Pt(14)
    
    p = tf1.add_paragraph()
    p.text = "Kiểm định Mã nguồn, Giám sát Tập trung và Triển khai Production\ncho Hệ thống Cổng Thông tin Vận tải InlaneWeb Logistics"
    p.font.name = "Arial"
    p.font.size = Pt(18)
    p.font.color.rgb = RGBColor(220, 230, 245)
    p.space_after = Pt(36)
    
    p = tf1.add_paragraph()
    p.text = "Giảng viên hướng dẫn: TS. Phạm Hoàng Duy   |   Học phần: DevOps & DevSecOps (SEC4342)"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.space_after = Pt(8)

    p = tf1.add_paragraph()
    p.text = "Nhóm thực hiện: Nhóm 11 — Lớp: M26CQAT01-B   |   Trưởng nhóm: Nguyễn Giang Nam (B26CHAT030)"
    p.font.name = "Arial"
    p.font.size = Pt(12)
    p.font.color.rgb = RGBColor(200, 215, 235)

    # =========================================================================
    # SLIDE 2: AGENDA
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Nội dung Báo cáo & Lộ trình Trình bày")
    
    agenda_items = [
        ("I", "Kiến trúc Ứng dụng Web & Ranh giới An ninh", "Khảo sát ứng dụng InlaneWeb Logistics, luồng dữ liệu nghiệp vụ và mô hình bảo vệ dữ liệu cá nhân theo Nghị định 13/2023 & GDPR."),
        ("II", "Hạ tầng Triển khai & Hệ thống Giám sát", "Kiến trúc mạng Docker cô lập, đóng gói bất biến GHCR, cụm giám sát Promtail + Loki + Grafana và cơ chế tự phục hồi Autoheal."),
        ("III", "Đường ống DevSecOps CI/CD 4 Cổng Kiểm soát", "Thiết kế chuỗi kiểm định tự động: Stage 1 Policy Guard, Stage 2 Dual-Gate (SonarQube & Semgrep SAST), Stage 3 Smoke Test, Stage 4 CD."),
        ("IV", "Chi tiết Phân công Nhiệm vụ & Kết quả 5 Thành viên", "Mỗi thành viên phụ trách 1 Lỗ hổng An ninh (CWE/OWASP) và 1 Lỗi Chất lượng mã nguồn (Clean Code Bug/Smell), kèm PoC và bản vá an toàn."),
        ("V", "Bảng Tổng hợp Chính sách An toàn & Kết luận", "Ma trận 16 điều khoản chính sách kỹ thuật, tổng kết các giá trị thực tiễn và nguyên tắc Shift-Left Security.")
    ]
    
    top_pos = 1.6
    for num, title, desc in agenda_items:
        add_card(s2, Inches(0.8), Inches(top_pos), Inches(11.733), Inches(0.95))
        
        # Badge
        b = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(top_pos + 0.15), Inches(0.65), Inches(0.65))
        b.fill.solid()
        b.fill.fore_color.rgb = NAVY
        b.line.color.rgb = NAVY
        b_p = b.text_frame.paragraphs[0]
        b_p.text = num
        b_p.font.name = "Arial"
        b_p.font.size = Pt(14)
        b_p.font.bold = True
        b_p.font.color.rgb = WHITE
        b_p.alignment = PP_ALIGN.CENTER
        
        # Text
        tb = s2.shapes.add_textbox(Inches(1.85), Inches(top_pos + 0.08), Inches(10.5), Inches(0.8))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = "Arial"
        p1.font.size = Pt(14)
        p1.font.bold = True
        p1.font.color.rgb = NAVY
        
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.name = "Arial"
        p2.font.size = Pt(11)
        p2.font.color.rgb = DARK
        
        top_pos += 1.1

    # =========================================================================
    # SLIDE 3: WEB ARCHITECTURE & DFD
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "I. Kiến trúc Ứng dụng Web InlaneWeb & Ranh giới Tin cậy")
    
    # Left Card: Info
    add_card(s3, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.4))
    tb3 = s3.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(5.2), Inches(5.1))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    
    p = tf3.paragraphs[0]
    p.text = "Cổng Thông tin Vận tải Biển InlaneWeb"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(12)
    
    points_s3 = [
        ("Nền tảng công nghệ", "Apache Web Server + PHP 8.2 kết nối cơ sở dữ liệu quan hệ MariaDB 10.11."),
        ("Nghiệp vụ cốt lõi", "Tra cứu hải trình & cảng biển (/ports), theo dõi vận đơn (/shipments), đăng nhập tài khoản (/login), bình luận tương tác (/comments), cẩm nang quy chuẩn (/guide), bảng quản trị (/admin)."),
        ("Ranh giới tin cậy (Trust Boundaries)", "Phân tách rõ 3 vùng: Public Zone (Người dùng Internet), Application Container Zone (Vùng xử lý nghiệp vụ) và Database Storage Zone (Vùng lưu trữ dữ liệu nội bộ)."),
        ("Phân loại dữ liệu cần bảo vệ (PII)", "Họ tên, email khách hàng, mật khẩu quản trị băm, thông tin vận đơn hàng hải và lịch sử giao dịch logistics."),
        ("Khung pháp lý áp dụng", "Nghị định 13/2023/NĐ-CP (Điều 9, 13, 26) và Quy định GDPR (Article 25 — Data Protection by Design & Article 32 — Security of Processing).")
    ]
    for lbl, val in points_s3:
        p = tf3.add_paragraph()
        p.text = f"• {lbl}: "
        p.font.name = "Arial"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = CRIMSON
        
        r = p.add_run()
        r.text = val
        r.font.name = "Arial"
        r.font.size = Pt(10.5)
        r.font.bold = False
        r.font.color.rgb = DARK
        p.space_after = Pt(8)

    # Right Card: Diagram
    add_card(s3, Inches(6.6), Inches(1.6), Inches(5.933), Inches(5.4))
    dfd_img = "cai-tien-bao-cao/hinh/v1-dfd-ranh-gioi-tin-cay.png"
    if os.path.exists(dfd_img):
        s3.shapes.add_picture(dfd_img, Inches(6.8), Inches(1.8), width=Inches(5.533))

    # =========================================================================
    # SLIDE 4: INFRASTRUCTURE & DOCKER DEPLOYMENT
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "II. Kiến trúc Hạ tầng Triển khai & Mạng Docker Cô lập")
    
    # Left Card: Diagram
    add_card(s4, Inches(0.8), Inches(1.6), Inches(5.933), Inches(5.4))
    gitops_img = "cai-tien-bao-cao/hinh/v4-gitops-push-pull.png"
    if os.path.exists(gitops_img):
        s4.shapes.add_picture(gitops_img, Inches(1.0), Inches(1.85), width=Inches(5.533))

    # Right Card: Text Info
    add_card(s4, Inches(6.9), Inches(1.6), Inches(5.633), Inches(5.4))
    tb4 = s4.shapes.add_textbox(Inches(7.1), Inches(1.75), Inches(5.2), Inches(5.1))
    tf4 = tb4.text_frame
    tf4.word_wrap = True
    
    p = tf4.paragraphs[0]
    p.text = "Thiết kế Hạ tầng Môi trường Production"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(12)
    
    points_s4 = [
        ("Mạng Docker cô lập (inlaneweb_net)", "Ứng dụng Web và MariaDB giao tiếp thông qua mạng bridge nội bộ riêng biệt, ngăn chặn hoàn toàn truy cập ngang hàng trái phép."),
        ("Chính sách Không lộ cổng CSDL (Non-exposed Port)", "Tuyệt đối cấm ánh xạ cổng 3306 của MariaDB ra ngoài môi trường Internet; cổng chỉ được expose nội bộ cho container ilfreight_web."),
        ("Đóng gói bất biến qua GHCR", "Toàn bộ Docker Images sau khi vượt qua Stage 3 đều được lưu trữ trên GitHub Packages với tag kép: :latest và commit SHA :${{ github.sha }} phục vụ truy vết."),
        ("Triển khai Decoupled Zero-Downtime", "Tách rời 2 dự án compose: inlaneweb-prod (Web app) và inlaneweb-monitoring (Giám sát). Khi cập nhật mã nguồn ứng dụng web, hệ thống ghi log 24/7 duy trì hoạt động liên tục."),
        ("Cơ chế tự phục hồi (Self-Healing)", "Container ilfreight_autoheal kiểm tra nhịp tim định kỳ và tự động khởi động lại dịch vụ web nếu endpoint /health bị lỗi.")
    ]
    for lbl, val in points_s4:
        p = tf4.add_paragraph()
        p.text = f"• {lbl}: "
        p.font.name = "Arial"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = BLUE_ACCENT
        
        r = p.add_run()
        r.text = val
        r.font.name = "Arial"
        r.font.size = Pt(10.5)
        r.font.bold = False
        r.font.color.rgb = DARK
        p.space_after = Pt(8)

    # =========================================================================
    # SLIDE 5: OBSERVABILITY & SIEM MONITORING
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "II. Nền tảng Giám sát Tập trung & Tuân thủ Báo cáo 72h")
    
    # Left Card: Info
    add_card(s5, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.4))
    tb5 = s5.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(5.2), Inches(5.1))
    tf5 = tb5.text_frame
    tf5.word_wrap = True
    
    p = tf5.paragraphs[0]
    p.text = "Cụm Giám sát Quan sát (Promtail - Loki - Grafana)"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(12)
    
    points_s5 = [
        ("Thu thập Log có cấu trúc (JSON Format)", "Apache được cấu hình ghi log dạng JSON bao gồm: client_ip, uri, query string, status, user_agent và response_time, bảo toàn 100% dữ liệu điều tra."),
        ("Tập trung hóa qua Loki 3.0", "Promtail đọc log trực tiếp từ Docker socket và đẩy về cụm lưu trữ Loki theo thời gian thực."),
        ("8 Panel Giám sát SIEM trên Grafana", "Thiết lập các bộ lọc LogQL nhận diện ngay lập tức các hành vi tấn công: SQL Injection, Path Traversal (LFI), XSS và quét dò lỗ hổng."),
        ("Nghĩa vụ Báo cáo Sự cố An ninh 72h", "Căn cứ Điều 13, 17 Nghị định 13/2023/NĐ-CP và Article 33 GDPR: Khi xảy ra rò rỉ dữ liệu cá nhân, doanh nghiệp bắt buộc phải lập hồ sơ báo cáo cơ quan chức năng trong vòng 72 giờ."),
        ("Kiểm định thực tế", "Đã xác thực luồng log và dashboard hoạt động thành công trên môi trường Production VPS thực tế.")
    ]
    for lbl, val in points_s5:
        p = tf5.add_paragraph()
        p.text = f"• {lbl}: "
        p.font.name = "Arial"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = GREEN
        
        r = p.add_run()
        r.text = val
        r.font.name = "Arial"
        r.font.size = Pt(10.5)
        r.font.bold = False
        r.font.color.rgb = DARK
        p.space_after = Pt(8)

    # Right Card: Grafana verification image
    add_card(s5, Inches(6.6), Inches(1.6), Inches(5.933), Inches(5.4))
    grafana_img = "docs/images/hinh_2_6_grafana_cd_verification.png"
    if os.path.exists(grafana_img):
        s5.shapes.add_picture(grafana_img, Inches(6.8), Inches(1.8), width=Inches(5.533))

    # =========================================================================
    # SLIDE 6: CI/CD PIPELINE 4 STAGES
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "III. Đường ống DevSecOps CI/CD — 4 Cổng Kiểm soát (Dual-Gate)")
    
    # Left Card: Diagram
    add_card(s6, Inches(0.8), Inches(1.6), Inches(6.2), Inches(5.4))
    pipeline_img = "cai-tien-bao-cao/hinh/v3-chuoi-cong.png"
    if os.path.exists(pipeline_img):
        s6.shapes.add_picture(pipeline_img, Inches(0.95), Inches(1.75), width=Inches(5.9))

    # Right Card: Description of 4 stages
    add_card(s6, Inches(7.2), Inches(1.6), Inches(5.333), Inches(5.4))
    tb6 = s6.shapes.add_textbox(Inches(7.4), Inches(1.75), Inches(4.9), Inches(5.1))
    tf6 = tb6.text_frame
    tf6.word_wrap = True
    
    p = tf6.paragraphs[0]
    p.text = "Cơ chế Chốt chặn An ninh Tự động hóa"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(12)
    
    stages_desc = [
        ("Stage 1: Policy Guard", "Kiểm soát phân nhánh, bắt buộc Conventional Commits (feat, fix, sec) và tiêu chuẩn PR định danh thành viên [namng] (ci/policy_guard.py)."),
        ("Stage 2: Dev Gate (Dual-Gate)", "Chốt chặn kép: SonarQube Scanner kiểm định chất lượng Clean Code PSR, độ tin cậy và trợ năng; Semgrep SAST quét chuyên sâu OWASP/CWE và kích hoạt Break-the-Build khi có lỗi ERROR."),
        ("Stage 3: Production Gate", "Thẩm định cú pháp IaC (ci/validate_configs.py), khởi tạo môi trường thử nghiệm tạm thời (Ephemeral Preview), kiểm tra nhịp tim E2E (/health HTTP 200) và đẩy ảnh lên GHCR."),
        ("Stage 4: Production CD", "Tự động kết nối SSH/SCP triển khai an toàn lên VPS. Tách rời luồng Web và Logging, bảo đảm Zero-Downtime.")
    ]
    for st_title, st_detail in stages_desc:
        p = tf6.add_paragraph()
        p.text = f"▶ {st_title}: "
        p.font.name = "Arial"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = CRIMSON
        
        r = p.add_run()
        r.text = st_detail
        r.font.name = "Arial"
        r.font.size = Pt(10.5)
        r.font.bold = False
        r.font.color.rgb = DARK
        p.space_after = Pt(8)

    # =========================================================================
    # HELPER FOR MEMBER SLIDES
    # =========================================================================
    def create_member_slide(m_num, m_name, m_role, m_scope, vuln_info, cq_info):
        s = prs.slides.add_slide(blank_layout)
        add_header(s, f"IV. Nhiệm vụ Thành viên {m_num}: {m_name}")
        
        # Sub-header bar: Role & Scope
        bar = add_card(s, Inches(0.8), Inches(1.5), Inches(11.733), Inches(0.55), bg_color=NAVY, border_color=NAVY)
        tb_bar = s.shapes.add_textbox(Inches(1.0), Inches(1.55), Inches(11.3), Inches(0.45))
        tf_bar = tb_bar.text_frame
        p_bar = tf_bar.paragraphs[0]
        p_bar.text = f"Vai trò: {m_role}   |   Phân hệ phụ trách: {m_scope}"
        p_bar.font.name = "Arial"
        p_bar.font.size = Pt(11.5)
        p_bar.font.bold = True
        p_bar.font.color.rgb = WHITE
        
        # LEFT CARD: VULNERABILITY (SAST - SEMGREP)
        add_card(s, Inches(0.8), Inches(2.2), Inches(5.7), Inches(4.8))
        tb_v = s.shapes.add_textbox(Inches(0.95), Inches(2.3), Inches(5.4), Inches(4.6))
        tf_v = tb_v.text_frame
        tf_v.word_wrap = True
        
        pv = tf_v.paragraphs[0]
        pv.text = "1. LỖ HỔNG AN NINH BẢO MẬT (SAST SEMGREP)"
        pv.font.name = "Arial"
        pv.font.size = Pt(13)
        pv.font.bold = True
        pv.font.color.rgb = CRIMSON
        pv.space_after = Pt(8)
        
        for k, v in vuln_info["meta"]:
            p = tf_v.add_paragraph()
            p.text = f"• {k}: "
            p.font.name = "Arial"
            p.font.size = Pt(10)
            p.font.bold = True
            p.font.color.rgb = DARK
            r = p.add_run()
            r.text = v
            r.font.bold = False
            p.space_after = Pt(3)
            
        p = tf_v.add_paragraph()
        p.text = "Mã nguồn vi phạm (Vulnerable Code):"
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p.space_after = Pt(2)
        
        p = tf_v.add_paragraph()
        p.text = vuln_info["code_snippet"]
        p.font.name = "Consolas"
        p.font.size = Pt(8.5)
        p.font.color.rgb = RGBColor(160, 20, 20)
        p.space_after = Pt(6)
        
        p = tf_v.add_paragraph()
        p.text = f"▶ Biện pháp khắc phục: {vuln_info['fix_summary']}"
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = GREEN
        p.space_after = Pt(4)
        
        p = tf_v.add_paragraph()
        p.text = f"▶ Căn cứ pháp lý: {vuln_info['legal']}"
        p.font.name = "Arial"
        p.font.size = Pt(9.5)
        p.font.color.rgb = DARK

        # RIGHT CARD: CODE QUALITY (SONARQUBE)
        add_card(s, Inches(6.8), Inches(2.2), Inches(5.733), Inches(4.8))
        tb_q = s.shapes.add_textbox(Inches(6.95), Inches(2.3), Inches(5.4), Inches(4.6))
        tf_q = tb_q.text_frame
        tf_q.word_wrap = True
        
        pq = tf_q.paragraphs[0]
        pq.text = "2. CHẤT LƯỢNG MÃ NGUỒN (SONARQUBE QUALITY)"
        pq.font.name = "Arial"
        pq.font.size = Pt(13)
        pq.font.bold = True
        pq.font.color.rgb = NAVY
        pq.space_after = Pt(8)
        
        for k, v in cq_info["meta"]:
            p = tf_q.add_paragraph()
            p.text = f"• {k}: "
            p.font.name = "Arial"
            p.font.size = Pt(10)
            p.font.bold = True
            p.font.color.rgb = DARK
            r = p.add_run()
            r.text = v
            r.font.bold = False
            p.space_after = Pt(3)
            
        p = tf_q.add_paragraph()
        p.text = "Cơ chế phân tích & Vi phạm quy chuẩn:"
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p.space_after = Pt(2)
        
        p = tf_q.add_paragraph()
        p.text = cq_info["analysis"]
        p.font.name = "Arial"
        p.font.size = Pt(9.5)
        p.font.color.rgb = DARK
        p.space_after = Pt(6)
        
        p = tf_q.add_paragraph()
        p.text = f"▶ Phương án Refactoring: {cq_info['fix']}"
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = GREEN
        p.space_after = Pt(6)
        
        p = tf_q.add_paragraph()
        p.text = f"▶ Kết quả Quality Gate: {cq_info['result']}"
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = BLUE_ACCENT
        
        return s

    # =========================================================================
    # SLIDE 7: MEMBER 1 - NGUYEN GIANG NAM
    # =========================================================================
    create_member_slide(
        1, "Nguyễn Giang Nam (Trưởng nhóm)",
        "Kiến trúc sư DevSecOps & Lead Architect",
        "Quản trị luồng CI/CD, Quy chuẩn nhánh & Tra cứu cảng biển (ports.php)",
        {
            "meta": [
                ("Tên lỗ hổng", "In-band UNION SQL Injection tại tra cứu cảng biển"),
                ("Vị trí vi phạm", "InlaneWeb/web/src/pages/ports.php:38"),
                ("Mã điểm yếu", "CWE-89: SQL Injection | OWASP Top 10: A03:2021"),
                ("Quy tắc phát hiện", "Semgrep Rule tainted-sql-string (Mode: Taint)")
            ],
            "code_snippet": "$q = $_GET['q'] ?? '';\n$sql = \"SELECT code, city, volume FROM ports WHERE code LIKE '%$q%'\";\n$res = query($sql); // Điểm chìm Sink",
            "fix_summary": "Tái cấu trúc 100% sang Prepared Statements tham số hóa: $stmt = db()->prepare(\"... LIKE ?\"); $stmt->bind_param(\"s\", $q);",
            "legal": "Nghị định 13/2023/NĐ-CP (Điều 9 K.2, Điều 26) & GDPR Art. 32 (Security of Processing)."
        },
        {
            "meta": [
                ("Mã vấn đề", "CQ-01: Input Control Missing ID & Associated Label"),
                ("Vị trí vi phạm", "InlaneWeb/web/src/pages/ports.php:26"),
                ("Quy tắc SonarQube", "Web:InputWithoutLabelCheck (Major Bug)"),
                ("Tiêu chuẩn vi phạm", "WCAG 2.1 Level A (Criteria 1.3.1, 4.1.2) / ISO/IEC 40500")
            ],
            "analysis": "Bộ phân tích DOM Tree phát hiện ô input tìm kiếm thiếu thuộc tính id liên kết với thẻ <label>, làm vô hiệu hóa thiết bị trợ năng cho người khuyết tật (Screen Readers).",
            "fix": "Bổ sung thẻ <label for=\"port-search-input\" class=\"sr-only\"> đồng bộ thuộc tính id.",
            "result": "New Bugs giảm từ 1 về 0, Reliability Rating đạt A, Quality Gate chuyển FAILED sang PASSED."
        }
    )

    # =========================================================================
    # SLIDE 8: MEMBER 2 - NGUYEN DINH HAI
    # =========================================================================
    create_member_slide(
        2, "Nguyễn Đình Hải",
        "Kỹ sư An ninh Phần mềm (Application Security Engineer)",
        "Module Xác thực Người dùng (login.php) & Phân tích luồng ô nhiễm Taint",
        {
            "meta": [
                ("Tên lỗ hổng", "Authentication Bypass SQL Injection tại Đăng nhập"),
                ("Vị trí vi phạm", "InlaneWeb/web/src/pages/login.php:19"),
                ("Mã điểm yếu", "CWE-89: SQL Injection | OWASP Top 10: A03:2021"),
                ("Quy tắc phát hiện", "Semgrep Taint Rule tainted-sql-string")
            ],
            "code_snippet": "$sql = \"SELECT id, username FROM users WHERE username = '$username' AND password = '$password'\";\n$row = query_one($sql);",
            "fix_summary": "Tách biệt câu truy vấn tìm user bằng Prepared Statement và so khớp mật khẩu qua hàm băm an toàn Bcrypt password_verify().",
            "legal": "Nghị định 13/2023/NĐ-CP (Điều 9 K.2, Điều 17) & GDPR Art. 32 (Nguy cơ chiếm đoạt phiên admin)."
        },
        {
            "meta": [
                ("Mã vấn đề", "CQ-01: Missing Curly Braces in Nested Statement"),
                ("Vị trí vi phạm", "InlaneWeb/web/src/pages/login.php:36"),
                ("Quy tắc SonarQube", "php:S121 (Critical Code Smell)"),
                ("Tiêu chuẩn vi phạm", "PSR-12 Control Structures Standard / Clean Code")
            ],
            "analysis": "Khối lệnh if lồng nhau không dùng cặp dấu ngoặc nhọn { } bao bọc, vi phạm tiêu chuẩn PSR-12 và dễ gây lỗi logic rẽ nhánh nguy hiểm khi bảo trì.",
            "fix": "Bọc khối rẽ nhánh bằng cặp ngoặc chuẩn: if ($error) { flash($error, 'error'); }.",
            "result": "Xóa sạch 1 Critical Code Smell, đưa Maintainability Rating về mức A tuyệt đối."
        }
    )

    # =========================================================================
    # SLIDE 9: MEMBER 3 - DAO XUAN MANH
    # =========================================================================
    create_member_slide(
        3, "Đào Xuân Mạnh",
        "Kỹ sư Kiểm định Chất lượng & Bảo mật (QA / DevSecOps Engineer)",
        "Module Cẩm nang Quy chuẩn logistics (guide.php) & SonarQube Quality Gate",
        {
            "meta": [
                ("Tên lỗ hổng", "Local File Inclusion (Path Traversal) tại Cẩm nang"),
                ("Vị trí vi phạm", "InlaneWeb/web/src/pages/guide.php:54"),
                ("Mã điểm yếu", "CWE-22: Path Traversal | OWASP Top 10: A01:2021"),
                ("Quy tắc phát hiện", "Semgrep Rule tainted-filename & SonarQube php:S2083")
            ],
            "code_snippet": "$doc = $_GET['doc'] ?? 'incoterms2020.html';\n$target_file = __DIR__ . '/../guides/' . $doc;\ninclude $target_file; // Kẻ tấn công dùng ../../etc/passwd",
            "fix_summary": "Sử dụng hàm lọc tên tệp basename() kết hợp cơ chế Whitelist danh mục tài liệu cho phép (incoterms2020, customs,...).",
            "legal": "Nghị định 13/2023/NĐ-CP (Điều 13 K.2, Điều 26) & GDPR Art. 5(1)(f) (Bảo vệ bí mật CSDL và hệ thống)."
        },
        {
            "meta": [
                ("Mã vấn đề", "CQ-01: Use 'include_once' Instead of 'include'"),
                ("Vị trí vi phạm", "InlaneWeb/web/src/pages/guide.php:56"),
                ("Quy tắc SonarQube", "php:S2003 (Minor Bug)"),
                ("Tiêu chuẩn vi phạm", "SonarQube PHP Reliability Standard")
            ],
            "analysis": "Dùng chỉ thị include nạp tệp không kiểm soát nạp lặp, có nguy cơ gây lỗi Fatal error: Cannot redeclare function làm sập ứng dụng runtime.",
            "fix": "Chuyển sang include_once bảo đảm tính idempotent cho luồng nạp tệp.",
            "result": "Khắc phục triệt để nguy cơ sập runtime, nâng Reliability Rating lên mức A."
        }
    )

    # =========================================================================
    # SLIDE 10: MEMBER 4 - LE DUC ANH
    # =========================================================================
    create_member_slide(
        4, "Lê Đức Anh",
        "Kỹ sư Tự động hóa Hạ tầng (Infrastructure Automation Engineer)",
        "Phân hệ Quản lý hồ sơ vận đơn (account.php) & Kiểm định an toàn IaC",
        {
            "meta": [
                ("Tên lỗ hổng", "Order-By Clause SQL Injection tại Quản lý Hồ sơ"),
                ("Vị trí vi phạm", "InlaneWeb/web/src/pages/account.php:41"),
                ("Mã điểm yếu", "CWE-89: SQL Injection | OWASP Top 10: A03:2021"),
                ("Quy tắc phát hiện", "Semgrep Custom Rule php-sqli-taint-order-by")
            ],
            "code_snippet": "$order = $_GET['order'] ?? 'id';\n$sql = \"SELECT tracking_no FROM shipments WHERE customer_id = $uid ORDER BY $order\";\n$res = query($sql);",
            "fix_summary": "Áp dụng kỹ thuật Whitelist danh mục cột sắp xếp hợp lệ ($allowed_columns = ['id'=>'id', 'tracking_no'=>'tracking_no', ...]).",
            "legal": "Nghị định 13/2023/NĐ-CP (Điều 9 K.2, Điều 26) & GDPR Art. 32 (Ngăn ngừa trích xuất dữ liệu vận đơn)."
        },
        {
            "meta": [
                ("Mã vấn đề", "CQ-01: Form Label Not Associated With Input Control"),
                ("Vị trí vi phạm", "InlaneWeb/web/src/pages/account.php:28"),
                ("Quy tắc SonarQube", "Web:S6853 (Major Code Smell)"),
                ("Tiêu chuẩn vi phạm", "WCAG 2.1 Level A (Criteria 1.3.1) / ISO/IEC 40500")
            ],
            "analysis": "Thẻ <label> đứng độc lập không có thuộc tính for liên kết tới id của trường nhập email, vi phạm tiêu chuẩn trợ năng quốc tế.",
            "fix": "Liên kết chuẩn: <label for=\"acc-email\">Email</label> và <input id=\"acc-email\" ...>.",
            "result": "Đưa New Code Smells về 0, đạt chứng chỉ trợ năng ISO/IEC 40500:2012."
        }
    )

    # =========================================================================
    # SLIDE 11: MEMBER 5 - NGUYEN PHUONG MAI
    # =========================================================================
    create_member_slide(
        5, "Nguyễn Phương Mai",
        "Kỹ sư Giám sát & Vận hành (Monitoring & SecOps Engineer)",
        "Module Bình luận vận đơn (comment_add.php), Dashboard Admin & Cụm SIEM",
        {
            "meta": [
                ("Tên lỗ hổng", "INSERT Statement SQL Injection tại Bình luận Vận đơn"),
                ("Vị trí vi phạm", "InlaneWeb/web/src/pages/comment_add.php:19"),
                ("Mã điểm yếu", "CWE-89: SQL Injection | OWASP Top 10: A03:2021"),
                ("Quy tắc phát hiện", "Semgrep Taint Rule tainted-sql-string (Severity: ERROR)")
            ],
            "code_snippet": "$sql = \"INSERT INTO comments (shipment_id, user_id, content) VALUES ($sid, $uid, '$content')\";\nif (exec_write($sql)) { flash('Thành công'); }",
            "fix_summary": "Chuyển sang Prepared Statement tham số hóa cho thao tác INSERT: $stmt = db()->prepare(\"INSERT INTO ... VALUES (?, ?, ?)\"); $stmt->bind_param(\"iis\", ...).",
            "legal": "Nghị định 13/2023/NĐ-CP (Điều 9, 17) & GDPR Art. 32, 33 (Nghĩa vụ phát hiện và báo cáo trong 72h)."
        },
        {
            "meta": [
                ("Mã vấn đề", "CQ-01: Admin Log Filter Input Without Associated Label"),
                ("Vị trí vi phạm", "InlaneWeb/web/src/pages/admin_dashboard.php:26"),
                ("Quy tắc SonarQube", "Web:InputWithoutLabelCheck (Major Bug)"),
                ("Tiêu chuẩn vi phạm", "WCAG 2.1 Level A (Criteria 1.3.1, 4.1.2) / ISO/IEC 40500")
            ],
            "analysis": "Ô input tìm kiếm trên trang dashboard quản trị thiếu hoàn toàn nhãn <label> trợ năng, làm giảm khả năng tiếp cận và đánh rớt SonarQube Quality Gate.",
            "fix": "Bổ sung <label for=\"admin-filter-log\" class=\"sr-only\">Lọc nhật ký:</label>.",
            "result": "Xóa bỏ 1 Major Bug, đưa SonarQube Quality Gate về trạng thái PASSED."
        }
    )

    # =========================================================================
    # SLIDE 12: SUMMARY MATRIX TABLE
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    add_header(s12, "V. Ma trận Phân bổ Nhiệm vụ & Cổng Kiểm soát 5 Thành viên")
    
    # Table layout
    table_shape = s12.shapes.add_table(6, 6, Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.3))
    t12 = table_shape.table
    
    col_w = [Inches(1.8), Inches(2.7), Inches(1.7), Inches(1.5), Inches(2.2), Inches(1.833)]
    for i, w in enumerate(col_w):
        t12.columns[i].width = w
        
    headers12 = ["Thành viên", "Vấn đề An toàn & Code Quality", "Nhóm lỗi", "Pha DevSecOps", "Căn cứ Pháp lý", "Cơ chế Kỹ thuật"]
    for j, h in enumerate(headers12):
        cell = t12.cell(0, j)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        p = cell.text_frame.paragraphs[0]
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER
        
    matrix_data = [
        ("Nguyễn Giang Nam\n(Trưởng nhóm)", "In-band UNION SQLi (ports.php:38)\n& Missing Input Label (CQ)", "Mã nguồn & Trợ năng", "Pha Test / SAST Gate\n(Stage 2)", "NĐ 13: Điều 9 K.2, Đ.26\nGDPR: Art. 32", "Semgrep Taint Engine\n& SonarQube Gate"),
        ("Nguyễn Đình Hải", "Auth Bypass SQLi (login.php:19)\n& PSR-12 Nested If Smell (CQ)", "Mã nguồn & Clean Code", "Pha Test / SAST Gate\n(Stage 2)", "NĐ 13: Điều 9 K.2, Đ.17\nGDPR: Art. 32", "Prepared Statements\n& SonarQube php:S121"),
        ("Đào Xuân Mạnh", "Local File Inclusion (guide.php:54)\n& include_once Bug (CQ)", "Mã nguồn & Reliability", "Pha Build / SAST Gate\n(Stage 2)", "NĐ 13: Điều 13 K.2, Đ.26\nGDPR: Art. 5(1)(f)", "Whitelist Basename\n& SonarQube php:S2003"),
        ("Lê Đức Anh", "Order-By SQLi (account.php:41)\n& Form Label Smell (CQ)", "Mã nguồn & Trợ năng", "Pha Test / SAST Gate\n(Stage 2)", "NĐ 13: Điều 9 K.2, Đ.26\nGDPR: Art. 32", "Whitelist Order Column\n& SonarQube Web:S6853"),
        ("Nguyễn Phương Mai", "INSERT SQLi (comment_add.php:19)\n& Admin Input Label Bug (CQ)", "Mã nguồn & Vận hành", "Pha Test & Monitor\n(Stage 2 & Stage 4)", "NĐ 13: Điều 9, 17, 26\nGDPR: Art. 32, 33 (72h)", "Parameterized INSERT\n& Promtail/Loki SIEM")
    ]
    for r_idx, row in enumerate(matrix_data, 1):
        for c_idx, val in enumerate(row):
            cell = t12.cell(r_idx, c_idx)
            cell.text = val
            cell.fill.solid()
            if r_idx % 2 == 1:
                cell.fill.fore_color.rgb = WHITE
            else:
                cell.fill.fore_color.rgb = LIGHT_BG
            p = cell.text_frame.paragraphs[0]
            p.font.name = "Arial"
            p.font.size = Pt(9.5)
            p.font.color.rgb = DARK
            if c_idx in [0, 2, 3]:
                p.alignment = PP_ALIGN.CENTER

    # =========================================================================
    # SLIDE 13: CONCLUSION & VALUE
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    add_header(s13, "VI. Kết luận & Giá trị Thực tiễn của Đề tài")
    
    conclusions = [
        ("Tự động hóa Toàn trình Khép kín", "Xây dựng thành công chuỗi 4 Stages kiểm định liên tục từ máy lập trình viên (Git Hook) đến phân tích an ninh tĩnh (SAST), đóng gói kiểm thử (Smoke Test) và tự động triển khai VPS."),
        ("Nguyên tắc Shift-Left Security & Dual-Gate", "Chuyển dịch kiểm soát an ninh về sớm nhất có thể. Kết hợp đồng thời Security Gate (chặn đứng lỗ hổng bảo mật) và Quality Gate (đảm bảo độ tin cậy và chuẩn Clean Code)."),
        ("Tuân thủ Pháp lý Nghiêm ngặt", "Mọi phân tích lỗ hổng và cơ chế kiểm toán đều đối chiếu trực tiếp theo Nghị định 13/2023/NĐ-CP và Quy chuẩn GDPR (Châu Âu), bảo vệ an toàn tuyệt đối dữ liệu người dùng."),
        ("Khả năng Vận hành Bền bỉ (24/7 Resilience)", "Tách biệt luồng triển khai Zero-Downtime, kết hợp hệ thống giám sát SIEM Grafana Loki và cơ chế tự phục hồi Autoheal bảo đảm tính sẵn sàng cao cho dịch vụ logistics.")
    ]
    
    top_c = 1.6
    for c_title, c_desc in conclusions:
        add_card(s13, Inches(0.8), Inches(top_c), Inches(11.733), Inches(1.05))
        
        # Icon box
        ib = s13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.05), Inches(top_c + 0.15), Inches(0.75), Inches(0.75))
        ib.fill.solid()
        ib.fill.fore_color.rgb = NAVY
        ib.line.color.rgb = NAVY
        ib_p = ib.text_frame.paragraphs[0]
        ib_p.text = "✓"
        ib_p.font.name = "Arial"
        ib_p.font.size = Pt(20)
        ib_p.font.bold = True
        ib_p.font.color.rgb = WHITE
        ib_p.alignment = PP_ALIGN.CENTER
        
        # Text
        tb = s13.shapes.add_textbox(Inches(2.0), Inches(top_c + 0.1), Inches(10.3), Inches(0.9))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = c_title
        p.font.name = "Arial"
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = NAVY
        
        p = tf.add_paragraph()
        p.text = c_desc
        p.font.name = "Arial"
        p.font.size = Pt(11)
        p.font.color.rgb = DARK
        
        top_c += 1.25

    # Footer note
    tb_foot = s13.shapes.add_textbox(Inches(0.8), Inches(6.8), Inches(11.733), Inches(0.4))
    tf_foot = tb_foot.text_frame
    p_foot = tf_foot.paragraphs[0]
    p_foot.text = "XIN TRÂN TRỌNG CẢM ƠN THẦY VÀ CÁC BẠN ĐÃ LẮNG NGHE! — NHÓM 11 (SEC4342)"
    p_foot.font.name = "Arial"
    p_foot.font.size = Pt(12)
    p_foot.font.bold = True
    p_foot.font.color.rgb = CRIMSON
    p_foot.alignment = PP_ALIGN.CENTER

    # Save presentation
    output_path = "docs/Slide_Bao_Cao_BTL_DevSecOps_Nhom11.pptx"
    prs.save(output_path)
    print(f"Successfully generated PowerPoint slides at: {output_path}")

if __name__ == "__main__":
    build_presentation()

