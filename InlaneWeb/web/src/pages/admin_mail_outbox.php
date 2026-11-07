<?php
/**
 * admin_mail_outbox.php — Hộp thư giả lập (Mock Mail Outbox) cho Staff/Admin.
 */
$u = require_role(['admin', 'staff']);

$searchQuery = trim($_GET['q'] ?? '');
$page        = max(1, (int)($_GET['page'] ?? 1));
$perPage     = 10;
$offset      = ($page - 1) * $perPage;

$whereClause = "";
$types = "";
$params = [];

if ($searchQuery !== '') {
    $whereClause = "WHERE to_email LIKE ? OR subject LIKE ? OR body LIKE ?";
    $types = "sss";
    $wild = '%' . $searchQuery . '%';
    $params = [$wild, $wild, $wild];
}

$countSql = "SELECT COUNT(*) AS total FROM mail_outbox {$whereClause}";
$totalRow = db_select_one($countSql, $types, $params);
$totalRecords = $totalRow ? (int)$totalRow['total'] : 0;
$totalPages = max(1, (int)ceil($totalRecords / $perPage));

$dataSql = "SELECT * FROM mail_outbox {$whereClause} ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?";
$typesWithLimit = $types . "ii";
$paramsWithLimit = array_merge($params, [$perPage, $offset]);

$emails = db_select($dataSql, $typesWithLimit, $paramsWithLimit);

render_header('Hộp thư giả lập (Mail Outbox)');
?>
<div class="card">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
        <div>
            <h1>Hộp thư giả lập (Simulated Mail Outbox)</h1>
            <p class="muted">Hệ thống không sử dụng SMTP bên ngoài; mọi thông báo chào mừng, token đổi mật khẩu và cập nhật đơn hàng đều được lưu tại đây.</p>
        </div>
    </div>

    <!-- Tìm kiếm -->
    <form method="get" action="/admin/mail-outbox" style="display:flex;gap:10px;margin:16px 0;">
        <input type="text" name="q" value="<?= htmlspecialchars($searchQuery, ENT_QUOTES, 'UTF-8') ?>" placeholder="Tìm email người nhận, tiêu đề, nội dung..." style="flex:1;padding:8px 12px;border:1px solid var(--line);border-radius:6px;">
        <button type="submit" class="btn btn-sm">Tìm kiếm</button>
        <?php if ($searchQuery !== ''): ?>
            <a href="/admin/mail-outbox" class="btn btn-sm" style="background:#5B6B7B;">Xoá tìm</a>
        <?php endif; ?>
    </form>

    <div class="table-responsive">
        <table class="data">
            <thead>
                <tr>
                    <th style="width:8%;">ID</th>
                    <th style="width:20%;">Người nhận (To)</th>
                    <th style="width:25%;">Tiêu đề (Subject)</th>
                    <th>Nội dung (Preview)</th>
                    <th style="width:16%;">Thời gian gửi</th>
                </tr>
            </thead>
            <tbody>
                <?php if (empty($emails)): ?>
                    <tr><td colspan="5" style="text-align:center;padding:24px;" class="muted">Hộp thư ra hiện đang trống.</td></tr>
                <?php else: ?>
                    <?php foreach ($emails as $em): ?>
                        <tr>
                            <td>#<?= htmlspecialchars((string)$em['id'], ENT_QUOTES, 'UTF-8') ?></td>
                            <td><strong><?= htmlspecialchars($em['to_email'], ENT_QUOTES, 'UTF-8') ?></strong></td>
                            <td><?= htmlspecialchars($em['subject'], ENT_QUOTES, 'UTF-8') ?></td>
                            <td>
                                <details>
                                    <summary style="cursor:pointer;color:var(--deep);font-size:13px;">
                                        <?= htmlspecialchars(mb_substr($em['body'], 0, 70), ENT_QUOTES, 'UTF-8') ?>... (Xem toàn bộ)
                                    </summary>
                                    <div style="background:#f4f7fb;border:1px solid var(--line);border-radius:6px;padding:12px;margin-top:6px;font-family:Consolas,monospace;font-size:12px;white-space:pre-wrap;">
                                        <?= htmlspecialchars($em['body'], ENT_QUOTES, 'UTF-8') ?>
                                    </div>
                                </details>
                            </td>
                            <td><?= htmlspecialchars($em['created_at'], ENT_QUOTES, 'UTF-8') ?></td>
                        </tr>
                    <?php endforeach; ?>
                <?php endif; ?>
            </tbody>
        </table>
    </div>

    <!-- Phân trang -->
    <?php if ($totalPages > 1): ?>
        <div class="pagination">
            <span>Trang <?= htmlspecialchars((string)$page, ENT_QUOTES, 'UTF-8') ?> / <?= htmlspecialchars((string)$totalPages, ENT_QUOTES, 'UTF-8') ?> (Tổng <?= htmlspecialchars((string)$totalRecords, ENT_QUOTES, 'UTF-8') ?> email)</span>
            <?php for ($i = 1; $i <= $totalPages; $i++): ?>
                <?php $url = '/admin/mail-outbox?page=' . $i . ($searchQuery !== '' ? '&q=' . urlencode($searchQuery) : ''); ?>
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
