<?php
/**
 * reset_password.php — Đặt lại mật khẩu bằng token.
 */
$token = trim($_GET['token'] ?? $_POST['token'] ?? '');
$token_hash = hash('sha256', $token);
$error = null;
$success = null;

// Kiểm tra token
$resetRecord = null;
if (!empty($token)) {
    $resetRecord = db_select_one(
        "SELECT * FROM password_resets WHERE token_hash = ? AND used_at IS NULL AND expires_at > NOW()",
        "s",
        [$token_hash]
    );
}

if (!$resetRecord) {
    $error = 'Liên kết đặt lại mật khẩu không hợp lệ, đã được sử dụng hoặc đã hết hạn (quá 30 phút).';
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && $resetRecord) {
    csrf_verify();

    $new_password = $_POST['new_password'] ?? '';
    $new_password_confirm = $_POST['new_password_confirm'] ?? '';

    if (mb_strlen($new_password) < 8) {
        $error = 'Mật khẩu mới phải có tối thiểu 8 ký tự.';
    } elseif ($new_password !== $new_password_confirm) {
        $error = 'Mật khẩu nhập lại không khớp.';
    } else {
        $userId = (int)$resetRecord['user_id'];

        // LAB: mat khau luu dang ro de tuong thich login.php
        db_execute(
            "UPDATE users SET password = ? WHERE id = ?",
            "si",
            [$new_password, $userId]
        );

        // Đánh dấu token hiện tại đã dùng
        db_execute(
            "UPDATE password_resets SET used_at = NOW() WHERE id = ?",
            "i",
            [(int)$resetRecord['id']]
        );

        // Vô hiệu hoá tất cả các token khác của user đó
        db_execute(
            "UPDATE password_resets SET used_at = NOW() WHERE user_id = ? AND used_at IS NULL",
            "i",
            [$userId]
        );

        $_SESSION['flash_msg'] = 'Đặt lại mật khẩu thành công! Bạn có thể đăng nhập bằng mật khẩu mới.';
        $_SESSION['flash_type'] = 'success';
        header('Location: /login');
        exit;
    }
}

render_header('Đặt lại mật khẩu');
?>
<div class="card" style="max-width:480px;margin:0 auto;">
    <h1>Đặt lại mật khẩu mới</h1>
    <?php if ($error) flash($error, 'error'); ?>

    <?php if ($resetRecord): ?>
        <p class="muted">Vui lòng nhập mật khẩu mới cho tài khoản của bạn.</p>
        <form action="/reset-password" method="post">
            <?= csrf_field() ?>
            <input type="hidden" name="token" value="<?= htmlspecialchars($token) ?>">
            <div class="form-row">
                <label>Mật khẩu mới (tối thiểu 8 ký tự)</label>
                <input type="password" name="new_password" required autofocus placeholder="Nhập mật khẩu mới">
            </div>
            <div class="form-row">
                <label>Xác nhận lại mật khẩu mới</label>
                <input type="password" name="new_password_confirm" required placeholder="Nhập lại mật khẩu mới">
            </div>
            <button class="btn" type="submit" style="width:100%">Lưu mật khẩu mới</button>
        </form>
    <?php else: ?>
        <p><a href="/forgot-password" class="btn btn-sm">Yêu cầu liên kết mới</a></p>
    <?php endif; ?>

    <div style="margin-top:16px;text-align:center;font-size:13px;">
        <a href="/login">← Quay lại trang Đăng nhập</a>
    </div>
</div>
<?php
render_footer();
