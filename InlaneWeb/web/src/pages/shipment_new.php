<?php
/**
 * shipment_new.php — Tạo đơn hàng / booking mới.
 */
$u = require_login();
$error = null;

// Lấy danh sách cảng có sẵn từ bảng ports
$ports = db_select("SELECT code, city, country FROM ports ORDER BY code ASC");

// Khởi tạo giá trị mặc định hoặc từ query parameters (từ trang báo giá /quote)
$shipper_name      = trim($_POST['shipper_name'] ?? '');
$shipper_address   = trim($_POST['shipper_address'] ?? '');
$consignee_name    = trim($_POST['consignee_name'] ?? '');
$consignee_address = trim($_POST['consignee_address'] ?? '');
$cargo_desc        = trim($_POST['cargo_desc'] ?? '');
$cargo_type        = $_POST['cargo_type'] ?? 'Thường';
$weight_kg         = $_POST['weight_kg'] ?? ($_GET['weight'] ?? '');
$container_type    = $_POST['container_type'] ?? ($_GET['type'] ?? '20GP');
$container_qty     = $_POST['container_qty'] ?? ($_GET['qty'] ?? '1');
$origin_port       = $_POST['origin_port'] ?? ($_GET['origin'] ?? '');
$dest_port         = $_POST['dest_port'] ?? ($_GET['dest'] ?? '');
$etd               = $_POST['etd'] ?? date('Y-m-d', strtotime('+7 days'));

