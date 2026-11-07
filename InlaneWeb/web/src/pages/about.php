<?php
/**
 * about.php — Trang giới thiệu về IlFreight Logistics.
 */
render_header('Giới thiệu công ty');
?>
<div class="hero">
    <h1>Về IlFreight Logistics</h1>
    <p>Nhà cung cấp giải pháp vận tải đa phương thức và dịch vụ cảng biển quốc tế hàng đầu.</p>
</div>

<div class="card">
    <h2>Lịch sử hình thành &amp; Phát triển</h2>
    <p style="line-height:1.6;color:var(--ink);">
        Thành lập từ năm 2010 với trụ sở chính đặt tại trung tâm logistics cảng biển Hải Phòng, <strong>IlFreight Logistics Corp.</strong> đã không ngừng mở rộng mạng lưới văn phòng đại diện và đối tác chiến lược tại các thương cảng sầm uất nhất thế giới như Thượng Hải, Singapore, Dubai, Rotterdam và Los Angeles.
    </p>
    <p style="line-height:1.6;color:var(--ink);">
        Với cam kết mang lại sự an tâm tuyệt đối và tối ưu chi phí chuỗi cung ứng, chúng tôi quản lý hơn 500.000 TEU hàng hoá mỗi năm thông qua đội tàu hiện đại và hệ thống kho bãi đạt chuẩn quốc tế ISO 9001:2015.
    </p>
</div>

<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;margin-bottom:20px;">
    <div class="card">
        <h3 style="color:var(--deep);margin-top:0;">🌐 Mạng lưới toàn cầu</h3>
        <p class="muted" style="line-height:1.5;">Kết nối hơn 120 quốc gia và vùng lãnh thổ với lịch trình tàu ổn định hàng tuần, đảm bảo thời gian vận chuyển nhanh nhất.</p>
    </div>
    <div class="card">
        <h3 style="color:var(--deep);margin-top:0;">🛡️ An toàn tuyệt đối</h3>
        <p class="muted" style="line-height:1.5;">Quy trình bốc dỡ chuẩn hóa, bảo hiểm hàng hoá toàn diện 110% giá trị CIF và đội ngũ chuyên gia giám sát hải trình 24/7.</p>
    </div>
    <div class="card">
        <h3 style="color:var(--deep);margin-top:0;">💻 Công nghệ tiên phong</h3>
        <p class="muted" style="line-height:1.5;">Hệ thống theo dõi tracking thời gian thực, quản lý vận đơn điện tử e-B/L và tính cước tự động minh bạch.</p>
    </div>
</div>

<div class="card">
    <h2>Ban lãnh đạo &amp; Cam kết chất lượng</h2>
    <p style="line-height:1.6;color:var(--ink);">
        Đội ngũ nhân sự của IlFreight bao gồm hơn 1.200 cán bộ công nhân viên được đào tạo bài bản theo chứng chỉ FIATA và IATA. Chúng tôi không chỉ vận chuyển hàng hoá — chúng tôi đồng hành cùng sự thành công và phát triển thịnh vượng của doanh nghiệp bạn.
    </p>
    <div style="margin-top:20px;display:flex;gap:12px;">
        <a href="/services" class="btn">Khám phá dịch vụ</a>
        <a href="/contact" class="btn btn-sm" style="background:var(--teal);display:inline-flex;align-items:center;">Liên hệ tư vấn</a>
    </div>
</div>
<?php
render_footer();
