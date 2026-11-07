<?php
/**
 * admin_shipments.php — Quản lý vận đơn (Staff & Admin).
 */
$u = require_role(['admin', 'staff']);

$statusFilter   = trim($_GET['status'] ?? '');
$portFilter     = trim($_GET['port'] ?? '');
$customerFilter = trim($_GET['customer'] ?? '');
$searchQuery    = trim($_GET['q'] ?? '');
$page           = max(1, (int)($_GET['page'] ?? 1));
$perPage        = 10;
$offset         = ($page - 1) * $perPage;

$whereClauses = ["1=1"];
$types = "";
$params = [];

if ($statusFilter !== '') {
    $whereClauses[] = "s.status = ?";
    $types .= "s";
    $params[] = $statusFilter;
}

if ($portFilter !== '') {
    $whereClauses[] = "s.port_code = ?";
    $types .= "s";
    $params[] = $portFilter;
}

if ($customerFilter !== '') {
    $whereClauses[] = "(u.username LIKE ? OR u.email LIKE ?)";
    $types .= "ss";
    $params[] = '%' . $customerFilter . '%';
    $params[] = '%' . $customerFilter . '%';
}

if ($searchQuery !== '') {
    $whereClauses[] = "s.tracking_no LIKE ?";
    $types .= "s";
    $params[] = '%' . $searchQuery . '%';
}

$whereSql = implode(' AND ', $whereClauses);

$countSql = "SELECT COUNT(*) AS total 
             FROM shipments s
             LEFT JOIN users u ON u.id = s.customer_id
             WHERE {$whereSql}";
$totalRow = db_select_one($countSql, $types, $params);
$totalRecords = $totalRow ? (int)$totalRow['total'] : 0;
$totalPages = max(1, (int)ceil($totalRecords / $perPage));

$dataSql = "SELECT s.id, s.tracking_no, s.port_code, s.status, s.customer_id,
                   u.username, u.email,
                   d.shipper_name, d.consignee_name, d.cargo_desc, d.weight_kg, d.container_type, d.container_qty, d.origin_port, d.etd
            FROM shipments s
            LEFT JOIN users u ON u.id = s.customer_id
            LEFT JOIN shipment_details d ON d.shipment_id = s.id
            WHERE {$whereSql}
            ORDER BY s.id DESC
            LIMIT ? OFFSET ?";
$typesWithLimit = $types . "ii";
$paramsWithLimit = array_merge($params, [$perPage, $offset]);

$shipments = db_select($dataSql, $typesWithLimit, $paramsWithLimit);

$ports = db_select("SELECT code, city FROM ports ORDER BY code ASC");

// Helper badge class
function get_adm_badge_class(string $status): string
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

