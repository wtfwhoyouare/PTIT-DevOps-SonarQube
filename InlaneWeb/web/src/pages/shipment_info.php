<?php
/**
 * shipment_info.php — Xem chi tiết an toàn + timeline trạng thái của vận đơn.
 */
$u = require_login();

$id = (int)($_GET['id'] ?? 0);
if ($id <= 0) {
    header('Location: /shipments/mine');
    exit;
}

// Lấy thông tin cơ bản của vận đơn
$sh = db_select_one("SELECT * FROM shipments WHERE id = ?", "i", [$id]);
if (!$sh) {
    http_response_code(404);
    render_header('Không tìm thấy đơn hàng');
    echo '<div class="card"><h1>404 — Không tìm thấy vận đơn</h1>'
        . '<p>Mã vận đơn #' . htmlspecialchars((string)$id, ENT_QUOTES, 'UTF-8') . ' không tồn tại trong hệ thống.</p>'
        . '<p><a href="/shipments/mine" class="btn btn-sm">Quay lại danh sách</a></p></div>';
    render_footer();
    exit;
}

// Kiểm tra quyền sở hữu: Customer chỉ xem được đơn của mình; Staff và Admin xem được tất cả
$isStaffOrAdmin = in_array($u['role'], ['admin', 'staff'], true);
$isOwner = ((int)$sh['customer_id'] === (int)$u['id']);

if (!$isOwner && !$isStaffOrAdmin) {
    http_response_code(403);
    render_header('403 — Truy cập bị từ chối');
    echo '<div class="card"><h1>403 — Truy cập bị từ chối</h1>'
        . '<p>Bạn không có quyền xem thông tin chi tiết của vận đơn <strong>#' . htmlspecialchars((string)$id, ENT_QUOTES, 'UTF-8') . '</strong>.</p>'
        . '<p><a href="/shipments/mine" class="btn btn-sm">Về đơn hàng của tôi</a></p></div>';
    render_footer();
    exit;
}

// Lấy thông tin chi tiết từ shipment_details
$details = db_select_one("SELECT * FROM shipment_details WHERE shipment_id = ?", "i", [$id]);

// Lấy timeline sự kiện từ shipment_events
$events = db_select(
    "SELECT e.*, u.username AS creator_name
     FROM shipment_events e
     LEFT JOIN users u ON u.id = e.created_by
     WHERE e.shipment_id = ?
     ORDER BY e.created_at ASC, e.id ASC",
    "i",
    [$id]
);

// Helper hàm lấy class badge theo trạng thái
function get_info_badge_class(string $status): string
{
    return match ($status) {
        'Booked'           => 'badge badge-booked',
        'In Transit'       => 'badge badge-transit',
        'At Port'          => 'badge badge-port',
        'Customs Hold'     => 'badge badge-hold',
        'Out for Delivery' => 'badge badge-delivery',
        'Delivered'        => 'badge badge-delivered',
        'Cancelled'        => 'badge badge-cancelled',
        default            => 'badge',
    };
}

render_header('Chi tiết vận đơn ' . htmlspecialchars($sh['tracking_no']));
?>
<div class="card">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
        <div>
            <h1>Vận đơn: <?= htmlspecialchars($sh['tracking_no']) ?></h1>
            <p class="muted">
                Trạng thái hiện tại: 
                <span class="<?= get_info_badge_class($sh['status']) ?>">
                    <?= htmlspecialchars($sh['status']) ?>
                </span>
                · Cảng đến: <strong><?= htmlspecialchars($sh['port_code']) ?></strong>
            </p>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;">
            <a href="/shipments/<?= htmlspecialchars((string)$id, ENT_QUOTES, 'UTF-8') ?>/documents/bill-of-lading" target="_blank" class="btn btn-sm" style="background:var(--teal);">📄 In Vận đơn (B/L)</a>
            <a href="/shipments/<?= htmlspecialchars((string)$id, ENT_QUOTES, 'UTF-8') ?>/documents/invoice" target="_blank" class="btn btn-sm" style="background:var(--deep);">🧾 In Hoá đơn cước</a>
            <a href="/shipments/<?= htmlspecialchars((string)$id, ENT_QUOTES, 'UTF-8') ?>" class="btn btn-sm" style="background:#5B6B7B;">💬 Thảo luận / Bình luận</a>
            <?php if ($isOwner && $sh['status'] === 'Booked'): ?>
                <a href="/shipments/<?= htmlspecialchars((string)$id, ENT_QUOTES, 'UTF-8') ?>/edit" class="btn btn-sm" style="background:var(--ok);">Sửa đơn</a>
                <form action="/shipments/<?= htmlspecialchars((string)$id, ENT_QUOTES, 'UTF-8') ?>/cancel" method="post" style="display:inline;" onsubmit="return confirm('Bạn có chắc chắn muốn huỷ đơn này?');">
                    <?= csrf_field() ?>
                    <button type="submit" class="btn btn-sm btn-danger">Huỷ đơn</button>
                </form>
            <?php endif; ?>
        </div>
    </div>
