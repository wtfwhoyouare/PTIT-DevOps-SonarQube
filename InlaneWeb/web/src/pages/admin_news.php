<?php
/**
 * admin_news.php — Quản lý tin tức (Staff & Admin).
 */
$u = require_role(['admin', 'staff']);
$error = null;
$success = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    csrf_verify();
    $action = $_POST['action'] ?? '';

    if ($action === 'create') {
        $title = trim($_POST['title'] ?? '');
        $body  = trim($_POST['body'] ?? '');

        if (empty($title) || empty($body)) {
            $error = 'Vui lòng nhập đầy đủ tiêu đề và nội dung bài viết.';
        } else {
            db_insert("INSERT INTO news (title, body, published_at) VALUES (?, ?, NOW())", "ss", [$title, $body]);
            $success = 'Đăng bài viết mới thành công!';
        }
    } elseif ($action === 'edit') {
        $newsId = (int)($_POST['news_id'] ?? 0);
        $title  = trim($_POST['title'] ?? '');
        $body   = trim($_POST['body'] ?? '');

        if (empty($title) || empty($body)) {
            $error = 'Tiêu đề và nội dung không được để trống.';
        } else {
            db_execute("UPDATE news SET title = ?, body = ? WHERE id = ?", "ssi", [$title, $body, $newsId]);
            $success = 'Cập nhật tin tức thành công!';
        }
    } elseif ($action === 'delete') {
        $newsId = (int)($_POST['news_id'] ?? 0);
        db_execute("DELETE FROM news WHERE id = ?", "i", [$newsId]);
        $success = 'Đã xoá bài viết!';
    }
}

$page       = max(1, (int)($_GET['page'] ?? 1));
$perPage    = 10;
$offset     = ($page - 1) * $perPage;
$totalRow   = db_select_one("SELECT COUNT(*) AS total FROM news");
$totalRecords = $totalRow ? (int)$totalRow['total'] : 0;
$totalPages = max(1, (int)ceil($totalRecords / $perPage));

$newsList = db_select("SELECT * FROM news ORDER BY published_at DESC, id DESC LIMIT ? OFFSET ?", "ii", [$perPage, $offset]);

