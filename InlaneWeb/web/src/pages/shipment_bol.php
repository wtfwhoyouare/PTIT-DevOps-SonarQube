<?php
/**
 * shipment_bol.php — Vận đơn đường biển (Bill of Lading - B/L) có thể in ấn.
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

render_header('Vận đơn đường biển #' . htmlspecialchars($sh['tracking_no']));
?>
<div class="no-print" style="margin-bottom:16px;display:flex;justify-content:space-between;align-items:center;">
    <a href="/shipments/<?= htmlspecialchars((string)$id, ENT_QUOTES, 'UTF-8') ?>/info" class="btn btn-sm" style="background:#5B6B7B;">← Quay lại chi tiết vận đơn</a>
    <button onclick="window.print()" class="btn">🖨️ In chứng từ (Print B/L)</button>
</div>

<div class="card" style="border:2px solid #142033;padding:32px;background:#fff;max-width:900px;margin:0 auto;">
    <div style="display:flex;justify-content:space-between;border-bottom:2px solid #142033;padding-bottom:16px;">
        <div>
            <div style="font-size:24px;font-weight:900;color:#065A82;letter-spacing:1px;">ILFREIGHT LOGISTICS CORP.</div>
            <div style="font-size:12px;color:#555;">OCEAN BILL OF LADING / VẬN ĐƠN ĐƯỜNG BIỂN</div>
            <div style="font-size:11px;color:#777;margin-top:4px;">Trụ sở: Hai Phong Port Logistics Hub · Hotline: +84 (0) 225 3888 999</div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:12px;font-weight:bold;color:#777;">B/L NUMBER:</div>
            <div style="font-size:20px;font-weight:bold;color:#E5484D;font-family:Consolas,monospace;"><?= htmlspecialchars($sh['tracking_no']) ?></div>
            <div style="font-size:11px;color:#555;margin-top:4px;">Ngày phát hành: <?= htmlspecialchars($details['created_at'] ?? date('Y-m-d')) ?></div>
        </div>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;border-bottom:1px solid #142033;margin-top:16px;padding-bottom:16px;gap:16px;">
        <div style="border-right:1px solid #ddd;padding-right:16px;">
            <div style="font-size:11px;font-weight:bold;color:#777;">1. SHIPPER (NGƯỜI GỬI HÀNG):</div>
            <div style="font-weight:bold;font-size:14px;margin-top:4px;"><?= htmlspecialchars($details['shipper_name'] ?? '—') ?></div>
            <div style="font-size:13px;color:#333;margin-top:2px;"><?= nl2br(htmlspecialchars($details['shipper_address'] ?? '—')) ?></div>
        </div>
        <div>
            <div style="font-size:11px;font-weight:bold;color:#777;">2. CONSIGNEE (NGƯỜI NHẬN HÀNG):</div>
            <div style="font-weight:bold;font-size:14px;margin-top:4px;"><?= htmlspecialchars($details['consignee_name'] ?? '—') ?></div>
            <div style="font-size:13px;color:#333;margin-top:2px;"><?= nl2br(htmlspecialchars($details['consignee_address'] ?? '—')) ?></div>
        </div>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;border-bottom:1px solid #142033;padding:12px 0;font-size:12px;gap:8px;">
        <div>
            <div style="font-size:10px;color:#777;font-weight:bold;">TÀU / CHUYẾN (VESSEL/VOY):</div>
            <div style="font-weight:bold;font-size:13px;">ILF PACIFIC V.2405</div>
        </div>
        <div>
            <div style="font-size:10px;color:#777;font-weight:bold;">CẢNG XẾP HÀNG (PORT OF LOADING):</div>
            <div style="font-weight:bold;font-size:13px;"><?= htmlspecialchars($details['origin_port'] ?? '—') ?></div>
        </div>
        <div>
            <div style="font-size:10px;color:#777;font-weight:bold;">CẢNG DỠ HÀNG (PORT OF DISCHARGE):</div>
            <div style="font-weight:bold;font-size:13px;"><?= htmlspecialchars($sh['port_code']) ?></div>
        </div>
        <div>
            <div style="font-size:10px;color:#777;font-weight:bold;">NGÀY KHỞI HÀNH (ETD):</div>
            <div style="font-weight:bold;font-size:13px;"><?= htmlspecialchars($details['etd'] ?? '—') ?></div>
        </div>
    </div>

    <table class="data" style="margin-top:16px;border:1px solid #333;">
        <thead>
            <tr>
                <th style="background:#142033;color:#fff;width:25%;">Ký mã hiệu & Số Container</th>
                <th style="background:#142033;color:#fff;">Mô tả hàng hoá</th>
                <th style="background:#142033;color:#fff;width:15%;">Loại hàng</th>
                <th style="background:#142033;color:#fff;width:20%;text-align:right;">Tổng trọng lượng (Gross Weight)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>
                    <strong>ILFU-<?= htmlspecialchars(substr(md5($sh['tracking_no']), 0, 7), ENT_QUOTES, 'UTF-8') ?></strong><br>
                    <span class="muted"><?= htmlspecialchars((string)($details['container_qty'] ?? 1)) ?> x <?= htmlspecialchars($details['container_type'] ?? '20GP') ?></span>
                </td>
                <td>
                    <strong><?= htmlspecialchars($details['cargo_desc'] ?? 'Hàng bách hoá thông thường') ?></strong><br>
                    <span class="muted" style="font-size:12px;">Đóng gói tiêu chuẩn xuất khẩu đường biển quốc tế.</span>
                </td>
                <td><?= htmlspecialchars($details['cargo_type'] ?? 'Thường') ?></td>
                <td style="text-align:right;font-weight:bold;font-size:14px;">
                    <?= htmlspecialchars(!empty($details['weight_kg']) ? number_format((float)$details['weight_kg'], 2, ',', '.') . ' KG' : 'N/A', ENT_QUOTES, 'UTF-8') ?>
                </td>
            </tr>
        </tbody>
    </table>

    <div style="margin-top:30px;display:grid;grid-template-columns:1fr 1fr;gap:40px;font-size:12px;">
        <div style="border:1px dashed #aaa;padding:12px;border-radius:6px;">
            <div style="font-weight:bold;margin-bottom:4px;">GHI CHÚ VẬN TẢI (CARRIER TERMS):</div>
            <div style="color:#555;line-height:1.4;">
                Hàng hoá được tiếp nhận trong tình trạng bên ngoài nguyên vẹn và niêm phong kẹp chì.
                Người vận chuyển chịu trách nhiệm theo Quy tắc Hague-Visby và Bộ luật Hàng hải Quốc tế.
            </div>
        </div>
        <div style="text-align:center;padding-top:10px;">
            <div style="font-weight:bold;margin-bottom:50px;">ĐẠI DIỆN HÃNG VẬN TẢI (FOR THE CARRIER)</div>
            <div style="border-top:1px solid #333;width:80%;margin:0 auto;padding-top:6px;font-style:italic;color:#555;">
                ILFREIGHT LOGISTICS AUTHORIZED SIGNATURE &amp; STAMP
            </div>
        </div>
    </div>
</div>
<?php
render_footer();
