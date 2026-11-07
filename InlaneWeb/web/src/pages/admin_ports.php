<?php
/**
 * admin_ports.php — Quản lý danh mục cảng biển (Staff & Admin).
 */
$u = require_role(['admin', 'staff']);
$error = null;
$success = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    csrf_verify();
    $action = $_POST['action'] ?? '';

    if ($action === 'create') {
        $code    = strtoupper(trim($_POST['code'] ?? ''));
        $city    = trim($_POST['city'] ?? '');
        $country = trim($_POST['country'] ?? '');
        $volume  = (float)($_POST['volume'] ?? 0);

        if (empty($code) || mb_strlen($code) > 10) {
            $error = 'Mã cảng không được để trống và tối đa 10 ký tự.';
        } elseif (empty($city) || empty($country)) {
            $error = 'Vui lòng nhập đầy đủ thành phố và quốc gia.';
        } elseif ($volume < 0) {
            $error = 'Sản lượng TEU phải là số không âm.';
        } else {
            $existPort = db_select_one("SELECT id FROM ports WHERE code = ?", "s", [$code]);
            if ($existPort) {
                $error = 'Mã cảng này đã tồn tại trong danh mục.';
            } else {
                db_insert(
                    "INSERT INTO ports (code, city, country, volume) VALUES (?, ?, ?, ?)",
                    "sssd",
                    [$code, $city, $country, $volume]
                );
                $success = "Thêm mới cảng biển {$code} ({$city}) thành công!";
            }
        }
    } elseif ($action === 'edit') {
        $portId  = (int)($_POST['port_id'] ?? 0);
        $code    = strtoupper(trim($_POST['code'] ?? ''));
        $city    = trim($_POST['city'] ?? '');
        $country = trim($_POST['country'] ?? '');
        $volume  = (float)($_POST['volume'] ?? 0);

        $curPort = db_select_one("SELECT * FROM ports WHERE id = ?", "i", [$portId]);
        if (!$curPort) {
            $error = 'Cảng biển không tồn tại.';
        } elseif (empty($code) || empty($city) || empty($country) || $volume < 0) {
            $error = 'Vui lòng điền thông tin cảng hợp lệ.';
        } else {
            // Kiểm tra trùng code với cảng khác
            $dup = db_select_one("SELECT id FROM ports WHERE code = ? AND id != ?", "si", [$code, $portId]);
            if ($dup) {
                $error = 'Mã cảng này bị trùng với cảng khác.';
            } else {
                db_execute(
                    "UPDATE ports SET code = ?, city = ?, country = ?, volume = ? WHERE id = ?",
                    "sssdi",
                    [$code, $city, $country, $volume, $portId]
                );
                $success = "Cập nhật cảng {$code} thành công!";
            }
        }
    } elseif ($action === 'delete') {
        $portId = (int)($_POST['port_id'] ?? 0);
        $curPort = db_select_one("SELECT * FROM ports WHERE id = ?", "i", [$portId]);
        if (!$curPort) {
            $error = 'Cảng không tồn tại.';
        } else {
            $code = $curPort['code'];
            // Kiểm tra ràng buộc: Không xoá cảng đang được đơn hàng sử dụng
            $inDest = db_select_one("SELECT COUNT(*) AS cnt FROM shipments WHERE port_code = ?", "s", [$code]);
            $inOrig = db_select_one("SELECT COUNT(*) AS cnt FROM shipment_details WHERE origin_port = ?", "s", [$code]);

            $destCnt = $inDest ? (int)$inDest['cnt'] : 0;
            $origCnt = $inOrig ? (int)$inOrig['cnt'] : 0;

            if ($destCnt > 0 || $origCnt > 0) {
                $error = "Không thể xoá cảng {$code} vì đang có {$destCnt} đơn đến và {$origCnt} đơn đi sử dụng cảng này.";
            } else {
                db_execute("DELETE FROM ports WHERE id = ?", "i", [$portId]);
                $success = "Đã xoá cảng {$code} khỏi hệ thống!";
            }
        }
    }
}

$ports = db_select("SELECT * FROM ports ORDER BY id DESC");

