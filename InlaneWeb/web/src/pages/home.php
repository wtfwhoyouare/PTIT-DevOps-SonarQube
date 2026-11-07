<?php
/**
 * home.php — Trang chu chinh thuc cua IlFreight Logistics.
 * Giao dien doanh nghiep van tai & logistics quoc te chuyen nghiep.
 */
render_header('Trang chủ — IlFreight Logistics Toàn Cầu');

// Lay du lieu an toan cho trang chu
$u = current_user();

// 3 ban tin moi nhat
$newsList = db_select("SELECT id, title, body, published_at FROM news ORDER BY published_at DESC LIMIT 3");

// Top 6 cang bien quoc te co san luong lon nhat
$topPorts = db_select("SELECT code, city, country, volume FROM ports ORDER BY volume DESC LIMIT 6");
?>

<!-- 1. HERO SECTION -->
<div class="home-hero">
    <div class="home-hero-badge">
        <span>⚓</span> HỆ THỐNG VẬN TẢI HÀNG HẢI &amp; LOGISTICS TOÀN CẦU
    </div>
    <h1>Dẫn Đầu Chuỗi Cung Ứng &amp;<br>Vận Tải Đa Phương Thức Tiên Tiến</h1>
    <p class="hero-lead">
        IlFreight Logistics kết nối hơn 120 quốc gia và vùng lãnh thổ với dịch vụ vận tải container FCL/LCL, hệ thống kho vận ngoại quan thông minh và năng lực vận hành trên 500.000 TEU mỗi năm.
    </p>

    <div class="home-hero-actions">
        <?php if ($u): ?>
            <a href="/shipments/new" class="btn-hero-primary">🚀 Tạo Đơn Booking Mới</a>
            <a href="/shipments/mine" class="btn-hero-secondary">📦 Đơn Hàng Của Tôi</a>
            <a href="/quote" class="btn-hero-secondary">📊 Tính Báo Giá Cước</a>
        <?php else: ?>
            <a href="/shipments/new" class="btn-hero-primary">🚀 Đặt Chỗ Vận Tải (Booking)</a>
            <a href="/quote" class="btn-hero-secondary">📊 Nhận Báo Giá Tức Thì</a>
            <a href="/register" class="btn-hero-secondary">🔑 Đăng Ký Tài Khoản</a>
            <a href="/track" class="btn-hero-ghost">Tra cứu hành trình vận đơn →</a>
        <?php endif; ?>
    </div>

    <!-- Chi so then chot (Key Metrics) -->
    <div class="home-stats-grid">
        <div class="home-stat-item">
            <div class="home-stat-num">120<span>+</span></div>
            <div class="home-stat-label">Cảng biển &amp; Thương cảng toàn cầu</div>
        </div>
        <div class="home-stat-item">
            <div class="home-stat-num">500K<span>+</span></div>
            <div class="home-stat-label">TEU vận chuyển hàng năm</div>
        </div>
        <div class="home-stat-item">
            <div class="home-stat-num">99.8<span>%</span></div>
            <div class="home-stat-label">Đúng tiến độ hải trình cam kết</div>
        </div>
        <div class="home-stat-item">
            <div class="home-stat-num">24<span>/7</span></div>
            <div class="home-stat-label">Giám sát container thời gian thực</div>
        </div>
    </div>
</div>

<!-- 2. OPERATIONAL GATEWAY (HUB NGHIỆP VỤ SỐ) -->
<div class="home-section-header">
    <div class="section-tag">TIỆN ÍCH TRỰC TUYẾN</div>
    <h2>Cổng Nghiệp Vụ Logistics Số Hoá</h2>
    <p>Truy cập nhanh các công cụ tác nghiệp và tra cứu dữ liệu hàng hải mọi lúc, mọi nơi.</p>
</div>