</div>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
    <!-- Thông tin người gửi / người nhận -->
    <div class="card">
        <h2>Thông tin Đối tác vận chuyển</h2>
        <table class="data">
            <tr>
                <th style="width:35%">Người gửi (Shipper)</th>
                <td>
                    <strong><?= htmlspecialchars($details['shipper_name'] ?? 'Chưa cập nhật') ?></strong><br>
                    <span class="muted"><?= nl2br(htmlspecialchars($details['shipper_address'] ?? '')) ?></span>
                </td>
            </tr>
            <tr>
                <th>Người nhận (Consignee)</th>
                <td>
                    <strong><?= htmlspecialchars($details['consignee_name'] ?? 'Chưa cập nhật') ?></strong><br>
                    <span class="muted"><?= nl2br(htmlspecialchars($details['consignee_address'] ?? '')) ?></span>
                </td>
            </tr>
        </table>
    </div>

    <!-- Thông tin Tuyến đường & Hàng hoá -->
    <div class="card">
        <h2>Hành trình & Quy cách hàng</h2>
        <table class="data">
            <tr>
                <th style="width:35%">Cảng xếp / Cảng dỡ</th>
                <td>
                    <strong><?= htmlspecialchars($details['origin_port'] ?? 'Chưa cập nhật') ?></strong> → 
                    <strong><?= htmlspecialchars($sh['port_code']) ?></strong>
                </td>
            </tr>
            <tr>
                <th>Mô tả hàng hoá</th>
                <td><?= htmlspecialchars($details['cargo_desc'] ?? 'Hàng tổng hợp') ?></td>
            </tr>
            <tr>
                <th>Loại hàng</th>
                <td><?= htmlspecialchars($details['cargo_type'] ?? 'Thường') ?></td>
            </tr>
            <tr>
                <th>Trọng lượng</th>
                <td><?= !empty($details['weight_kg']) ? number_format((float)$details['weight_kg'], 2, ',', '.') . ' kg' : 'Chưa cập nhật' ?></td>
            </tr>
            <tr>
                <th>Container</th>
                <td>
                    <?= !empty($details['container_qty']) ? htmlspecialchars((string)$details['container_qty']) . ' x ' . htmlspecialchars($details['container_type']) : 'Chưa cập nhật' ?>
                </td>
            </tr>
            <tr>
                <th>Lịch trình (ETD / ETA)</th>
                <td>
                    Khởi hành (ETD): <?= htmlspecialchars($details['etd'] ?? '—') ?><br>
                    Dự kiến đến (ETA): <?= htmlspecialchars($details['eta'] ?? '—') ?>
                </td>
            </tr>
        </table>
    </div>
</div>

<!-- Timeline trạng thái -->
<div class="card">
    <h2>Nhật ký hành trình & Sự kiện (Status Timeline)</h2>
    <?php if (empty($events)): ?>
        <p class="muted">Chưa ghi nhận sự kiện nào cho vận đơn này.</p>
    <?php else: ?>
        <div class="timeline">
            <?php foreach ($events as $ev): ?>
                <div class="timeline-item">
                    <div class="timeline-date">
                        <?= htmlspecialchars($ev['created_at']) ?>
                        <?php if (!empty($ev['location'])): ?>
                            · Địa điểm: <strong><?= htmlspecialchars($ev['location']) ?></strong>
                        <?php endif; ?>
                    </div>
                    <div class="timeline-title">
                        <span class="<?= get_info_badge_class($ev['status']) ?>">
                            <?= htmlspecialchars($ev['status']) ?>
                        </span>
                    </div>
                    <div class="timeline-desc">
                        <?= htmlspecialchars($ev['note'] ?? '') ?>
                        <?php if (!empty($ev['creator_name'])): ?>
                            <span class="muted">(Ghi nhận bởi: <?= htmlspecialchars($ev['creator_name']) ?>)</span>
                        <?php endif; ?>
                    </div>
                </div>
            <?php endforeach; ?>
        </div>
    <?php endif; ?>
</div>

<p style="margin-top:16px;">
    <a href="/shipments/mine" class="btn btn-sm">← Quay lại danh sách vận đơn của tôi</a>
</p>
<?php
render_footer();
