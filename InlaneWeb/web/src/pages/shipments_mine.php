<?php
/**
 * shipments_mine.php — Danh sách vận đơn của người dùng hiện tại.
 */
$u = require_login();

$statusFilter = trim($_GET['status'] ?? '');
$searchQuery  = trim($_GET['q'] ?? '');
$page         = max(1, (int)($_GET['page'] ?? 1));
$perPage      = 10;
$offset       = ($page - 1) * $perPage;

// Xây dựng câu truy vấn an toàn bằng prepared statements
$whereClauses = ["s.customer_id = ?"];
$types = "i";
$params = [(int)$u['id']];

if ($statusFilter !== '') {
    $whereClauses[] = "s.status = ?";
    $types .= "s";
    $params[] = $statusFilter;
}

if ($searchQuery !== '') {
    $whereClauses[] = "s.tracking_no LIKE ?";
    $types .= "s";
    $params[] = '%' . $searchQuery . '%';
}

$whereSql = implode(' AND ', $whereClauses);

// Đếm tổng số bản ghi
$countSql = "SELECT COUNT(*) AS total FROM shipments s WHERE {$whereSql}";
$totalRow = db_select_one($countSql, $types, $params);
$totalRecords = $totalRow ? (int)$totalRow['total'] : 0;
$totalPages = max(1, (int)ceil($totalRecords / $perPage));

// Lấy danh sách vận đơn kèm chi tiết (nếu có)
$dataSql = "SELECT s.id, s.tracking_no, s.port_code, s.status,
                   d.cargo_desc, d.weight_kg, d.container_type, d.container_qty, d.origin_port, d.etd
            FROM shipments s
            LEFT JOIN shipment_details d ON d.shipment_id = s.id
            WHERE {$whereSql}
            ORDER BY s.id DESC
            LIMIT ? OFFSET ?";
$typesWithLimit = $types . "ii";
$paramsWithLimit = array_merge($params, [$perPage, $offset]);

$shipments = db_select($dataSql, $typesWithLimit, $paramsWithLimit);

// Helper hàm lấy class badge theo trạng thái
function get_status_badge_class(string $status): string
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