<div class="home-hub-grid">
    <div class="home-hub-card">
        <div>
            <div class="home-hub-icon">📦</div>
            <h3>Tra Cứu Vận Đơn</h3>
            <p>Theo dõi vị trí và tiến trình thông quan của lô hàng qua mã vận đơn (Tracking Number) với độ chính xác cao.</p>
        </div>
        <a href="/track" class="home-hub-link">Tra cứu hành trình &rarr;</a>
    </div>

    <div class="home-hub-card">
        <div>
            <div class="home-hub-icon">⚓</div>
            <h3>Cổng Tra Cứu Cảng Biển</h3>
            <p>Tra cứu danh bạ hơn 100 thương cảng quốc tế, sản lượng bốc dỡ TEU và năng lực tiếp nhận tàu biển.</p>
        </div>
        <a href="/ports" class="home-hub-link">Mở cổng tra cứu cảng &rarr;</a>
    </div>

    <div class="home-hub-card">
        <div>
            <div class="home-hub-icon">💰</div>
            <h3>Dự Toán Cước Vận Tải</h3>
            <p>Công cụ ước tính tự động chi phí cước biển cho container 20GP, 40GP, 40HC kèm phụ phí minh bạch.</p>
        </div>
        <a href="/quote" class="home-hub-link">Tính báo giá ngay &rarr;</a>
    </div>

    <div class="home-hub-card">
        <div>
            <div class="home-hub-icon">📘</div>
            <h3>Quy Chuẩn &amp; Biểu Mẫu</h3>
            <p>Cẩm nang vận tải, bộ quy tắc Incoterms 2020 và hướng dẫn quy chuẩn đóng gói container quốc tế.</p>
        </div>
        <a href="/guide" class="home-hub-link">Xem cẩm nang &rarr;</a>
    </div>
</div>

<!-- 3. QUICK TRACKING CALLOUT -->
<div class="home-track-callout">
    <div class="home-track-callout-text">
        <h3>🔍 Bạn cần theo dõi lô hàng đang vận chuyển?</h3>
        <p>Nhập mã vận đơn (ví dụ: <code>ILF1042CN</code>) để xem trạng thái tức thì từ hệ thống định vị vệ tinh.</p>
    </div>
    <form class="home-track-callout-form" action="/track" method="get">
        <input type="text" name="tracking" placeholder="Nhập mã vận đơn (Tracking No)..." required>
        <button class="btn" type="submit">Kiểm Tra Ngay</button>
    </form>
</div>

<!-- 4. CORE SERVICES SHOWCASE -->
<div class="home-section-header">
    <div class="section-tag">DỊCH VỤ CỐT LÕI</div>
    <h2>Giải Pháp Chuỗi Cung Ứng Khép Kín</h2>
    <p>Đáp ứng mọi yêu cầu khắt khe của doanh nghiệp xuất nhập khẩu với tiêu chuẩn chất lượng quốc tế.</p>
</div>