render_header('Quản lý cảng biển');
?>
<div class="card">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
        <div>
            <h1>Quản lý cảng biển (Port Directory)</h1>
            <p class="muted">Thêm, sửa, xoá danh mục các cảng biển phục vụ hoạt động logistics.</p>
        </div>
        <button onclick="document.getElementById('createPortModal').style.display='block'" class="btn">+ Thêm cảng mới</button>
    </div>

    <?php
    if ($error) flash($error, 'error');
    if ($success) flash($success, 'success');
    ?>

    <div class="table-responsive" style="margin-top:16px;">
        <table class="data">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Mã cảng (Code)</th>
                    <th>Thành phố</th>
                    <th>Quốc gia</th>
                    <th>Sản lượng (Triệu TEU)</th>
                    <th>Thao tác</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($ports as $p): ?>
                    <tr>
                        <td>#<?= htmlspecialchars((string)$p['id'], ENT_QUOTES, 'UTF-8') ?></td>
                        <td><strong><a href="/ports/<?= htmlspecialchars($p['code'], ENT_QUOTES, 'UTF-8') ?>"><?= htmlspecialchars($p['code'], ENT_QUOTES, 'UTF-8') ?></a></strong></td>
                        <td><?= htmlspecialchars($p['city'], ENT_QUOTES, 'UTF-8') ?></td>
                        <td><?= htmlspecialchars($p['country'], ENT_QUOTES, 'UTF-8') ?></td>
                        <td><?= number_format((float)$p['volume'], 2, ',', '.') ?> TEU</td>
                        <td style="white-space:nowrap;">
                            <details style="display:inline-block;">
                                <summary class="btn btn-sm" style="padding:3px 8px;font-size:12px;background:var(--teal);cursor:pointer;list-style:none;">Sửa</summary>
                                <div style="position:absolute;z-index:100;background:#fff;border:2px solid var(--line);box-shadow:0 4px 12px rgba(0,0,0,0.15);padding:16px;border-radius:8px;min-width:280px;margin-top:4px;">
                                    <h4 style="margin:0 0 10px 0;">Sửa cảng <?= htmlspecialchars($p['code'], ENT_QUOTES, 'UTF-8') ?></h4>
                                    <form method="post" action="/admin/ports">
                                        <?= csrf_field() ?>
                                        <input type="hidden" name="action" value="edit">
                                        <input type="hidden" name="port_id" value="<?= htmlspecialchars((string)$p['id'], ENT_QUOTES, 'UTF-8') ?>">
                                        <div class="form-row">
                                            <label>Mã cảng</label>
                                            <input type="text" name="code" value="<?= htmlspecialchars($p['code'], ENT_QUOTES, 'UTF-8') ?>" required>
                                        </div>
                                        <div class="form-row">
                                            <label>Thành phố</label>
                                            <input type="text" name="city" value="<?= htmlspecialchars($p['city'], ENT_QUOTES, 'UTF-8') ?>" required>
                                        </div>
                                        <div class="form-row">
                                            <label>Quốc gia</label>
                                            <input type="text" name="country" value="<?= htmlspecialchars($p['country'], ENT_QUOTES, 'UTF-8') ?>" required>
                                        </div>
                                        <div class="form-row">
                                            <label>Sản lượng TEU (triệu)</label>
                                            <input type="number" step="0.01" min="0" name="volume" value="<?= htmlspecialchars((string)$p['volume'], ENT_QUOTES, 'UTF-8') ?>" required>
                                        </div>
                                        <button type="submit" class="btn btn-sm">Lưu</button>
                                    </form>
                                </div>
                            </details>

                            <form method="post" action="/admin/ports" style="display:inline;" onsubmit="return confirm('Bạn có chắc chắn muốn xoá cảng này?');">
                                <?= csrf_field() ?>
                                <input type="hidden" name="action" value="delete">
                                <input type="hidden" name="port_id" value="<?= htmlspecialchars((string)$p['id'], ENT_QUOTES, 'UTF-8') ?>">
                                <button type="submit" class="btn btn-sm btn-danger" style="padding:3px 8px;font-size:12px;">Xoá</button>
                            </form>
                        </td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
</div>

<!-- Modal thêm cảng mới -->
<div id="createPortModal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:999;overflow-y:auto;">
    <div style="background:#fff;max-width:480px;margin:50px auto;padding:24px;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,0.2);">
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--line);padding-bottom:12px;margin-bottom:16px;">
            <h2 style="margin:0;">Thêm cảng biển mới</h2>
            <button onclick="document.getElementById('createPortModal').style.display='none'" style="border:none;background:none;font-size:20px;cursor:pointer;">&times;</button>
        </div>
        <form method="post" action="/admin/ports">
            <?= csrf_field() ?>
            <input type="hidden" name="action" value="create">
            <div class="form-row">
                <label>Mã cảng (Port Code, vd: VN HPH, SG SIN) (*)</label>
                <input type="text" name="code" required placeholder="VN HPH">
            </div>
            <div class="form-row">
                <label>Thành phố (*)</label>
                <input type="text" name="city" required placeholder="Hai Phong">
            </div>
            <div class="form-row">
                <label>Quốc gia (*)</label>
                <input type="text" name="country" required placeholder="Vietnam">
            </div>
            <div class="form-row">
                <label>Sản lượng thông qua (Triệu TEU) (*)</label>
                <input type="number" step="0.01" min="0" name="volume" value="5.50" required>
            </div>
            <div style="display:flex;gap:10px;margin-top:20px;">
                <button type="submit" class="btn">Thêm cảng</button>
                <button type="button" onclick="document.getElementById('createPortModal').style.display='none'" class="btn" style="background:#5B6B7B;">Đóng</button>
            </div>
        </form>
    </div>
</div>
<?php
render_footer();