render_header('Đơn hàng của tôi');
?>
<div class="card">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
        <div>
            <h1>Vận đơn của tôi</h1>
            <p class="muted">Quản lý và tra cứu tiến trình các lô hàng của tài khoản <strong><?= htmlspecialchars($u['username']) ?></strong>.</p>
        </div>
        <div>
            <a href="/shipments/new" class="btn">+ Tạo đơn mới (Booking)</a>
        </div>
    </div>

    <!-- Bộ lọc & Tìm kiếm -->
    <form method="get" action="/shipments/mine" style="display:flex;gap:12px;margin:16px 0;flex-wrap:wrap;align-items:center;">
        <input type="text" name="q" value="<?= htmlspecialchars($searchQuery) ?>" placeholder="Tìm mã vận đơn..." style="padding:8px 12px;border:1px solid var(--line);border-radius:6px;font-size:14px;min-width:200px;">
        <select name="status" style="padding:8px 12px;border:1px solid var(--line);border-radius:6px;font-size:14px;">
            <option value="">-- Tất cả trạng thái --</option>
            <option value="Booked" <?= $statusFilter === 'Booked' ? 'selected' : '' ?>>Booked (Đã tạo)</option>
            <option value="In Transit" <?= $statusFilter === 'In Transit' ? 'selected' : '' ?>>In Transit (Đang vận chuyển)</option>
            <option value="At Port" <?= $statusFilter === 'At Port' ? 'selected' : '' ?>>At Port (Đã cập cảng)</option>
            <option value="Customs Hold" <?= $statusFilter === 'Customs Hold' ? 'selected' : '' ?>>Customs Hold (Giữ hải quan)</option>
            <option value="Out for Delivery" <?= $statusFilter === 'Out for Delivery' ? 'selected' : '' ?>>Out for Delivery (Đang giao)</option>
            <option value="Delivered" <?= $statusFilter === 'Delivered' ? 'selected' : '' ?>>Delivered (Đã giao hàng)</option>
            <option value="Cancelled" <?= $statusFilter === 'Cancelled' ? 'selected' : '' ?>>Cancelled (Đã huỷ)</option>
        </select>
        <button class="btn btn-sm" type="submit">Lọc dữ liệu</button>
        <?php if ($statusFilter !== '' || $searchQuery !== ''): ?>
            <a href="/shipments/mine" class="btn btn-sm" style="background:#5B6B7B;">Xoá bộ lọc</a>
        <?php endif; ?>
    </form>

    <?php if (empty($shipments)): ?>
        <p class="muted" style="padding:20px;text-align:center;background:var(--panelalt);border-radius:8px;">
            Không tìm thấy vận đơn nào phù hợp.
        </p>
    <?php else: ?>
        <div class="table-responsive">
            <table class="data">
                <thead>
                    <tr>
                        <th>Mã vận đơn</th>
                        <th>Tuyến vận tải</th>
                        <th>Hàng hoá</th>
                        <th>Container</th>
                        <th>Trạng thái</th>
                        <th>Thao tác</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($shipments as $sh): ?>
                        <tr>
                            <td>
                                <strong><a href="/shipments/<?= (int)$sh['id'] ?>/info"><?= htmlspecialchars($sh['tracking_no']) ?></a></strong>
                            </td>
                            <td>
                                <?= htmlspecialchars($sh['origin_port'] ?? '—') ?> → <strong><?= htmlspecialchars($sh['port_code']) ?></strong>
                                <?php if (!empty($sh['etd'])): ?>
                                    <div class="muted" style="font-size:11px;">ETD: <?= htmlspecialchars($sh['etd']) ?></div>
                                <?php endif; ?>
                            </td>
                            <td>
                                <?= htmlspecialchars($sh['cargo_desc'] ?? 'Chưa cập nhật') ?>
                                <?php if (!empty($sh['weight_kg'])): ?>
                                    <div class="muted" style="font-size:11px;"><?= number_format((float)$sh['weight_kg'], 0, ',', '.') ?> kg</div>
                                <?php endif; ?>
                            </td>
                            <td>
                                <?= !empty($sh['container_qty']) ? htmlspecialchars((string)$sh['container_qty']) . ' x ' . htmlspecialchars($sh['container_type']) : '—' ?>
                            </td>
                            <td>
                                <span class="<?= get_status_badge_class($sh['status']) ?>">
                                    <?= htmlspecialchars($sh['status']) ?>
                                </span>
                            </td>
                            <td style="white-space:nowrap;">
                                <a href="/shipments/<?= (int)$sh['id'] ?>/info" class="btn btn-sm" style="padding:4px 8px;font-size:12px;">Xem</a>
                                <a href="/shipments/<?= (int)$sh['id'] ?>" class="btn btn-sm" style="padding:4px 8px;font-size:12px;background:#5B6B7B;">Bình luận</a>

                                <?php if ($sh['status'] === 'Booked'): ?>
                                    <a href="/shipments/<?= (int)$sh['id'] ?>/edit" class="btn btn-sm" style="padding:4px 8px;font-size:12px;background:var(--teal);">Sửa</a>
                                    <form action="/shipments/<?= (int)$sh['id'] ?>/cancel" method="post" style="display:inline;" onsubmit="return confirm('Bạn có chắc chắn muốn huỷ vận đơn này?');">
                                        <?= csrf_field() ?>
                                        <button type="submit" class="btn btn-sm btn-danger" style="padding:4px 8px;font-size:12px;">Huỷ</button>
                                    </form>
                                <?php endif; ?>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>

        <!-- Phân trang -->
        <?php if ($totalPages > 1): ?>
            <div class="pagination">
                <span>Trang <?= $page ?> / <?= $totalPages ?> (Tổng <?= $totalRecords ?> đơn)</span>
                <?php for ($i = 1; $i <= $totalPages; $i++): ?>
                    <?php
                    $url = '/shipments/mine?page=' . $i;
                    if ($statusFilter !== '') $url .= '&status=' . urlencode($statusFilter);
                    if ($searchQuery !== '')  $url .= '&q=' . urlencode($searchQuery);
                    ?>
                    <?php if ($i === $page): ?>
                        <span class="active"><?= $i ?></span>
                    <?php else: ?>
                        <a href="<?= htmlspecialchars($url) ?>"><?= $i ?></a>
                    <?php endif; ?>
                <?php endfor; ?>
            </div>
        <?php endif; ?>
    <?php endif; ?>
</div>
<?php
render_footer();
