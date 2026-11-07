<?php
/**
 * shipment_edit.php — Chỉnh sửa thông tin đơn hàng (chỉ khi đang ở trạng thái Booked).
 */
$u = require_login();

$id = (int)($_GET['id'] ?? 0);
if ($id <= 0) {
    header('Location: /shipments/mine');
    exit;
}

// Kiểm tra vận đơn
$sh = db_select_one("SELECT * FROM shipments WHERE id = ?", "i", [$id]);
if (!$sh) {
    header('Location: /shipments/mine');
    exit;
}

// Chỉ chủ đơn mới sửa được
if ((int)$sh['customer_id'] !== (int)$u['id']) {
    http_response_code(403);
    render_header('403 — Từ chối');
    echo '<div class="card"><h1>403 — Không có quyền sửa</h1><p>Bạn không phải là chủ sở hữu của đơn hàng này.</p></div>';
    render_footer();
    exit;
}

// Chỉ được sửa khi đơn đang ở trạng thái Booked
if ($sh['status'] !== 'Booked') {
    render_header('Không thể chỉnh sửa');
    echo '<div class="card"><h1>Đơn hàng không thể chỉnh sửa</h1>'
        . '<p>Chỉ những đơn hàng ở trạng thái <strong>Booked</strong> mới được phép chỉnh sửa. Đơn hàng này đang ở trạng thái <strong>'
        . htmlspecialchars($sh['status']) . '</strong>.</p>'
        . '<p><a href="/shipments/' . htmlspecialchars((string)$id, ENT_QUOTES, 'UTF-8') . '/info" class="btn btn-sm">Quay lại chi tiết đơn hàng</a></p></div>';
    render_footer();
    exit;
}

$details = db_select_one("SELECT * FROM shipment_details WHERE shipment_id = ?", "i", [$id]) ?? [];
$ports = db_select("SELECT code, city, country FROM ports ORDER BY code ASC");

