<?php
/**
 * admin_dashboard.php — Dashboard quan tri (staff/admin).
 * Co o tim khach hang (?customer=) -> Boolean/Error, va cac lien ket toi
 * cong cu export (CREATE) va console (stacked).
 */
$u = current_user();
if (!$u || !in_array($u['role'], ['admin', 'staff'])) {
    render_header('Truy cập bị từ chối');
    echo '<div class="card"><h1>403 — Cần quyền quản trị</h1>'
       . '<p class="muted">Gợi ý: có thể đăng nhập bằng SQLi với vai trò admin.</p></div>';
    render_footer();
    exit;
}

render_header('Quản trị');
?>
<div class="card">
    <h1>Bảng điều khiển quản trị</h1>
    <p class="muted">Xin chào <?= htmlspecialchars($u['username']) ?> (<?= htmlspecialchars($u['role']) ?>)</p>
</div>

<?php
// Thong ke Tong quan (Business Overview)
$totalShipmentsRow = db_select_one("SELECT COUNT(*) AS cnt FROM shipments");
$totalShipments = $totalShipmentsRow ? (int)$totalShipmentsRow['cnt'] : 0;

$statusCounts = db_select("SELECT status, COUNT(*) AS cnt FROM shipments GROUP BY status ORDER BY cnt DESC");

$topPorts = db_select("SELECT port_code, COUNT(*) AS cnt FROM shipments GROUP BY port_code ORDER BY cnt DESC LIMIT 5");

$newUsersRow = db_select_one("SELECT COUNT(*) AS cnt FROM user_profiles WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)");
$newUsersCount = $newUsersRow ? (int)$newUsersRow['cnt'] : 0;

$unhandledMsgRow = db_select_one("SELECT COUNT(*) AS cnt FROM contact_messages WHERE is_handled = 0");
$unhandledMsgCount = $unhandledMsgRow ? (int)$unhandledMsgRow['cnt'] : 0;
?>
<div class="card">
    <h2>Tổng quan hoạt động logistics</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(200px, 1fr));gap:16px;margin:16px 0;">
        <div style="background:#eaf1f7;padding:16px;border-radius:8px;border-left:4px solid var(--deep);">
            <div class="muted" style="font-size:12px;font-weight:bold;">TỔNG SỐ ĐƠN HÀNG</div>
            <div style="font-size:26px;font-weight:bold;color:var(--deep);margin-top:4px;"><?= htmlspecialchars((string)$totalShipments, ENT_QUOTES, 'UTF-8') ?></div>
            <div style="font-size:12px;margin-top:4px;"><a href="/admin/shipments">Xem tất cả vận đơn →</a></div>
        </div>
        <div style="background:#fff3d6;padding:16px;border-radius:8px;border-left:4px solid var(--accent);">
            <div class="muted" style="font-size:12px;font-weight:bold;color:#8a6100;">USER MỚI (30 NGÀY)</div>
            <div style="font-size:26px;font-weight:bold;color:#8a6100;margin-top:4px;"><?= htmlspecialchars((string)$newUsersCount, ENT_QUOTES, 'UTF-8') ?></div>
            <div style="font-size:12px;margin-top:4px;"><?php if ($u['role'] === 'admin'): ?><a href="/admin/users">Quản lý người dùng →</a><?php else: ?>Người dùng mới<?php endif; ?></div>
        </div>
        <div style="background:#fbe4e5;padding:16px;border-radius:8px;border-left:4px solid var(--danger);">
            <div class="muted" style="font-size:12px;font-weight:bold;color:var(--danger);">LIÊN HỆ CHƯA XỬ LÝ</div>
            <div style="font-size:26px;font-weight:bold;color:var(--danger);margin-top:4px;"><?= htmlspecialchars((string)$unhandledMsgCount, ENT_QUOTES, 'UTF-8') ?></div>
            <div style="font-size:12px;margin-top:4px;"><a href="/admin/messages?handled=0">Xem tin nhắn liên hệ →</a></div>
        </div>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:16px;">
        <div>
            <h3 style="font-size:15px;margin-bottom:8px;">Trạng thái vận đơn</h3>
            <table class="data" style="margin-top:0;">
                <thead><tr><th>Trạng thái</th><th style="text-align:right;">Số lượng</th></tr></thead>
                <tbody>
                    <?php if (empty($statusCounts)): ?>
                        <tr><td colspan="2" class="muted">Chưa có dữ liệu</td></tr>
                    <?php else: ?>
                        <?php foreach ($statusCounts as $sc): ?>
                            <tr>
                                <td><?= htmlspecialchars($sc['status'], ENT_QUOTES, 'UTF-8') ?></td>
                                <td style="text-align:right;font-weight:bold;"><?= htmlspecialchars((string)$sc['cnt'], ENT_QUOTES, 'UTF-8') ?></td>
                            </tr>
                        <?php endforeach; ?>
                    <?php endif; ?>
                </tbody>
            </table>
        </div>
        <div>
            <h3 style="font-size:15px;margin-bottom:8px;">Top 5 Cảng đến phổ biến</h3>
            <table class="data" style="margin-top:0;">
                <thead><tr><th>Mã cảng đến</th><th style="text-align:right;">Lượt vận chuyển</th></tr></thead>
                <tbody>
                    <?php if (empty($topPorts)): ?>
                        <tr><td colspan="2" class="muted">Chưa có dữ liệu</td></tr>
                    <?php else: ?>
                        <?php foreach ($topPorts as $tp): ?>
                            <tr>
                                <td><strong><?= htmlspecialchars($tp['port_code'], ENT_QUOTES, 'UTF-8') ?></strong></td>
                                <td style="text-align:right;font-weight:bold;"><?= htmlspecialchars((string)$tp['cnt'], ENT_QUOTES, 'UTF-8') ?></td>
                            </tr>
                        <?php endforeach; ?>
                    <?php endif; ?>
                </tbody>
            </table>
        </div>
    </div>
