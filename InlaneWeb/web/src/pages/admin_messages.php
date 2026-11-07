<?php
/**
 * admin_messages.php — Hộp thư liên hệ từ khách hàng (Staff & Admin).
 */
$u = require_role(['admin', 'staff']);
$error = null;
$success = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    csrf_verify();
    $action = $_POST['action'] ?? '';
    $msgId  = (int)($_POST['msg_id'] ?? 0);

    if ($action === 'toggle_handle') {
        $val = (int)($_POST['handled_val'] ?? 1);
        db_execute("UPDATE contact_messages SET is_handled = ? WHERE id = ?", "ii", [$val, $msgId]);
        $success = ($val === 1) ? 'Đã đánh dấu tin nhắn là đã xử lý!' : 'Đã chuyển tin nhắn sang trạng thái chờ xử lý.';
    }
}

$handledFilter = $_GET['handled'] ?? '';
$page          = max(1, (int)($_GET['page'] ?? 1));
$perPage       = 10;
$offset        = ($page - 1) * $perPage;

$whereClause = "";
$types = "";
$params = [];

if ($handledFilter === '0' || $handledFilter === '1') {
    $whereClause = "WHERE is_handled = ?";
    $types = "i";
    $params = [(int)$handledFilter];
}

$countSql = "SELECT COUNT(*) AS total FROM contact_messages {$whereClause}";
$totalRow = db_select_one($countSql, $types, $params);
$totalRecords = $totalRow ? (int)$totalRow['total'] : 0;
$totalPages = max(1, (int)ceil($totalRecords / $perPage));

$dataSql = "SELECT * FROM contact_messages {$whereClause} ORDER BY is_handled ASC, created_at DESC, id DESC LIMIT ? OFFSET ?";
$typesWithLimit = $types . "ii";
$paramsWithLimit = array_merge($params, [$perPage, $offset]);

$messages = db_select($dataSql, $typesWithLimit, $paramsWithLimit);

render_header('Hộp thư liên hệ');
?>
<div class="card">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
        <div>
            <h1>Hộp thư liên hệ (Contact Messages)</h1>
            <p class="muted">Tiếp nhận yêu cầu tư vấn, báo giá và phản hồi của khách hàng gửi từ form liên hệ.</p>
        </div>
        <div style="display:flex;gap:8px;">
            <a href="/admin/messages" class="btn btn-sm" style="<?= $handledFilter === '' ? 'background:var(--deep);' : 'background:#5B6B7B;' ?>">Tất cả</a>
            <a href="/admin/messages?handled=0" class="btn btn-sm" style="<?= $handledFilter === '0' ? 'background:var(--danger);' : 'background:#5B6B7B;' ?>">Chưa xử lý</a>
            <a href="/admin/messages?handled=1" class="btn btn-sm" style="<?= $handledFilter === '1' ? 'background:var(--ok);' : 'background:#5B6B7B;' ?>">Đã xử lý</a>
        </div>
    </div>

    <?php
    if ($error) flash($error, 'error');
    if ($success) flash($success, 'success');
    ?>

    <div class="table-responsive" style="margin-top:16px;">
        <table class="data">
            <thead>
                <tr>
                    <th style="width:6%;">ID</th>
                    <th style="width:20%;">Khách hàng</th>
                    <th style="width:18%;">Email / SĐT</th>
                    <th>Nội dung tin nhắn</th>
                    <th style="width:12%;">Trạng thái</th>
                    <th style="width:14%;">Thao tác</th>
                </tr>
            </thead>
            <tbody>
                <?php if (empty($messages)): ?>
                    <tr><td colspan="6" style="text-align:center;padding:24px;" class="muted">Không có tin nhắn nào.</td></tr>
                <?php else: ?>
                    <?php foreach ($messages as $m): ?>
                        <tr>
                            <td>#<?= htmlspecialchars((string)$m['id'], ENT_QUOTES, 'UTF-8') ?></td>
                            <td>
                                <strong><?= htmlspecialchars($m['full_name'], ENT_QUOTES, 'UTF-8') ?></strong><br>
                                <span class="muted" style="font-size:11px;"><?= htmlspecialchars($m['created_at'], ENT_QUOTES, 'UTF-8') ?></span>
                            </td>
                            <td>
                                <a href="mailto:<?= htmlspecialchars($m['email'], ENT_QUOTES, 'UTF-8') ?>"><?= htmlspecialchars($m['email'], ENT_QUOTES, 'UTF-8') ?></a><br>
                                <span class="muted"><?= htmlspecialchars($m['phone'] ?? '—', ENT_QUOTES, 'UTF-8') ?></span>
                            </td>
                            <td>
                                <div style="line-height:1.4;font-size:13px;">
                                    <?= nl2br(htmlspecialchars($m['message'], ENT_QUOTES, 'UTF-8')) ?>
                                </div>
                            </td>
                            <td>
                                <?php if (!empty($m['is_handled'])): ?>
                                    <span class="badge badge-delivered">ĐÃ XỬ LÝ</span>
                                <?php else: ?>
                                    <span class="badge badge-hold">CHƯA XỬ LÝ</span>
                                <?php endif; ?>
                            </td>
                            <td>
                                <form method="post" action="/admin/messages" style="display:inline;">
                                    <?= csrf_field() ?>
                                    <input type="hidden" name="action" value="toggle_handle">
                                    <input type="hidden" name="msg_id" value="<?= htmlspecialchars((string)$m['id'], ENT_QUOTES, 'UTF-8') ?>">
                                    <?php if (!empty($m['is_handled'])): ?>
                                        <input type="hidden" name="handled_val" value="0">
                                        <button type="submit" class="btn btn-sm" style="background:#5B6B7B;font-size:12px;padding:3px 8px;">Đánh dấu chưa xử lý</button>
                                    <?php else: ?>
                                        <input type="hidden" name="handled_val" value="1">
                                        <button type="submit" class="btn btn-sm" style="background:var(--ok);font-size:12px;padding:3px 8px;">Đánh dấu đã xử lý</button>
                                    <?php endif; ?>
                                </form>
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
            <span>Trang <?= htmlspecialchars((string)$page, ENT_QUOTES, 'UTF-8') ?> / <?= htmlspecialchars((string)$totalPages, ENT_QUOTES, 'UTF-8') ?></span>
            <?php for ($i = 1; $i <= $totalPages; $i++): ?>
                <?php $url = '/admin/messages?page=' . $i . ($handledFilter !== '' ? '&handled=' . urlencode($handledFilter) : ''); ?>
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