$error = null;
$shipper_name      = trim($_POST['shipper_name'] ?? ($details['shipper_name'] ?? ''));
$shipper_address   = trim($_POST['shipper_address'] ?? ($details['shipper_address'] ?? ''));
$consignee_name    = trim($_POST['consignee_name'] ?? ($details['consignee_name'] ?? ''));
$consignee_address = trim($_POST['consignee_address'] ?? ($details['consignee_address'] ?? ''));
$cargo_desc        = trim($_POST['cargo_desc'] ?? ($details['cargo_desc'] ?? ''));
$cargo_type        = $_POST['cargo_type'] ?? ($details['cargo_type'] ?? 'Thường');
$weight_kg         = $_POST['weight_kg'] ?? ($details['weight_kg'] ?? '');
$container_type    = $_POST['container_type'] ?? ($details['container_type'] ?? '20GP');
$container_qty     = $_POST['container_qty'] ?? ($details['container_qty'] ?? 1);
$origin_port       = $_POST['origin_port'] ?? ($details['origin_port'] ?? '');
$dest_port         = $_POST['dest_port'] ?? $sh['port_code'];
$etd               = $_POST['etd'] ?? ($details['etd'] ?? date('Y-m-d'));

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    csrf_verify();

    $weight_kg = (float)$weight_kg;
    $container_qty = (int)$container_qty;
    $validCargoTypes = ['Thường', 'Lạnh', 'Nguy hiểm'];
    $validContainerTypes = ['20GP', '40GP', '40HC'];
    $portCodes = array_column($ports, 'code');

    if (empty($shipper_name) || empty($shipper_address)) {
        $error = 'Vui lòng nhập đầy đủ tên và địa chỉ người gửi (Shipper).';
    } elseif (empty($consignee_name) || empty($consignee_address)) {
        $error = 'Vui lòng nhập đầy đủ tên và địa chỉ người nhận (Consignee).';
    } elseif (empty($cargo_desc)) {
        $error = 'Vui lòng nhập mô tả chi tiết hàng hoá.';
    } elseif (!in_array($cargo_type, $validCargoTypes, true)) {
        $error = 'Loại hàng hoá không hợp lệ.';
    } elseif ($weight_kg <= 0) {
        $error = 'Trọng lượng hàng hoá phải là số dương lớn hơn 0.';
    } elseif ($container_qty < 1 || $container_qty > 100) {
        $error = 'Số lượng container phải từ 1 đến 100.';
    } elseif (!in_array($container_type, $validContainerTypes, true)) {
        $error = 'Loại container không hợp lệ.';
    } elseif (!in_array($origin_port, $portCodes, true) || !in_array($dest_port, $portCodes, true)) {
        $error = 'Cảng đi hoặc cảng đến không tồn tại trong hệ thống.';
    } elseif ($origin_port === $dest_port) {
        $error = 'Cảng đi và cảng đến không được trùng nhau.';
    } elseif (!preg_match('/^\d{4}-\d{2}-\d{2}$/', $etd) || strtotime($etd) === false) {
        $error = 'Ngày dự kiến khởi hành (ETD) không hợp lệ.';
    } else {
        $eta = date('Y-m-d', strtotime($etd . ' + 14 days'));

        // Cập nhật cảng đến trong bảng shipments nếu có đổi
        if ($dest_port !== $sh['port_code']) {
            db_execute("UPDATE shipments SET port_code = ? WHERE id = ?", "si", [$dest_port, $id]);
        }

        // Cập nhật shipment_details
        if ($details) {
            db_execute(
                "UPDATE shipment_details SET shipper_name = ?, shipper_address = ?, consignee_name = ?, consignee_address = ?, cargo_desc = ?, cargo_type = ?, weight_kg = ?, container_type = ?, container_qty = ?, origin_port = ?, etd = ?, eta = ? WHERE shipment_id = ?",
                "ssssssdsisssi",
                [$shipper_name, $shipper_address, $consignee_name, $consignee_address, $cargo_desc, $cargo_type, $weight_kg, $container_type, $container_qty, $origin_port, $etd, $eta, $id]
            );
        } else {
            db_execute(
                "INSERT INTO shipment_details (shipment_id, shipper_name, shipper_address, consignee_name, consignee_address, cargo_desc, cargo_type, weight_kg, container_type, container_qty, origin_port, etd, eta) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                "issssssdsisss",
                [$id, $shipper_name, $shipper_address, $consignee_name, $consignee_address, $cargo_desc, $cargo_type, $weight_kg, $container_type, $container_qty, $origin_port, $etd, $eta]
            );
        }

        // Ghi lại sự kiện chỉnh sửa
        db_execute(
            "INSERT INTO shipment_events (shipment_id, status, location, note, created_by) VALUES (?, 'Booked', ?, 'Cập nhật thông tin chi tiết đơn hàng bởi khách hàng', ?)",
            "isi",
            [$id, $origin_port, (int)$u['id']]
        );

        header("Location: /shipments/{$id}/info");
        exit;
    }
}