render_header('Quản lý vận đơn');
?>
<div class="card">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
        <div>
            <h1>Quản lý vận đơn (Shipment Operations)</h1>
            <p class="muted">Theo dõi và cập nhật trạng thái mọi lô hàng trong hệ thống.</p>
        </div>
        <div>
            <a href="/shipments/new" class="btn">+ Tạo đơn mới</a>
        </div>
    </div>

    <?php
    if (!empty($_SESSION['admin_flash'])) {
        flash($_SESSION['admin_flash'], $_SESSION['admin_flash_type'] ?? 'info');
        unset($_SESSION['admin_flash'], $_SESSION['admin_flash_type']);
    }
    ?>

    <!-- Bộ lọc tìm kiếm -->
    <form method="get" action="/admin/shipments" style="display:flex;gap:10px;margin:16px 0;flex-wrap:wrap;align-items:center;">
        <input type="text" name="q" value="<?= htmlspecialchars($searchQuery, ENT_QUOTES, 'UTF-8') ?>" placeholder="Mã vận đơn..." style="padding:8px 12px;border:1px solid var(--line);border-radius:6px;min-width:140px;">
        <input type="text" name="customer" value="<?= htmlspecialchars($customerFilter, ENT_QUOTES, 'UTF-8') ?>" placeholder="Khách hàng / Email..." style="padding:8px 12px;border:1px solid var(--line);border-radius:6px;min-width:160px;">
        
        <select name="status" style="padding:8px 12px;border:1px solid var(--line);border-radius:6px;">
            <option value="">-- Trạng thái --</option>
            <?php foreach (['Booked', 'In Transit', 'At Port', 'Customs Hold', 'Out for Delivery', 'Delivered', 'Cancelled'] as $st): ?>
                <option value="<?= $st ?>" <?= $statusFilter === $st ? 'selected' : '' ?>><?= $st ?></option>
            <?php endforeach; ?>
        </select>

        <select name="port" style="padding:8px 12px;border:1px solid var(--line);border-radius:6px;">
            <option value="">-- Cảng đến --</option>
            <?php foreach ($ports as $p): ?>
                <option value="<?= htmlspecialchars($p['code'], ENT_QUOTES, 'UTF-8') ?>" <?= $portFilter === $p['code'] ? 'selected' : '' ?>>
                    <?= htmlspecialchars($p['code'], ENT_QUOTES, 'UTF-8') ?> (<?= htmlspecialchars($p['city'], ENT_QUOTES, 'UTF-8') ?>)
                </option>
            <?php endforeach; ?>
        </select>

        <button type="submit" class="btn btn-sm">Lọc</button>
        <?php if ($statusFilter !== '' || $portFilter !== '' || $customerFilter !== '' || $searchQuery !== ''): ?>
            <a href="/admin/shipments" class="btn btn-sm" style="background:#5B6B7B;">Xoá lọc</a>
        <?php endif; ?>
    </form>

    <div class="table-responsive">
        <table class="data">
            <thead>
                <tr>
                    <th>Mã B/L</th>
                    <th>Khách hàng</th>
                    <th>Tuyến đường</th>
                    <th>Hàng hoá</th>
                    <th>Trạng thái</th>
                    <th>Cập nhật trạng thái</th>
                    <th>Chi tiết</th>
                </tr>
            </thead>
            <tbody>
                <?php if (empty($shipments)): ?>
                    <tr><td colspan="7" style="text-align:center;padding:24px;" class="muted">Không có vận đơn nào phù hợp với bộ lọc.</td></tr>
                <?php else: ?>
                    <?php foreach ($shipments as $sh): ?>
                        <tr>
                            <td>
                                <strong><a href="/shipments/<?= htmlspecialchars((string)$sh['id'], ENT_QUOTES, 'UTF-8') ?>/info"><?= htmlspecialchars($sh['tracking_no'], ENT_QUOTES, 'UTF-8') ?></a></strong>
                            </td>
                            <td>
                                <strong><?= htmlspecialchars($sh['username'] ?? 'Khách #' . $sh['customer_id'], ENT_QUOTES, 'UTF-8') ?></strong><br>
                                <span class="muted"><?= htmlspecialchars($sh['email'] ?? '—', ENT_QUOTES, 'UTF-8') ?></span>
                            </td>
                            <td>
                                <?= htmlspecialchars($sh['origin_port'] ?? '—', ENT_QUOTES, 'UTF-8') ?> → <strong><?= htmlspecialchars($sh['port_code'], ENT_QUOTES, 'UTF-8') ?></strong>
                                <?php if (!empty($sh['etd'])): ?>
                                    <div class="muted" style="font-size:11px;">ETD: <?= htmlspecialchars($sh['etd'], ENT_QUOTES, 'UTF-8') ?></div>
                                <?php endif; ?>
                            </td>
                            <td>
                                <?= htmlspecialchars($sh['cargo_desc'] ?? 'Hàng xuất khẩu', ENT_QUOTES, 'UTF-8') ?><br>
                                <span class="muted" style="font-size:11px;">
                                    <?= !empty($sh['container_qty']) ? htmlspecialchars((string)$sh['container_qty'], ENT_QUOTES, 'UTF-8') . 'x' . htmlspecialchars($sh['container_type'], ENT_QUOTES, 'UTF-8') : '' ?>
                                    <?= !empty($sh['weight_kg']) ? ' · ' . number_format((float)$sh['weight_kg'], 0, ',', '.') . 'kg' : '' ?>
                                </span>
                            </td>
                            <td>
                                <span class="<?= get_adm_badge_class($sh['status']) ?>">
                                    <?= htmlspecialchars($sh['status'], ENT_QUOTES, 'UTF-8') ?>
                                </span>
                            </td>
                            <td>
                                <!-- Form nhanh cập nhật trạng thái -->
                                <details style="display:inline-block;">
                                    <summary class="btn btn-sm" style="padding:4px 8px;font-size:12px;background:var(--deep);cursor:pointer;list-style:none;">Đổi trạng thái</summary>
                                    <div style="position:absolute;z-index:100;background:#fff;border:2px solid var(--line);box-shadow:0 4px 12px rgba(0,0,0,0.15);padding:16px;border-radius:8px;min-width:320px;margin-top:4px;">
                                        <h4 style="margin:0 0 10px 0;">Cập nhật đơn <?= htmlspecialchars($sh['tracking_no'], ENT_QUOTES, 'UTF-8') ?></h4>
                                        <form method="post" action="/admin/shipments/<?= htmlspecialchars((string)$sh['id'], ENT_QUOTES, 'UTF-8') ?>/status">
                                            <?= csrf_field() ?>
                                            <div class="form-row">
                                                <label>Trạng thái mới (*)</label>
                                                <select name="status" required>
                                                    <?php foreach (['Booked', 'In Transit', 'At Port', 'Customs Hold', 'Out for Delivery', 'Delivered', 'Cancelled'] as $st): ?>
                                                        <option value="<?= $st ?>" <?= $sh['status'] === $st ? 'selected' : '' ?>><?= $st ?></option>
                                                    <?php endforeach; ?>
                                                </select>
                                            </div>
                                            <div class="form-row">
                                                <label>Địa điểm ghi nhận</label>
                                                <input type="text" name="location" placeholder="Ví dụ: Cảng Hải Phòng / Kho Tân Cảng">
                                            </div>
                                            <div class="form-row">
                                                <label>Ghi chú tiến trình</label>
                                                <textarea name="note" rows="2" placeholder="Ghi chú thêm..."></textarea>
                                            </div>
                                            <button type="submit" class="btn btn-sm" style="width:100%;">Cập nhật &amp; Báo khách</button>
                                        </form>
                                    </div>
                                </details>
                            </td>
                            <td>
                                <a href="/shipments/<?= htmlspecialchars((string)$sh['id'], ENT_QUOTES, 'UTF-8') ?>/info" class="btn btn-sm" style="padding:4px 8px;font-size:12px;">Xem</a>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                <?php endif; ?>
            </tbody>
        </table>
    </div>

    <!-- Phân trang -->
    <?php if ($totalPages > 1): ?>
        <div class="pagination">
            <span>Trang <?= htmlspecialchars((string)$page, ENT_QUOTES, 'UTF-8') ?> / <?= htmlspecialchars((string)$totalPages, ENT_QUOTES, 'UTF-8') ?> (Tổng <?= htmlspecialchars((string)$totalRecords, ENT_QUOTES, 'UTF-8') ?> đơn)</span>
            <?php for ($i = 1; $i <= $totalPages; $i++): ?>
                <?php
                $url = '/admin/shipments?page=' . $i;
                if ($statusFilter !== '')   $url .= '&status=' . urlencode($statusFilter);
                if ($portFilter !== '')     $url .= '&port=' . urlencode($portFilter);
                if ($customerFilter !== '') $url .= '&customer=' . urlencode($customerFilter);
                if ($searchQuery !== '')    $url .= '&q=' . urlencode($searchQuery);
                ?>
                <?php if ($i === $page): ?>
                    <span class="active"><?= htmlspecialchars((string)$i, ENT_QUOTES, 'UTF-8') ?></span>
                <?php else: ?>
                    <a href="<?= htmlspecialchars($url, ENT_QUOTES, 'UTF-8') ?>"><?= htmlspecialchars((string)$i, ENT_QUOTES, 'UTF-8') ?></a>
                <?php endif; ?>
            <?php endfor; ?>
        </div>
    <?php endif; ?>
</div>
<?php
render_footer();
