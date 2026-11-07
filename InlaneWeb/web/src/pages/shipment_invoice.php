<?php
/**
 * shipment_invoice.php — Hoá đơn cước vận tải (Freight Invoice).
 */
$u = require_login();

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

$isStaffOrAdmin = in_array($u['role'], ['admin', 'staff'], true);
$isOwner = ((int)$sh['customer_id'] === (int)$u['id']);
if (!$isOwner && !$isStaffOrAdmin) {
    http_response_code(403);
    render_header('403 — Từ chối');
    echo '<div class="card"><h1>403 — Không có quyền truy cập</h1></div>';
    render_footer();
    exit;
}

$details = db_select_one("SELECT * FROM shipment_details WHERE shipment_id = ?", "i", [$id]) ?? [];

$originPort    = $details['origin_port'] ?? 'US LAX';
$destPort      = $sh['port_code'];
$containerType = $details['container_type'] ?? '20GP';
$containerQty  = max(1, (int)($details['container_qty'] ?? 1));
$weightKg      = (float)($details['weight_kg'] ?? 10000);

// Tra cứu giá cơ sở trong freight_rates
$rateRow = db_select_one(
    "SELECT base_price_usd FROM freight_rates WHERE origin_port = ? AND dest_port = ? AND container_type = ?",
    "sss",
    [$originPort, $destPort, $containerType]
);

$baseRate = 0.0;
if ($rateRow) {
    $baseRate = (float)$rateRow['base_price_usd'];
} else {
    // Giá mặc định theo loại container nếu tuyến chưa có trong bảng giá
    $baseRate = match ($containerType) {
        '40HC'  => 2400.00,
        '40GP'  => 2000.00,
        default => 1200.00,
    };
}

$freightTotal = $baseRate * $containerQty;
$thcTotal = 150.00 * $containerQty;
$docFee = 50.00;
$overweightFee = ($weightKg > 15000) ? 250.00 : 0.00;

$totalUsd = $freightTotal + $thcTotal + $docFee + $overweightFee;
$exchangeRate = 25400;
$totalVnd = $totalUsd * $exchangeRate;

render_header('Hoá đơn cước #' . htmlspecialchars($sh['tracking_no']));
?>
<div class="no-print" style="margin-bottom:16px;display:flex;justify-content:space-between;align-items:center;">
    <a href="/shipments/<?= htmlspecialchars((string)$id, ENT_QUOTES, 'UTF-8') ?>/info" class="btn btn-sm" style="background:#5B6B7B;">← Quay lại chi tiết vận đơn</a>
    <button onclick="window.print()" class="btn">🖨️ In hoá đơn cước (Print Invoice)</button>
</div>