</div>

<div class="card">
    <h2>Tìm khách hàng</h2>
    <form class="searchbar" action="/admin" method="get">
        <input type="text" name="customer" value="<?= htmlspecialchars($_GET['customer'] ?? '') ?>" placeholder="Tên khách hàng...">
        <button class="btn" type="submit">Tìm</button>
    </form>
    <?php
    if (!empty($_GET['customer'])) {
        $c = $_GET['customer'];
        // !!! NOI CHUOI -> UNION/Error/Boolean !!!
        $sql = "SELECT username, email, role FROM users WHERE username LIKE '%$c%'";
        echo '<div class="query-box">' . htmlspecialchars($sql) . '</div>';
        $res = query($sql);
        if ($res && mysqli_num_rows($res) > 0) {
            echo '<table class="data"><tr><th>Username</th><th>Email</th><th>Role</th></tr>';
            while ($row = mysqli_fetch_row($res)) {
                echo '<tr><td>' . htmlspecialchars((string)$row[0]) . '</td>'
                   . '<td>' . htmlspecialchars((string)$row[1]) . '</td>'
                   . '<td>' . htmlspecialchars((string)$row[2]) . '</td></tr>';
            }
            echo '</table>';
        }
    }
    ?>
</div>

<div class="card">
    <h2>Công cụ & Quản lý nghiệp vụ</h2>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px;">
        <p><a href="/admin/shipments">→ Quản lý vận đơn</a> — Tra cứu, giám sát và cập nhật trạng thái đơn hàng.</p>
        <p><a href="/admin/ports">→ Quản lý cảng biển</a> — Danh mục các cảng biển và sản lượng TEU.</p>
        <p><a href="/admin/news">→ Quản lý tin tức</a> — Bản tin hàng hải và cập nhật thông báo.</p>
        <p><a href="/admin/messages">→ Hộp thư liên hệ</a> — Tiếp nhận và xử lý phản hồi từ khách hàng.</p>
        <p><a href="/admin/mail-outbox">→ Hộp thư giả lập (Mail Outbox)</a> — Xem email thông báo và reset password.</p>
        <?php if ($u['role'] === 'admin'): ?>
            <p><a href="/admin/users">→ Quản lý người dùng</a> — Danh sách user, phân quyền và khoá tài khoản.</p>
        <?php endif; ?>
    </div>
    <h3>Công cụ phục vụ thực hành bảo mật</h3>
    <p><a href="/admin/reports/export">→ Xuất báo cáo (tạo bảng tạm)</a> — tạo bảng snapshot theo tên tuỳ chọn.</p>
    <p><a href="/admin/console?filter=status">→ Console lọc nâng cao</a> — bộ lọc dữ liệu vận đơn.</p>
</div>
<?php
render_footer();