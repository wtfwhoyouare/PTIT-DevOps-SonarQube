<?php
/** layout.php — Header / nav / footer dung chung (UI giong app that). */

require_once __DIR__ . '/icons.php';

function current_user(): ?array
{
    if (!empty($_SESSION['uid'])) {
        // NOTE: doc lai user tu DB moi request (khong sanitize uid tu session)
        return query_one("SELECT * FROM users WHERE id = " . intval($_SESSION['uid']));
    }
    return null;
}

function render_header(string $title = 'IlFreight Logistics'): void
{
    $u = current_user();
    $unread_count = 0;
    if ($u && function_exists('db_select_one')) {
        try {
            $n_row = db_select_one("SELECT COUNT(*) AS cnt FROM notifications WHERE user_id = ? AND is_read = 0", "i", [(int)$u['id']]);
            if ($n_row) {
                $unread_count = (int)$n_row['cnt'];
            }
        } catch (\Throwable $e) {
            // Neu bang notifications chua khoi tao thi bo qua
            $unread_count = 0;
        }
    }
    ?><!doctype html>
<html lang="vi">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title><?= htmlspecialchars($title) ?> — IlFreight Logistics</title>
    <link rel="stylesheet" href="/assets/style.css?v=<?= (int) @filemtime(__DIR__ . '/../assets/style.css') ?>">
</head>
<body>
<header class="topbar">
    <a class="brand" href="/">
        <span class="brand-mark">◆</span> IlFreight <span class="brand-sub">Logistics</span>
    </a>
    <nav class="mainnav">
        <a href="/">Trang chủ</a>
        <a href="/services">Dịch vụ</a>
        <a href="/ports">Cảng biển</a>
        <a href="/quote">Báo giá</a>
        <a href="/track">Tra cứu</a>
        <a href="/guide">Quy chuẩn</a>
        <a href="/news">Tin tức</a>
        <a href="/about">Giới thiệu</a>
        <a href="/contact">Liên hệ</a>
        <?php if ($u): ?>
            <a href="/shipments/mine">Đơn của tôi</a>
            <a href="/notifications">Thông báo<?= $unread_count > 0 ? ' (' . $unread_count . ')' : '' ?></a>
            <a href="/account">Hồ sơ</a>
            <?php if (in_array($u['role'], ['admin', 'staff'])): ?>
                <a href="/admin" class="nav-admin">Quản trị</a>
            <?php endif; ?>
            <a href="/logout" class="nav-cta">Đăng xuất (<?= htmlspecialchars($u['username']) ?>)</a>
        <?php else: ?>
            <a href="/register">Đăng ký</a>
            <a href="/login" class="nav-cta">Đăng nhập</a>
        <?php endif; ?>
    </nav>
</header>
<?php if ($u && in_array($u['role'], ['admin', 'staff'], true)): ?>
<nav class="admin-subnav no-print" aria-label="Menu quản trị">
    <span class="admin-subnav-label">Quản trị:</span>
    <a href="/admin">Tổng quan</a>
    <a href="/admin/shipments">Quản lý vận đơn</a>
    <a href="/admin/ports">Quản lý cảng</a>
    <a href="/admin/news">Quản lý tin tức</a>
    <a href="/admin/messages">Hộp thư liên hệ</a>
    <a href="/admin/mail-outbox">Mail Outbox</a>
    <?php if ($u['role'] === 'admin'): ?>
        <a href="/admin/users">Quản lý người dùng</a>
    <?php endif; ?>
</nav>
<?php endif; ?>
<main class="container">
<?php
}

function render_footer(): void
{
    ?>
</main>
<footer class="footer">
    <div style="margin-bottom:10px">
        <a href="/about">Giới thiệu</a> · 
        <a href="/services">Dịch vụ</a> · 
        <a href="/quote">Báo giá cước</a> · 
        <a href="/ports">Cảng biển</a> · 
        <a href="/track">Tra cứu vận đơn</a> · 
        <a href="/guide">Quy chuẩn</a> · 
        <a href="/news">Tin tức</a> · 
        <a href="/contact">Liên hệ</a>
    </div>
    <div>© <?= date('Y') ?> IlFreight Logistics Co. — Global Freight Forwarding &amp; Port Services</div>
    <div class="footer-warn">Môi trường huấn luyện nội bộ</div>
</footer>
</body>
</html>
<?php
}

/** flash() — thong bao ngan (success/error/info). */
function flash(string $msg, string $type = 'info'): void
{
    echo '<div class="flash flash-' . $type . '">' . $msg . '</div>';
}
