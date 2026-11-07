<?php
/**
 * shipment_cancel.php — Huỷ đơn hàng (chỉ khi đang ở trạng thái Booked).
 */
$u = require_login();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: /shipments/mine');
    exit;
}

csrf_verify();

$id = (int)($_GET['id'] ?? 0);
if ($id <= 0) {
    header('Location: /shipments/mine');
    exit;
}

$sh = db_select_one("SELECT * FROM shipments WHERE id = ?", "i", [$id]);
if (!$sh) {
    header('Location: /shipments/mine');
    exit;
}

// Kiểm tra quyền sở hữu: chỉ chủ đơn mới được huỷ
if ((int)$sh['customer_id'] !== (int)$u['id']) {
    http_response_code(403);
    render_header('403 — Từ chối');
    echo '<div class="card"><h1>403 — Không có quyền huỷ</h1><p>Bạn không có quyền huỷ đơn hàng này.</p></div>';
    render_footer();
    exit;
}

// Chỉ được huỷ khi đang Booked
if ($sh['status'] !== 'Booked') {
    render_header('Không thể huỷ đơn');
    echo '<div class="card"><h1>Không thể huỷ đơn hàng</h1>'
        . '<p>Chỉ những đơn hàng ở trạng thái <strong>Booked</strong> mới có thể huỷ. Đơn hàng hiện tại đang ở trạng thái <strong>'
        . htmlspecialchars($sh['status']) . '</strong>.</p>'
        . '<p><a href="/shipments/' . htmlspecialchars((string)$id, ENT_QUOTES, 'UTF-8') . '/info" class="btn btn-sm">Quay lại chi tiết</a></p></div>';
    render_footer();
    exit;
}

// Cập nhật trạng thái thành Cancelled
db_execute("UPDATE shipments SET status = 'Cancelled' WHERE id = ?", "i", [$id]);

// Ghi nhận sự kiện huỷ
db_execute(
    "INSERT INTO shipment_events (shipment_id, status, location, note, created_by) VALUES (?, 'Cancelled', 'Yêu cầu của khách hàng', 'Đơn hàng đã bị huỷ bởi người tạo đơn', ?)",
    "ii",
    [$id, (int)$u['id']]
);

// Tạo thông báo cho người dùng
$msg = "Đơn vận chuyển {$sh['tracking_no']} đã được huỷ thành công theo yêu cầu của bạn.";
db_insert(
    "INSERT INTO notifications (user_id, shipment_id, message) VALUES (?, ?, ?)",
    "iis",
    [(int)$u['id'], $id, $msg]
);

// Ghi nhận vào mail_outbox
$subject = "Xác nhận huỷ đơn hàng: {$sh['tracking_no']}";
$body = "Xin chào {$u['username']},\n\n"
    . "Đơn hàng {$sh['tracking_no']} của bạn tại IlFreight Logistics đã được chuyển sang trạng thái Cancelled (Đã huỷ).\n\n"
    . "Nếu cần giải đáp thêm, vui lòng liên hệ bộ phận hỗ trợ khách hàng của chúng tôi.\n\n"
    . "Trân trọng,\nIlFreight Logistics";

db_insert(
    "INSERT INTO mail_outbox (to_email, subject, body) VALUES (?, ?, ?)",
    "sss",
    [$u['email'], $subject, $body]
);

$_SESSION['flash_msg'] = "Đơn vận chuyển {$sh['tracking_no']} đã được huỷ thành công.";
$_SESSION['flash_type'] = 'info';
header('Location: /shipments/mine');
exit;