<div class="home-services-grid">
    <div class="home-service-card">
        <div class="svc-icon-box">🚢</div>
        <h3>Vận Tải Đường Biển Quốc Tế</h3>
        <p>Dịch vụ gom hàng lẻ (LCL) và hàng nguyên container (FCL) tới các cảng chính tại Châu Á, Châu Âu và Bắc Mỹ với lịch tàu hàng tuần.</p>
        <ul>
            <li>Hợp tác với các liên minh hãng tàu lớn</li>
            <li>Cam kết chỗ xếp hàng ngay cả mùa cao điểm</li>
            <li>Theo dõi mớn nước và định vị hành trình</li>
        </ul>
        <a href="/services" class="btn btn-sm">Chi tiết dịch vụ →</a>
    </div>

    <div class="home-service-card">
        <div class="svc-icon-box">❄️</div>
        <h3>Chuỗi Cung Ứng Lạnh (Reefer)</h3>
        <p>Kiểm soát độ ẩm và dải nhiệt độ nghiêm ngặt từ -30°C đến +30°C cho nông sản tươi, thuỷ hải sản đông lạnh và dược phẩm y tế.</p>
        <ul>
            <li>Container lạnh thế hệ mới tiết kiệm năng lượng</li>
            <li>Cảm biến IoT truyền dữ liệu nhiệt độ liên tục</li>
            <li>Quy trình khử trùng và kiểm dịch chuyên nghiệp</li>
        </ul>
        <a href="/services" class="btn btn-sm">Chi tiết dịch vụ →</a>
    </div>

    <div class="home-service-card">
        <div class="svc-icon-box">🏢</div>
        <h3>Hệ Thống Kho Bãi &amp; Ngoại Quan</h3>
        <p>Hệ thống kho CFS và kho ngoại quan phân bố tại các trung tâm logistics trọng điểm, trang bị hệ thống quản lý WMS thông minh.</p>
        <ul>
            <li>Phân loại, đóng gói và dán nhãn hàng hoá</li>
            <li>Bảo quản an toàn với hệ thống PCCC tự động</li>
            <li>Bốc dỡ nhanh chóng với xe nâng và cẩu giàn</li>
        </ul>
        <a href="/services" class="btn btn-sm">Chi tiết dịch vụ →</a>
    </div>

    <div class="home-service-card">
        <div class="svc-icon-box">📑</div>
        <h3>Thủ Tục Hải Quan &amp; Bảo Hiểm</h3>
        <p>Đại lý hải quan chuyên trách hoàn tất chứng từ xuất nhập khẩu nhanh chóng, giảm thiểu tối đa rủi ro chậm trễ tại cảng.</p>
        <ul>
            <li>Khai báo tờ khai hải quan điện tử VNACCS</li>
            <li>Tư vấn mã HS và chính sách thuế ưu đãi</li>
            <li>Bảo hiểm hàng hải toàn diện 110% giá trị CIF</li>
        </ul>
        <a href="/services" class="btn btn-sm">Chi tiết dịch vụ →</a>
    </div>
</div>

<!-- 5. GLOBAL GATEWAY PORTS NETWORK -->
<div class="home-section-header" style="display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:12px;">
    <div>
        <div class="section-tag">MẠNG LƯỚI TOÀN CẦU</div>
        <h2>Các Thương Cảng Trọng Điểm</h2>
        <p>Mạng lưới kết nối xuyên suốt các trung tâm trung chuyển hàng hải sầm uất nhất hành tinh.</p>
    </div>
    <div>
        <a href="/ports" class="btn btn-sm" style="background:#5B6B7B;">Xem tất cả các cảng biển →</a>
    </div>
</div>

<div class="home-ports-grid">
    <?php foreach ($topPorts as $port): ?>
        <a href="/ports/<?= urlencode($port['code']) ?>" class="home-port-card">
            <span class="home-port-code"><?= htmlspecialchars($port['code'], ENT_QUOTES, 'UTF-8') ?></span>
            <div class="home-port-city"><?= htmlspecialchars($port['city'], ENT_QUOTES, 'UTF-8') ?></div>
            <div class="home-port-country"><?= htmlspecialchars($port['country'], ENT_QUOTES, 'UTF-8') ?></div>
            <div class="home-port-vol">📊 <?= htmlspecialchars(number_format((float)$port['volume'], 1), ENT_QUOTES, 'UTF-8') ?>M TEU/năm</div>
        </a>
    <?php endforeach; ?>
</div>

