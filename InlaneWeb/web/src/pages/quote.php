<?php
/**
 * quote.php — Công cụ tính và tra cứu báo giá cước vận tải ước lượng.
 */
$ports = db_select("SELECT code, city, country FROM ports ORDER BY code ASC");

$origin_port    = trim($_GET['origin'] ?? '');
$dest_port      = trim($_GET['dest'] ?? '');
$container_type = trim($_GET['type'] ?? '20GP');
$container_qty  = max(1, (int)($_GET['qty'] ?? 1));
$weight_kg      = (float)($_GET['weight'] ?? 10000);

$hasCalculated = (!empty($origin_port) && !empty($dest_port));
$error = null;
$quoteResult = null;

if ($hasCalculated) {
    if ($origin_port === $dest_port) {
        $error = 'Cảng đi và cảng đến không được trùng nhau.';
    } else {
        // Tra giá cơ sở trong bảng freight_rates
        $rateRow = db_select_one(
            "SELECT base_price_usd FROM freight_rates WHERE origin_port = ? AND dest_port = ? AND container_type = ?",
            "sss",
            [$origin_port, $dest_port, $container_type]
        );

        $isCustomRate = false;
        if ($rateRow) {
            $basePrice = (float)$rateRow['base_price_usd'];
            $isCustomRate = true;
        } else {
            // Giá mặc định theo quy chuẩn loại container
            $basePrice = match ($container_type) {
                '40HC'  => 2400.00,
                '40GP'  => 2000.00,
                default => 1200.00,
            };
        }

        $oceanFreight = $basePrice * $container_qty;
        $thcFee = 150.00 * $container_qty;
        $docFee = 50.00;
        $overweightFee = ($weight_kg > 15000) ? 250.00 : 0.00;

        $totalUsd = $oceanFreight + $thcFee + $docFee + $overweightFee;
        $exchangeRate = 25400;
        $totalVnd = $totalUsd * $exchangeRate;

        $quoteResult = [
            'origin'        => $origin_port,
            'dest'          => $dest_port,
            'type'          => $container_type,
            'qty'           => $container_qty,
            'weight'        => $weight_kg,
            'base_price'    => $basePrice,
            'is_custom'     => $isCustomRate,
            'ocean_freight' => $oceanFreight,
            'thc_fee'       => $thcFee,
            'doc_fee'       => $docFee,
            'overweight_fee'=> $overweightFee,
            'total_usd'     => $totalUsd,
            'total_vnd'     => $totalVnd,
        ];
    }
}

$u = current_user();

render_header('Tra cứu báo giá cước');
?>
<div class="hero">
    <h1>Báo giá cước vận tải đường biển tự động</h1>
    <p>Ước tính cước container FCL và các khoản phụ phí vận tải minh bạch, nhanh chóng chỉ trong vài giây.</p>
</div>

<div class="card">
    <h2>Nhập thông số tuyến hàng &amp; Quy cách</h2>
    <?php if ($error) flash($error, 'error'); ?>

    <form method="get" action="/quote" style="margin-top:16px;">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
            <div class="form-row">
                <label>Cảng đi (Port of Loading - POL) (*)</label>
                <select name="origin" required>
                    <option value="">-- Chọn cảng đi --</option>
                    <?php foreach ($ports as $p): ?>
                        <option value="<?= htmlspecialchars($p['code'], ENT_QUOTES, 'UTF-8') ?>" <?= $origin_port === $p['code'] ? 'selected' : '' ?>>
                            <?= htmlspecialchars($p['code'], ENT_QUOTES, 'UTF-8') ?> — <?= htmlspecialchars($p['city'], ENT_QUOTES, 'UTF-8') ?>, <?= htmlspecialchars($p['country'], ENT_QUOTES, 'UTF-8') ?>
                        </option>
                    <?php endforeach; ?>
                </select>
            </div>

            <div class="form-row">
                <label>Cảng đến (Port of Discharge - POD) (*)</label>
                <select name="dest" required>
                    <option value="">-- Chọn cảng đến --</option>
                    <?php foreach ($ports as $p): ?>
                        <option value="<?= htmlspecialchars($p['code'], ENT_QUOTES, 'UTF-8') ?>" <?= $dest_port === $p['code'] ? 'selected' : '' ?>>
                            <?= htmlspecialchars($p['code'], ENT_QUOTES, 'UTF-8') ?> — <?= htmlspecialchars($p['city'], ENT_QUOTES, 'UTF-8') ?>, <?= htmlspecialchars($p['country'], ENT_QUOTES, 'UTF-8') ?>
                        </option>
                    <?php endforeach; ?>
                </select>
            </div>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;">
            <div class="form-row">
                <label>Loại container (*)</label>
                <select name="type">
                    <option value="20GP" <?= $container_type === '20GP' ? 'selected' : '' ?>>20' General Purpose (20GP)</option>
                    <option value="40GP" <?= $container_type === '40GP' ? 'selected' : '' ?>>40' General Purpose (40GP)</option>
                    <option value="40HC" <?= $container_type === '40HC' ? 'selected' : '' ?>>40' High Cube (40HC)</option>
                </select>
            </div>

            <div class="form-row">
                <label>Số lượng container (*)</label>
                <input type="number" min="1" max="50" name="qty" value="<?= htmlspecialchars((string)$container_qty, ENT_QUOTES, 'UTF-8') ?>" required>
            </div>

            <div class="form-row">
                <label>Trọng lượng hàng ước tính (kg) (*)</label>
                <input type="number" step="100" min="500" name="weight" value="<?= htmlspecialchars((string)$weight_kg, ENT_QUOTES, 'UTF-8') ?>" required>
            </div>
        </div>

        <div style="margin-top:10px;">
            <button type="submit" class="btn">Tính toán chi phí</button>
        </div>
    </form>
