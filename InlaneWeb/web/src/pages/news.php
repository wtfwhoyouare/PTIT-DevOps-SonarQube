<?php
/**
 * news.php — Tin tuc. Xem chi tiet 1 tin qua ?id=
 *
 * !!! DIEM INJECT (phu): UNION/Error qua ?id= !!!
 * Payload mau:  /news?id=1 UNION SELECT 1,username,password FROM users-- -
 */
render_header('Tin tức');

$id = $_GET['id'] ?? '';
?>
<div class="card">
    <h1>Tin tức &amp; Thông báo</h1>
    <?php
    if ($id !== '') {
        // !!! NOI CHUOI id (kieu so, khong bao quote) -> UNION-based (3 cot) !!!
        $sql = "SELECT id, title, body FROM news WHERE id = $id";
        echo '<div class="query-box">' . htmlspecialchars($sql) . '</div>';
        $res = query($sql);
        if ($res) {
            while ($row = mysqli_fetch_row($res)) {
                echo '<h2>' . htmlspecialchars((string)$row[1], ENT_QUOTES, 'UTF-8') . '</h2>';
                echo '<div class="news-article-body">' . nl2br(htmlspecialchars((string)$row[2], ENT_QUOTES, 'UTF-8')) . '</div>';
            }
        }
        echo '<p class="muted" style="margin-top:20px;"><a href="/news">← Tất cả tin tức</a></p>';
    } else {
        $page = max(1, (int)($_GET['page'] ?? 1));
        $limit = 10;
        $offset = ($page - 1) * $limit;

        $countRow = db_select_one("SELECT COUNT(*) AS c FROM news");
        $total = $countRow ? (int)$countRow['c'] : 0;
        $totalPages = max(1, (int)ceil($total / $limit));

        $rows = db_select(
            "SELECT id, title, body, published_at FROM news ORDER BY published_at DESC, id DESC LIMIT ? OFFSET ?",
            'ii',
            [$limit, $offset]
        );
        ?>
        <p class="muted" style="margin-bottom:16px;">
            Cập nhật tin tức ngành hàng hải, hạ tầng cảng biển, giá cước container và thông báo vận hành mới nhất từ IlFreight Logistics
            (Tổng số: <strong><?= htmlspecialchars((string)$total, ENT_QUOTES, 'UTF-8') ?></strong> bản tin).
        </p>

        <?php if (empty($rows)): ?>
            <p class="muted">Hiện chưa có bản tin nào.</p>
        <?php else: ?>
            <div class="news-list-stack">
                <?php foreach ($rows as $row):
                    $rowId = (int)$row['id'];
                    $bodyText = trim((string)($row['body'] ?? ''));
                    $excerpt = mb_substr($bodyText, 0, 200);
                    if (mb_strlen($bodyText) > 200) {
                        $excerpt .= '...';
                    }
                    ?>
                    <article class="news-list-item">
                        <div class="news-list-meta">
                            <?= htmlspecialchars((string)$row['published_at'], ENT_QUOTES, 'UTF-8') ?>
                            · Bản tin #<?= htmlspecialchars((string)$rowId, ENT_QUOTES, 'UTF-8') ?>
                        </div>
                        <h3>
                            <a href="/news?id=<?= htmlspecialchars((string)$rowId, ENT_QUOTES, 'UTF-8') ?>">
                                <?= htmlspecialchars((string)$row['title'], ENT_QUOTES, 'UTF-8') ?>
                            </a>
                        </h3>
                        <p class="muted"><?= htmlspecialchars($excerpt, ENT_QUOTES, 'UTF-8') ?></p>
                        <a class="btn btn-sm" href="/news?id=<?= htmlspecialchars((string)$rowId, ENT_QUOTES, 'UTF-8') ?>">Đọc chi tiết →</a>
                    </article>
                <?php endforeach; ?>
            </div>

            <?php if ($totalPages > 1):
                $prevPage = htmlspecialchars((string)($page - 1), ENT_QUOTES, 'UTF-8');
                $nextPage = htmlspecialchars((string)($page + 1), ENT_QUOTES, 'UTF-8');
                ?>
                <div class="pagination" style="margin-top:20px;display:flex;gap:8px;align-items:center;">
                    <?php if ($page > 1): ?>
                        <a class="btn btn-sm" href="/news?page=<?= $prevPage ?>">« Trước</a>
                    <?php endif; ?>
                    <span>Trang <?= htmlspecialchars((string)$page, ENT_QUOTES, 'UTF-8') ?> / <?= htmlspecialchars((string)$totalPages, ENT_QUOTES, 'UTF-8') ?></span>
                    <?php if ($page < $totalPages): ?>
                        <a class="btn btn-sm" href="/news?page=<?= $nextPage ?>">Sau »</a>
                    <?php endif; ?>
                </div>
            <?php endif; ?>
        <?php endif; ?>
        <?php
    }
    ?>
</div>
<?php
render_footer();