render_header('Quản lý tin tức');
?>
<div class="card">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
        <div>
            <h1>Quản lý tin tức &amp; Bản tin hàng hải</h1>
            <p class="muted">Soạn thảo và phát hành thông báo, tin tức logistics cho khách hàng.</p>
        </div>
        <button onclick="document.getElementById('createNewsModal').style.display='block'" class="btn">+ Viết bài mới</button>
    </div>

    <?php
    if ($error) flash($error, 'error');
    if ($success) flash($success, 'success');
    ?>

    <div style="margin-top:20px;">
        <?php if (empty($newsList)): ?>
            <p class="muted">Chưa có bài viết tin tức nào.</p>
        <?php else: ?>
            <?php foreach ($newsList as $n): ?>
                <div style="border:1px solid var(--line);border-radius:8px;padding:16px;margin-bottom:14px;background:#fff;">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;">
                        <div>
                            <h3 style="margin:0 0 6px 0;font-size:17px;color:var(--deep);"><?= htmlspecialchars($n['title'], ENT_QUOTES, 'UTF-8') ?></h3>
                            <div class="muted" style="font-size:12px;margin-bottom:10px;">Ngày xuất bản: <?= htmlspecialchars($n['published_at'], ENT_QUOTES, 'UTF-8') ?></div>
                        </div>
                        <div style="display:flex;gap:6px;">
                            <details style="display:inline-block;">
                                <summary class="btn btn-sm" style="padding:3px 8px;font-size:12px;background:var(--teal);cursor:pointer;list-style:none;">Sửa</summary>
                                <div style="position:absolute;z-index:100;right:40px;background:#fff;border:2px solid var(--line);box-shadow:0 4px 12px rgba(0,0,0,0.15);padding:16px;border-radius:8px;min-width:400px;margin-top:4px;">
                                    <h4 style="margin:0 0 10px 0;">Sửa tin tức #<?= htmlspecialchars((string)$n['id'], ENT_QUOTES, 'UTF-8') ?></h4>
                                    <form method="post" action="/admin/news">
                                        <?= csrf_field() ?>
                                        <input type="hidden" name="action" value="edit">
                                        <input type="hidden" name="news_id" value="<?= htmlspecialchars((string)$n['id'], ENT_QUOTES, 'UTF-8') ?>">
                                        <div class="form-row">
                                            <label>Tiêu đề</label>
                                            <input type="text" name="title" value="<?= htmlspecialchars($n['title'], ENT_QUOTES, 'UTF-8') ?>" required>
                                        </div>
                                        <div class="form-row">
                                            <label>Nội dung</label>
                                            <textarea name="body" rows="6" required><?= htmlspecialchars($n['body'], ENT_QUOTES, 'UTF-8') ?></textarea>
                                        </div>
                                        <button type="submit" class="btn btn-sm">Lưu</button>
                                    </form>
                                </div>
                            </details>

                            <form method="post" action="/admin/news" style="display:inline;" onsubmit="return confirm('Bạn có chắc muốn xoá bài viết này?');">
                                <?= csrf_field() ?>
                                <input type="hidden" name="action" value="delete">
                                <input type="hidden" name="news_id" value="<?= htmlspecialchars((string)$n['id'], ENT_QUOTES, 'UTF-8') ?>">
                                <button type="submit" class="btn btn-sm btn-danger" style="padding:3px 8px;font-size:12px;">Xoá</button>
                            </form>
                        </div>
                    </div>
                    <div style="font-size:14px;color:var(--ink);line-height:1.5;">
                        <?= nl2br(htmlspecialchars($n['body'], ENT_QUOTES, 'UTF-8')) ?>
                    </div>
                </div>
            <?php endforeach; ?>
        <?php endif; ?>
    </div>

    <?php if ($totalPages > 1): ?>
        <div class="pagination">
            <span>Trang <?= htmlspecialchars((string)$page, ENT_QUOTES, 'UTF-8') ?> / <?= htmlspecialchars((string)$totalPages, ENT_QUOTES, 'UTF-8') ?> (Tổng <?= htmlspecialchars((string)$totalRecords, ENT_QUOTES, 'UTF-8') ?> bài viết)</span>
            <?php for ($i = 1; $i <= $totalPages; $i++): ?>
                <?php if ($i === $page): ?>
                    <span class="active"><?= htmlspecialchars((string)$i, ENT_QUOTES, 'UTF-8') ?></span>
                <?php else: ?>
                    <a href="/admin/news?page=<?= htmlspecialchars((string)$i, ENT_QUOTES, 'UTF-8') ?>"><?= htmlspecialchars((string)$i, ENT_QUOTES, 'UTF-8') ?></a>
                <?php endif; ?>
            <?php endfor; ?>
        </div>
    <?php endif; ?>
</div>

<!-- Modal thêm tin tức -->
<div id="createNewsModal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:999;overflow-y:auto;">
    <div style="background:#fff;max-width:560px;margin:50px auto;padding:24px;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,0.2);">
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--line);padding-bottom:12px;margin-bottom:16px;">
            <h2 style="margin:0;">Đăng tin tức mới</h2>
            <button onclick="document.getElementById('createNewsModal').style.display='none'" style="border:none;background:none;font-size:20px;cursor:pointer;">&times;</button>
        </div>
        <form method="post" action="/admin/news">
            <?= csrf_field() ?>
            <input type="hidden" name="action" value="create">
            <div class="form-row">
                <label>Tiêu đề bài viết (*)</label>
                <input type="text" name="title" required placeholder="Nhập tiêu đề...">
            </div>
            <div class="form-row">
                <label>Nội dung chi tiết (*)</label>
                <textarea name="body" rows="6" required placeholder="Nhập nội dung bài viết..."></textarea>
            </div>
            <div style="display:flex;gap:10px;margin-top:20px;">
                <button type="submit" class="btn">Đăng bài</button>
                <button type="button" onclick="document.getElementById('createNewsModal').style.display='none'" class="btn" style="background:#5B6B7B;">Đóng</button>
            </div>
        </form>
    </div>
</div>
<?php
render_footer();