<!-- 6. WHY CHOOSE ILFREIGHT -->
<div class="card" style="margin-bottom:36px;background:linear-gradient(135deg,#ffffff 0%,#f5f9fd 100%);border-color:#bad5ed;">
    <div class="home-section-header" style="margin-bottom:20px;">
        <div class="section-tag">CAM KẾT THƯƠNG HIỆU</div>
        <h2>Tại Sao Các Doanh Nghiệp Chọn IlFreight Logistics?</h2>
        <p>Hơn 15 năm kiến tạo giải pháp vận tải biển đáng tin cậy cho hàng nghìn doanh nghiệp xuất nhập khẩu.</p>
    </div>

    <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(220px, 1fr));gap:20px;">
        <div>
            <h4 style="color:var(--deep);font-size:16px;margin:0 0 8px;">🌐 Mạng Lưới Tuyến Tàu Bao Phủ</h4>
            <p class="muted" style="line-height:1.6;margin:0;">Liên kết chặt chẽ với các liên minh hãng tàu lớn, đảm bảo lịch khởi hành cố định hàng tuần và không bị hủy chuyến.</p>
        </div>
        <div>
            <h4 style="color:var(--deep);font-size:16px;margin:0 0 8px;">⚡ Số Hoá Thủ Tục Toàn Diện</h4>
            <p class="muted" style="line-height:1.6;margin:0;">Khởi tạo vận đơn đường biển (B/L) và hoá đơn điện tử trực tiếp trên nền tảng web, tiết kiệm 70% thời gian tác nghiệp.</p>
        </div>
        <div>
            <h4 style="color:var(--deep);font-size:16px;margin:0 0 8px;">🛡️ Minh Bạch &amp; Bảo Hiểm Toàn Phần</h4>
            <p class="muted" style="line-height:1.6;margin:0;">Bảng giá niêm yết rõ ràng, không phụ phí ẩn. Chính sách bồi thường 100% trong trường hợp tổn thất hàng hoá.</p>
        </div>
        <div>
            <h4 style="color:var(--deep);font-size:16px;margin:0 0 8px;">🤝 Chuyên Gia Đồng Hành 24/7</h4>
            <p class="muted" style="line-height:1.6;margin:0;">Đội ngũ chuyên viên chứng từ và giao nhận giàu kinh nghiệm luôn túc trực hỗ trợ xử lý sự cố tại hiện trường cảng.</p>
        </div>
    </div>
</div>

<!-- 7. LATEST MARITIME NEWS -->
<div class="home-section-header" style="display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:12px;">
    <div>
        <div class="section-tag">TIN TỨC &amp; THỊ TRƯỜNG</div>
        <h2>Bản Tin Hàng Hải &amp; Cập Nhật Tuyến Vận Tải</h2>
        <p>Thông tin cập nhật mới nhất về biến động thị trường cước, nâng cấp hạ tầng cảng và chính sách logistics.</p>
    </div>
    <div>
        <a href="/news" class="btn btn-sm" style="background:#5B6B7B;">Xem toàn bộ tin tức →</a>
    </div>
</div>

<div class="home-news-grid">
    <?php if (!empty($newsList)): ?>
        <?php foreach ($newsList as $newsItem): ?>
            <div class="home-news-card">
                <div>
                    <div class="news-date">📅 <?= htmlspecialchars($newsItem['published_at'], ENT_QUOTES, 'UTF-8') ?></div>
                    <h3><?= htmlspecialchars($newsItem['title'], ENT_QUOTES, 'UTF-8') ?></h3>
                    <p><?= htmlspecialchars(mb_substr($newsItem['body'], 0, 140), ENT_QUOTES, 'UTF-8') ?>...</p>
                </div>
                <div>
                    <a href="/news" style="font-weight:700;font-size:13px;color:var(--deep);">Đọc chi tiết bản tin &rarr;</a>
                </div>
            </div>
        <?php endforeach; ?>
    <?php else: ?>
        <p class="muted">Hiện chưa có bản tin mới.</p>
    <?php endif; ?>
</div>

<!-- 8. BOTTOM ENTERPRISE CTA -->
<div class="home-cta-banner">
    <h2>Sẵn Sàng Nâng Tầm Chuỗi Cung Ứng Của Doanh Nghiệp?</h2>
    <p>
        Đội ngũ chuyên gia của IlFreight luôn sẵn sàng tư vấn lộ trình vận tải tối ưu chi phí và thời gian cho lô hàng tiếp theo của bạn.
    </p>
    <div class="btn-group">
        <a href="/shipments/new" class="btn-hero-primary">Tạo Đơn Hàng Mới</a>
        <a href="/quote" class="btn-hero-secondary">Tra Cứu Báo Giá Cước</a>
        <a href="/contact" class="btn-hero-secondary">Liên Hệ Chuyên Viên</a>
    </div>
</div>

<?php
render_footer();