<div class="card" style="border:2px solid #142033;padding:32px;background:#fff;max-width:900px;margin:0 auto;">
    <div style="display:flex;justify-content:space-between;border-bottom:2px solid #142033;padding-bottom:16px;">
        <div>
            <div style="font-size:24px;font-weight:900;color:#065A82;letter-spacing:1px;">ILFREIGHT LOGISTICS CORP.</div>
            <div style="font-size:12px;color:#555;">FREIGHT DEBIT NOTE / HOÁ ĐƠN CƯỚC VẬN TẢI</div>
            <div style="font-size:11px;color:#777;margin-top:4px;">Tax Code: 0201889988 · Swift Code: ILFVNVX</div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:12px;font-weight:bold;color:#777;">INVOICE NO:</div>
            <div style="font-size:20px;font-weight:bold;color:#142033;font-family:Consolas,monospace;">INV-<?= htmlspecialchars($sh['tracking_no']) ?></div>
            <div style="font-size:11px;color:#555;margin-top:4px;">Ngày lập: <?= date('Y-m-d') ?></div>
            <div style="font-size:11px;color:#555;">Mã vận đơn: <strong><?= htmlspecialchars($sh['tracking_no']) ?></strong></div>
        </div>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;border-bottom:1px solid #142033;margin-top:16px;padding-bottom:16px;gap:16px;">
        <div>
            <div style="font-size:11px;font-weight:bold;color:#777;">ĐƠN VỊ THANH TOÁN (BILLED TO):</div>
            <div style="font-weight:bold;font-size:14px;margin-top:4px;"><?= htmlspecialchars($details['shipper_name'] ?? $u['username']) ?></div>
            <div style="font-size:13px;color:#333;margin-top:2px;"><?= nl2br(htmlspecialchars($details['shipper_address'] ?? '')) ?></div>
        </div>
        <div>
            <div style="font-size:11px;font-weight:bold;color:#777;">CHI TIẾT TUYẾN HÀNH TRÌNH:</div>
            <div style="font-size:13px;color:#333;margin-top:4px;">
                Tuyến: <strong><?= htmlspecialchars($originPort) ?></strong> → <strong><?= htmlspecialchars($destPort) ?></strong><br>
                Hàng hoá: <?= htmlspecialchars($details['cargo_desc'] ?? 'Hàng xuất khẩu') ?><br>
                Quy cách: <?= $containerQty ?> x <?= htmlspecialchars($containerType) ?> (<?= number_format($weightKg, 0, ',', '.') ?> kg)
            </div>
        </div>
    </div>

    <table class="data" style="margin-top:16px;border:1px solid #333;">
        <thead>
            <tr>
                <th style="background:#142033;color:#fff;">Hạng mục cước &amp; phụ phí (Description)</th>
                <th style="background:#142033;color:#fff;text-align:center;width:12%;">Số lượng</th>
                <th style="background:#142033;color:#fff;text-align:right;width:18%;">Đơn giá (USD)</th>
                <th style="background:#142033;color:#fff;text-align:right;width:20%;">Thành tiền (USD)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>
                    <strong>Cước vận chuyển đường biển quốc tế (Ocean Freight)</strong><br>
                    <span class="muted" style="font-size:12px;">Tuyến: <?= htmlspecialchars($originPort) ?> đến <?= htmlspecialchars($destPort) ?> (Loại <?= htmlspecialchars($containerType) ?>)</span>
                </td>
                <td style="text-align:center;"><?= $containerQty ?></td>
                <td style="text-align:right;">$<?= number_format($baseRate, 2) ?></td>
                <td style="text-align:right;font-weight:bold;">$<?= number_format($freightTotal, 2) ?></td>
            </tr>
            <tr>
                <td>
                    <strong>Phụ phí xếp dỡ tại cảng (Terminal Handling Charge - THC)</strong>
                </td>
                <td style="text-align:center;"><?= $containerQty ?></td>
                <td style="text-align:right;">$150.00</td>
                <td style="text-align:right;font-weight:bold;">$<?= number_format($thcTotal, 2) ?></td>
            </tr>
            <tr>
                <td>
                    <strong>Phí phát hành chứng từ &amp; vận đơn (Documentation Fee - B/L Fee)</strong>
                </td>
                <td style="text-align:center;">1</td>
                <td style="text-align:right;">$50.00</td>
                <td style="text-align:right;font-weight:bold;">$50.00</td>
            </tr>
            <?php if ($overweightFee > 0): ?>
                <tr>
                    <td>
                        <strong>Phụ phí hàng nặng (Overweight Surcharge - OW)</strong><br>
                        <span class="muted" style="font-size:12px;">Áp dụng cho lô hàng trọng lượng vượt ngưỡng 15,000 kg</span>
                    </td>
                    <td style="text-align:center;">1</td>
                    <td style="text-align:right;">$250.00</td>
                    <td style="text-align:right;font-weight:bold;">$250.00</td>
                </tr>
            <?php endif; ?>
        </tbody>
        <tfoot>
            <tr style="border-top:2px solid #142033;font-size:15px;">
                <td colspan="3" style="text-align:right;font-weight:bold;">TỔNG CỘNG THANH TOÁN (TOTAL USD):</td>
                <td style="text-align:right;font-weight:bold;color:#065A82;font-size:17px;">$<?= number_format($totalUsd, 2) ?></td>
            </tr>
            <tr style="font-size:14px;background:#f9f9f9;">
                <td colspan="3" style="text-align:right;color:#555;">Quy đổi ước tính (Tỷ giá: 1 USD = <?= number_format($exchangeRate) ?> VND):</td>
                <td style="text-align:right;font-weight:bold;color:#E5484D;"><?= number_format($totalVnd, 0, ',', '.') ?> VND</td>
            </tr>
        </tfoot>
    </table>

    <div style="margin-top:24px;display:grid;grid-template-columns:1.5fr 1fr;gap:20px;font-size:12px;">
        <div style="border:1px solid #ddd;padding:12px;border-radius:6px;">
            <div style="font-weight:bold;margin-bottom:4px;">THÔNG TIN TÀI KHOẢN THANH TOÁN (PAYMENT INFO):</div>
            <div>Ngân hàng: Vietcombank - Chi nhánh Hải Phòng</div>
            <div>Số tài khoản: <strong>0021 000 889988</strong> (VND) / <strong>0021 037 889988</strong> (USD)</div>
            <div>Tên chủ tài khoản: CONG TY CO PHAN LOGISTICS ILFREIGHT</div>
            <div>Nội dung chuyển khoản: <code>INV-<?= htmlspecialchars($sh['tracking_no']) ?></code></div>
        </div>
        <div style="text-align:center;">
            <div style="font-weight:bold;margin-bottom:50px;">BỘ PHẬN KẾ TOÁN (ACCOUNTING DEPT)</div>
            <div style="border-top:1px solid #333;width:80%;margin:0 auto;padding-top:6px;font-style:italic;color:#555;">
                ĐÃ XÁC NHẬN / PAID &amp; VERIFIED
            </div>
        </div>
    </div>
</div>
<?php
render_footer();
