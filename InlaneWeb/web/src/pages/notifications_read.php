<?php
/**
 * notifications_read.php — Đánh dấu tất cả thông báo của người dùng là đã đọc.
 */
$u = require_login();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: /notifications');
    exit;
}

csrf_verify();

db_execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?", "i", [(int)$u['id']]);

header('Location: /notifications');
exit;