// Nếu chưa điền shipper thì lấy thông tin từ user_profiles
if (empty($shipper_name) && empty($shipper_address)) {
    $profile = db_select_one("SELECT full_name, company, address FROM user_profiles WHERE user_id = ?", "i", [(int)$u['id']]);
    if ($profile) {
        $shipper_name = $profile['full_name'] ?: ($profile['company'] ?: $u['username']);
        $shipper_address = $profile['address'] ?: '';
    }
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    csrf_verify();

    $weight_kg = (float)$weight_kg;
    $container_qty = (int)$container_qty;

    // Validate dữ liệu
    $validCargoTypes = ['Thường', 'Lạnh', 'Nguy hiểm'];
    $validContainerTypes = ['20GP', '40GP', '40HC'];

    // Lấy danh sách mã cảng hợp lệ
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
        $error = 'Ngày dự kiến khởi hành (ETD) không hợp lệ (định dạng YYYY-MM-DD).';
    } else {
        // Sinh mã vận đơn duy nhất: ILF + 4 chữ số + 2 ký tự mã nước của cảng đến
        // Tìm thông tin nước của cảng đến
        $destPortRow = null;
        foreach ($ports as $p) {
            if ($p['code'] === $dest_port) {
                $destPortRow = $p;
                break;
            }
        }
        $countryCode = 'XX';
        if ($destPortRow) {
            // Lấy 2 chữ cái đầu của code hoặc country
            $codeParts = explode(' ', $destPortRow['code']);
            $countryCode = strtoupper(substr($codeParts[0] ?? 'VN', 0, 2));
        }

        // Đảm bảo mã tracking_no là duy nhất
        $tracking_no = '';
        for ($i = 0; $i < 10; $i++) {
            $candidate = 'ILF' . str_pad((string)random_int(1000, 9999), 4, '0', STR_PAD_LEFT) . $countryCode;
            $existTrack = db_select_one("SELECT id FROM shipments WHERE tracking_no = ?", "s", [$candidate]);
            if (!$existTrack) {
                $tracking_no = $candidate;
                break;
            }
        }

        if (empty($tracking_no)) {
            $tracking_no = 'ILF' . time() . $countryCode;
        }

        // Tính ngày dự kiến đến cảng ETA (khoảng 14 ngày sau ETD)
        $eta = date('Y-m-d', strtotime($etd . ' + 14 days'));

        // 1. INSERT vào shipments
        $shipmentId = db_insert(
            "INSERT INTO shipments (tracking_no, port_code, status, customer_id) VALUES (?, ?, 'Booked', ?)",
            "ssi",
            [$tracking_no, $dest_port, (int)$u['id']]
        );

        if ($shipmentId > 0) {
            // 2. INSERT vào shipment_details
            db_execute(
                "INSERT INTO shipment_details (shipment_id, shipper_name, shipper_address, consignee_name, consignee_address, cargo_desc, cargo_type, weight_kg, container_type, container_qty, origin_port, etd, eta) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                "issssssdsisss",
                [
                    $shipmentId, $shipper_name, $shipper_address, $consignee_name, $consignee_address,
                    $cargo_desc, $cargo_type, $weight_kg, $container_type, $container_qty,
                    $origin_port, $etd, $eta
                ]
            );

            // 3. Tạo sự kiện đầu tiên trong shipment_events
            db_execute(
                "INSERT INTO shipment_events (shipment_id, status, location, note, created_by) VALUES (?, 'Booked', ?, 'Đơn hàng được khởi tạo thành công bởi khách hàng', ?)",
                "isi",
                [$shipmentId, $origin_port, (int)$u['id']]
            );

            // 4. Tạo thông báo cho khách hàng
            $notifMsg = "Đơn vận chuyển {$tracking_no} đã được tạo thành công với trạng thái Booked.";
            db_insert(
                "INSERT INTO notifications (user_id, shipment_id, message) VALUES (?, ?, ?)",
                "iis",
                [(int)$u['id'], $shipmentId, $notifMsg]
            );

            // 5. Gửi email xác nhận vào mail_outbox
            $mailSubject = "Xác nhận đặt đơn vận chuyển: {$tracking_no}";
            $mailBody = "Kính gửi {$shipper_name},\n\n"
                . "Đơn vận chuyển của bạn đã được tiếp nhận vào hệ thống IlFreight Logistics.\n"
                . "- Mã vận đơn: {$tracking_no}\n"
                . "- Tuyến vận tải: {$origin_port} → {$dest_port}\n"
                . "- Hàng hoá: {$cargo_desc} ({$weight_kg} kg)\n"
                . "- Loại container: {$container_qty} x {$container_type}\n"
                . "- Ngày dự kiến khởi hành (ETD): {$etd}\n\n"
                . "Bạn có thể theo dõi tiến trình đơn hàng tại: " . app_base_url() . "/shipments/{$shipmentId}/info\n\n"
                . "Trân trọng,\nIlFreight Logistics";

            db_insert(
                "INSERT INTO mail_outbox (to_email, subject, body) VALUES (?, ?, ?)",
                "sss",
                [$u['email'], $mailSubject, $mailBody]
            );

            $_SESSION['flash_msg'] = "Tạo đơn hàng thành công! Mã vận đơn của bạn là {$tracking_no}.";
            $_SESSION['flash_type'] = 'success';
            header("Location: /shipments/{$shipmentId}/info");
            exit;
        } else {
            $error = 'Có lỗi xảy ra khi tạo đơn hàng. Vui lòng thử lại sau.';
        }
    }
}