render_header('Sửa vận đơn ' . htmlspecialchars($sh['tracking_no']));
?>
<div class="card">
    <h1>Chỉnh sửa vận đơn: <?= htmlspecialchars($sh['tracking_no']) ?></h1>
    <p class="muted">Cập nhật thông tin hàng hoá và hành trình cho đơn vận chuyển.</p>
    <?php if ($error) flash($error, 'error'); ?>

    <form action="/shipments/<?= htmlspecialchars((string)$id, ENT_QUOTES, 'UTF-8') ?>/edit" method="post">
        <?= csrf_field() ?>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
            <div>
                <h2>Người gửi (Shipper)</h2>
                <div class="form-row">
                    <label>Tên người gửi (*)</label>
                    <input type="text" name="shipper_name" value="<?= htmlspecialchars($shipper_name) ?>" required>
                </div>
                <div class="form-row">
                    <label>Địa chỉ người gửi (*)</label>
                    <textarea name="shipper_address" rows="3" required><?= htmlspecialchars($shipper_address) ?></textarea>
                </div>
            </div>

            <div>
                <h2>Người nhận (Consignee)</h2>
                <div class="form-row">
                    <label>Tên người nhận (*)</label>
                    <input type="text" name="consignee_name" value="<?= htmlspecialchars($consignee_name) ?>" required>
                </div>
                <div class="form-row">
                    <label>Địa chỉ người nhận (*)</label>
                    <textarea name="consignee_address" rows="3" required><?= htmlspecialchars($consignee_address) ?></textarea>
                </div>
            </div>
        </div>

        <h2 style="margin-top:20px;">Hành trình & Hàng hoá</h2>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;">
            <div class="form-row">
                <label>Cảng đi (*)</label>
                <select name="origin_port" required>
                    <?php foreach ($ports as $p): ?>
                        <option value="<?= htmlspecialchars($p['code']) ?>" <?= $origin_port === $p['code'] ? 'selected' : '' ?>>
                            <?= htmlspecialchars($p['code']) ?> — <?= htmlspecialchars($p['city']) ?>
                        </option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div class="form-row">
                <label>Cảng đến (*)</label>
                <select name="dest_port" required>
                    <?php foreach ($ports as $p): ?>
                        <option value="<?= htmlspecialchars($p['code']) ?>" <?= $dest_port === $p['code'] ? 'selected' : '' ?>>
                            <?= htmlspecialchars($p['code']) ?> — <?= htmlspecialchars($p['city']) ?>
                        </option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div class="form-row">
                <label>Ngày khởi hành (ETD) (*)</label>
                <input type="date" name="etd" value="<?= htmlspecialchars($etd) ?>" required>
            </div>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;">
            <div class="form-row">
                <label>Loại hàng (*)</label>
                <select name="cargo_type" required>
                    <option value="Thường" <?= $cargo_type === 'Thường' ? 'selected' : '' ?>>Thường</option>
                    <option value="Lạnh" <?= $cargo_type === 'Lạnh' ? 'selected' : '' ?>>Lạnh</option>
                    <option value="Nguy hiểm" <?= $cargo_type === 'Nguy hiểm' ? 'selected' : '' ?>>Nguy hiểm</option>
                </select>
            </div>
            <div class="form-row">
                <label>Loại container (*)</label>
                <select name="container_type" required>
                    <option value="20GP" <?= $container_type === '20GP' ? 'selected' : '' ?>>20GP</option>
                    <option value="40GP" <?= $container_type === '40GP' ? 'selected' : '' ?>>40GP</option>
                    <option value="40HC" <?= $container_type === '40HC' ? 'selected' : '' ?>>40HC</option>
                </select>
            </div>
            <div class="form-row">
                <label>Số lượng (*)</label>
                <input type="number" name="container_qty" min="1" max="100" value="<?= htmlspecialchars((string)$container_qty) ?>" required>
            </div>
        </div>

        <div style="display:grid;grid-template-columns:2fr 1fr;gap:16px;">
            <div class="form-row">
                <label>Mô tả hàng (*)</label>
                <input type="text" name="cargo_desc" value="<?= htmlspecialchars($cargo_desc) ?>" required>
            </div>
            <div class="form-row">
                <label>Trọng lượng (kg) (*)</label>
                <input type="number" step="0.01" min="1" name="weight_kg" value="<?= htmlspecialchars((string)$weight_kg) ?>" required>
            </div>
        </div>

        <div style="margin-top:20px;display:flex;gap:12px;">
            <button class="btn" type="submit">Lưu thay đổi</button>
            <a href="/shipments/<?= htmlspecialchars((string)$id, ENT_QUOTES, 'UTF-8') ?>/info" class="btn btn-sm" style="background:#5B6B7B;display:inline-flex;align-items:center;">Huỷ bỏ</a>
        </div>
    </form>
</div>
<?php
render_footer();
