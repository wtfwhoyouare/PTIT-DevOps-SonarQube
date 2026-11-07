<?php
/**
 * notifications.php — Danh sách thông báo của người dùng.
 */
$u = require_login();

$page = max(1, (int)($_GET['page'] ?? 1));
$perPage = 10;
$offset = ($page - 1) * $perPage;

$userId = (int)$u['id'];

$totalRow = db_select_one("SELECT COUNT(*) AS total FROM notifications WHERE user_id = ?", "i", [$userId]);
$totalRecords = $totalRow ? (int)$totalRow['total'] : 0;
$totalPages = max(1, (int)ceil($totalRecords / $perPage));

$notifications = db_select(
    "SELECT n.*, s.tracking_no
     FROM notifications n
     LEFT JOIN shipments s ON s.id = n.shipment_id
     WHERE n.user_id = ?
     ORDER BY n.created_at DESC, n.id DESC
     LIMIT ? OFFSET ?",
    "iii",
    [$userId, $perPage, $offset]
);

$unreadRow = db_select_one("SELECT COUNT(*) AS cnt FROM notifications WHERE user_id = ? AND is_read = 0", "i", [$userId]);
$unreadCount = $unreadRow ? (int)$unreadRow['cnt'] : 0;

render_header('Thông báo của tôi');
?>
<div class="card">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
        <div>
            <h1>Thông báo hệ thống</h1>
            <p class="muted">
                Bạn có <strong><?= $unreadCount ?></strong> thông báo chưa đọc trong tổng số <?= $totalRecords ?> thông báo.
            </p>
        </div>
        <?php if ($unreadCount > 0): ?>
            <div>
                <form action="/notifications/read" method="post" style="margin:0;">
                    <?= csrf_field() ?>
                    <button type="submit" class="btn btn-sm">Đánh dấu tất cả đã đọc</button>
                </form>
            </div>
        <?php endif; ?>
    </div>

    <?php if (empty($notifications)): ?>
        <p class="muted" style="padding:24px;text-align:center;background:var(--panelalt);border-radius:8px;">
            Bạn chưa có thông báo nào.
        </p>
    <?php else: ?>
        <div style="margin-top:16px;">
            <?php foreach ($notifications as $n): ?>
                <div style="padding:14px 16px;border-radius:8px;margin-bottom:10px;border-left:4px solid <?= $n['is_read'] ? 'var(--line)' : 'var(--deep)' ?>;background:<?= $n['is_read'] ? 'var(--panel)' : 'var(--panelalt)' ?>;border:1px solid var(--line);border-left-width:4px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-size:12px;color:var(--gray);font-weight:600;">
                            <?= htmlspecialchars($n['created_at']) ?>
                            <?php if (!$n['is_read']): ?>
                                <span class="badge" style="background:var(--accent);color:#fff;margin-left:6px;font-size:10px;">MỚI</span>
                            <?php endif; ?>
                        </span>
                        <?php if (!empty($n['shipment_id'])): ?>
                            <a href="/shipments/<?= htmlspecialchars((string)$n['shipment_id'], ENT_QUOTES, 'UTF-8') ?>/info" class="btn btn-sm" style="padding:2px 8px;font-size:11px;">Xem đơn</a>
                        <?php endif; ?>
                    </div>
                    <div style="margin-top:6px;font-size:14px;color:var(--ink);">
                        <?= htmlspecialchars($n['message']) ?>
                    </div>
                </div>
            <?php endforeach; ?>
        </div>

        <?php if ($totalPages > 1): ?>
            <div class="pagination">
                <span>Trang <?= htmlspecialchars((string)$page, ENT_QUOTES, 'UTF-8') ?> / <?= htmlspecialchars((string)$totalPages, ENT_QUOTES, 'UTF-8') ?></span>
                <?php for ($i = 1; $i <= $totalPages; $i++): ?>
                    <?php if ($i === $page): ?>
                        <span class="active"><?= htmlspecialchars((string)$i, ENT_QUOTES, 'UTF-8') ?></span>
                    <?php else: ?>
                        <a href="/notifications?page=<?= htmlspecialchars((string)$i, ENT_QUOTES, 'UTF-8') ?>"><?= htmlspecialchars((string)$i, ENT_QUOTES, 'UTF-8') ?></a>
                    <?php endif; ?>
                <?php endfor; ?>
            </div>
        <?php endif; ?>
    <?php endif; ?>
</div>
<?php
render_footer();