render_header('Tạo đơn vận chuyển mới');
?>
<div class="card">
    <h1>Tạo đơn vận chuyển (Booking)</h1>
    <p class="muted">Vui lòng điền đầy đủ thông tin bên dưới để khởi tạo vận đơn đường biển.</p>
    <?php if ($error) flash($error, 'error'); ?>

    <form action="/shipments/new" method="post">
        <?= csrf_field() ?>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
            <div>
                <h2>Thông tin Người gửi (Shipper)</h2>
                <div class="form-row">
                    <label>Tên người gửi / Công ty gửi (*)</label>
                    <input type="text" name="shipper_name" value="<?= htmlspecialchars($shipper_name) ?>" required placeholder="Tên đơn vị gửi hàng">
                </div>
                <div class="form-row">
                    <label>Địa chỉ lấy hàng (*)</label>
                    <textarea name="shipper_address" rows="3" required placeholder="Địa chỉ chi tiết người gửi"><?= htmlspecialchars($shipper_address) ?></textarea>
                </div>
            </div>

            <div>
                <h2>Thông tin Người nhận (Consignee)</h2>
                <div class="form-row">
                    <label>Tên người nhận / Công ty nhận (*)</label>
                    <input type="text" name="consignee_name" value="<?= htmlspecialchars($consignee_name) ?>" required placeholder="Tên đơn vị nhận hàng">
                </div>
                <div class="form-row">
                    <label>Địa chỉ giao hàng (*)</label>
                    <textarea name="consignee_address" rows="3" required placeholder="Địa chỉ chi tiết người nhận"><?= htmlspecialchars($consignee_address) ?></textarea>
                </div>
            </div>
        </div>

        <h2 style="margin-top:20px;">Thông tin Tuyến vận tải & Hàng hoá</h2>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;">
            <div class="form-row">
                <label>Cảng đi (Origin Port) (*)</label>
                <select name="origin_port" required>
                    <option value="">-- Chọn cảng đi --</option>
                    <?php foreach ($ports as $p): ?>
                        <option value="<?= htmlspecialchars($p['code']) ?>" <?= $origin_port === $p['code'] ? 'selected' : '' ?>>
                            <?= htmlspecialchars($p['code']) ?> — <?= htmlspecialchars($p['city']) ?>, <?= htmlspecialchars($p['country']) ?>
                        </option>
                    <?php endforeach; ?>
                </select>
            </div>

            <div class="form-row">
                <label>Cảng đến (Destination Port) (*)</label>
                <select name="dest_port" required>
                    <option value="">-- Chọn cảng đến --</option>
                    <?php foreach ($ports as $p): ?>
                        <option value="<?= htmlspecialchars($p['code']) ?>" <?= $dest_port === $p['code'] ? 'selected' : '' ?>>
                            <?= htmlspecialchars($p['code']) ?> — <?= htmlspecialchars($p['city']) ?>, <?= htmlspecialchars($p['country']) ?>
                        </option>
                    <?php endforeach; ?>
                </select>
            </div>

            <div class="form-row">
                <label>Ngày dự kiến khởi hành (ETD) (*)</label>
                <input type="date" name="etd" value="<?= htmlspecialchars($etd) ?>" required>
            </div>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;">
            <div class="form-row">
                <label>Loại hàng hoá (*)</label>
                <select name="cargo_type" required>
                    <option value="Thường" <?= $cargo_type === 'Thường' ? 'selected' : '' ?>>Hàng thông thường</option>
                    <option value="Lạnh" <?= $cargo_type === 'Lạnh' ? 'selected' : '' ?>>Hàng lạnh / Bảo quản nhiệt</option>
                    <option value="Nguy hiểm" <?= $cargo_type === 'Nguy hiểm' ? 'selected' : '' ?>>Hàng hoá chất / Nguy hiểm (DG)</option>
                </select>
            </div>

            <div class="form-row">
                <label>Loại container (*)</label>
                <select name="container_type" required>
                    <option value="20GP" <?= $container_type === '20GP' ? 'selected' : '' ?>>20' General Purpose (20GP)</option>
                    <option value="40GP" <?= $container_type === '40GP' ? 'selected' : '' ?>>40' General Purpose (40GP)</option>
                    <option value="40HC" <?= $container_type === '40HC' ? 'selected' : '' ?>>40' High Cube (40HC)</option>
                </select>
            </div>

            <div class="form-row">
                <label>Số lượng container (*)</label>
                <input type="number" name="container_qty" min="1" max="100" value="<?= htmlspecialchars((string)$container_qty) ?>" required>
            </div>
        </div>

        <div style="display:grid;grid-template-columns:2fr 1fr;gap:16px;">
            <div class="form-row">
                <label>Mô tả chi tiết hàng hoá (*)</label>
                <input type="text" name="cargo_desc" value="<?= htmlspecialchars($cargo_desc) ?>" required placeholder="Ví dụ: May mặc, máy móc viễn thông, hạt cà phê đóng bao...">
            </div>
            <div class="form-row">
                <label>Tổng trọng lượng (kg) (*)</label>
                <input type="number" step="0.01" min="1" name="weight_kg" value="<?= htmlspecialchars((string)$weight_kg) ?>" required placeholder="Ví dụ: 12500">
            </div>
        </div>

        <div style="margin-top:20px;display:flex;gap:12px;">
            <button class="btn" type="submit">Xác nhận tạo đơn hàng</button>
            <a href="/shipments/mine" class="btn btn-sm" style="background:#5B6B7B;display:inline-flex;align-items:center;">Huỷ bỏ</a>
        </div>
    </form>
</div>
<?php
render_footer();