</div>

<?php if ($quoteResult): ?>
    <div class="card" style="border-top:4px solid var(--ok);">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;">
            <div>
                <h2>Kết quả ước tính chi phí vận chuyển</h2>
                <p class="muted">
                    Tuyến: <strong><?= htmlspecialchars($quoteResult['origin'], ENT_QUOTES, 'UTF-8') ?></strong> → 
                    <strong><?= htmlspecialchars($quoteResult['dest'], ENT_QUOTES, 'UTF-8') ?></strong> · 
                    Quy cách: <strong><?= htmlspecialchars((string)$quoteResult['qty'], ENT_QUOTES, 'UTF-8') ?> x <?= htmlspecialchars($quoteResult['type'], ENT_QUOTES, 'UTF-8') ?></strong>
                    (<?= number_format($quoteResult['weight'], 0, ',', '.') ?> kg)
                </p>
            </div>
            <div>
                <?php if ($u): ?>
                    <?php
                    $bookUrl = '/shipments/new?origin=' . urlencode($quoteResult['origin'])
                        . '&dest=' . urlencode($quoteResult['dest'])
                        . '&type=' . urlencode($quoteResult['type'])
                        . '&qty=' . urlencode((string)$quoteResult['qty'])
                        . '&weight=' . urlencode((string)$quoteResult['weight']);
                    ?>
                    <a href="<?= htmlspecialchars($bookUrl, ENT_QUOTES, 'UTF-8') ?>" class="btn" style="background:var(--ok);font-size:16px;">
                        ✓ Đặt chỗ với báo giá này
                    </a>
                <?php else: ?>
                    <a href="/login" class="btn" style="background:var(--deep);">
                        Đăng nhập để đặt chỗ trực tuyến
                    </a>
                <?php endif; ?>
            </div>
        </div>

        <table class="data" style="margin-top:16px;">
            <thead>
                <tr>
                    <th>Hạng mục chi phí</th>
                    <th style="text-align:center;width:15%;">Số lượng</th>
                    <th style="text-align:right;width:20%;">Đơn giá</th>
                    <th style="text-align:right;width:25%;">Thành tiền (USD)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>
                        <strong>Cước biển quốc tế (Ocean Freight)</strong><br>
                        <span class="muted" style="font-size:12px;">
                            <?= $quoteResult['is_custom'] ? 'Áp dụng biểu giá ưu đãi hợp đồng' : 'Biểu giá cước tiêu chuẩn' ?>
                        </span>
                    </td>
                    <td style="text-align:center;"><?= htmlspecialchars((string)$quoteResult['qty'], ENT_QUOTES, 'UTF-8') ?></td>
                    <td style="text-align:right;">$<?= number_format($quoteResult['base_price'], 2) ?></td>
                    <td style="text-align:right;font-weight:bold;">$<?= number_format($quoteResult['ocean_freight'], 2) ?></td>
                </tr>
                <tr>
                    <td>
                        <strong>Phí xếp dỡ tại cảng (THC)</strong>
                    </td>
                    <td style="text-align:center;"><?= htmlspecialchars((string)$quoteResult['qty'], ENT_QUOTES, 'UTF-8') ?></td>
                    <td style="text-align:right;">$150.00</td>
                    <td style="text-align:right;font-weight:bold;">$<?= number_format($quoteResult['thc_fee'], 2) ?></td>
                </tr>
                <tr>
                    <td>
                        <strong>Phí phát hành chứng từ B/L (Documentation Fee)</strong>
                    </td>
                    <td style="text-align:center;">1</td>
                    <td style="text-align:right;">$50.00</td>
                    <td style="text-align:right;font-weight:bold;">$50.00</td>
                </tr>
                <?php if ($quoteResult['overweight_fee'] > 0): ?>
                    <tr>
                        <td>
                            <strong>Phụ phí hàng nặng (Overweight Surcharge)</strong><br>
                            <span class="muted" style="font-size:12px;">Áp dụng cho tải trọng vượt 15,000 kg</span>
                        </td>
                        <td style="text-align:center;">1</td>
                        <td style="text-align:right;">$250.00</td>
                        <td style="text-align:right;font-weight:bold;">$250.00</td>
                    </tr>
                <?php endif; ?>
            </tbody>
            <tfoot>
                <tr style="border-top:2px solid var(--deep);font-size:16px;">
                    <td colspan="3" style="text-align:right;font-weight:bold;">TỔNG CƯỚC ƯỚC TÍNH (USD):</td>
                    <td style="text-align:right;font-weight:bold;color:var(--deep);font-size:18px;">$<?= number_format($quoteResult['total_usd'], 2) ?></td>
                </tr>
                <tr style="font-size:14px;background:#f9f9f9;">
                    <td colspan="3" style="text-align:right;color:var(--gray);">Quy đổi VNĐ tương đương (Tỷ giá: 1 USD = 25.400 VND):</td>
                    <td style="text-align:right;font-weight:bold;color:var(--danger);"><?= number_format($quoteResult['total_vnd'], 0, ',', '.') ?> VND</td>
                </tr>
            </tfoot>
        </table>
        <p class="muted" style="margin-top:12px;font-size:12px;">
            * Lưu ý: Giá cước trên là giá ước tính chưa bao gồm thuế GTGT và các khoản phí hải quan, lưu kho đặc thù (nếu phát sinh).
        </p>
    </div>
<?php endif; ?>
<?php
render_footer();
