<?php
/**
 * admin_shipment_status.php — Cập nhật trạng thái vận đơn bởi staff/admin.
 */
$u = require_role(['admin', 'staff']);

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: /admin/shipments');
    exit;
}

csrf_verify();

$id = (int)($_GET['id'] ?? 0);
if ($id <= 0) {
    header('Location: /admin/shipments');
    exit;
}

$sh = db_select_one("SELECT * FROM shipments WHERE id = ?", "i", [$id]);
if (!$sh) {
    header('Location: /admin/shipments');
    exit;
}

$newStatus = trim($_POST['status'] ?? '');
$location  = trim($_POST['location'] ?? '');
$note      = trim($_POST['note'] ?? '');

$validStatuses = [
    'Booked',
    'In Transit',
    'At Port',
    'Customs Hold',
    'Out for Delivery',
    'Delivered',
    'Cancelled'
];

if (!in_array($newStatus, $validStatuses, true)) {
    $_SESSION['admin_flash'] = 'Trạng thái cập nhật không hợp lệ.';
    $_SESSION['admin_flash_type'] = 'error';
    header('Location: /admin/shipments');
    exit;
}

// 1. Cập nhật bảng shipments
db_execute("UPDATE shipments SET status = ? WHERE id = ?", "si", [$newStatus, $id]);

// 2. Ghi nhận sự kiện vào shipment_events
db_execute(
    "INSERT INTO shipment_events (shipment_id, status, location, note, created_by) VALUES (?, ?, ?, ?, ?)",
    "isssi",
    [$id, $newStatus, $location, $note, (int)$u['id']]
);

// 3. Tạo thông báo cho chủ sở hữu đơn hàng
$notifMsg = "Vận đơn {$sh['tracking_no']} của bạn vừa được cập nhật sang trạng thái: {$newStatus}";
if ($location !== '') {
    $notifMsg .= " tại {$location}";
}
if ($note !== '') {
    $notifMsg .= " (Ghi chú: {$note})";
}

$owner = db_select_one("SELECT id, username, email FROM users WHERE id = ?", "i", [(int)$sh['customer_id']]);
if ($owner) {
    db_insert(
        "INSERT INTO notifications (user_id, shipment_id, message) VALUES (?, ?, ?)",
        "iis",
        [(int)$owner['id'], $id, $notifMsg]
    );

    // 4. Ghi email vào mail_outbox
    $mailSubject = "Cập nhật trạng thái đơn hàng: {$sh['tracking_no']} [{$newStatus}]";
    $mailBody = "Kính gửi {$owner['username']},\n\n"
        . "Đơn vận chuyển {$sh['tracking_no']} của bạn tại IlFreight Logistics đã có cập nhật mới:\n"
        . "- Trạng thái mới: {$newStatus}\n"
        . "- Địa điểm: " . ($location ?: 'Hệ thống') . "\n"
        . "- Ghi chú: " . ($note ?: 'Không có ghi chú thêm') . "\n\n"
        . "Tra cứu tiến trình trực tiếp tại: " . app_base_url() . "/shipments/{$id}/info\n\n"
        . "Trân trọng,\nIlFreight Logistics Operations";

    db_insert(
        "INSERT INTO mail_outbox (to_email, subject, body) VALUES (?, ?, ?)",
        "sss",
        [$owner['email'], $mailSubject, $mailBody]
    );
}

$_SESSION['admin_flash'] = "Đã cập nhật trạng thái đơn {$sh['tracking_no']} thành [{$newStatus}].";
$_SESSION['admin_flash_type'] = 'success';
header('Location: /admin/shipments');
exit;
