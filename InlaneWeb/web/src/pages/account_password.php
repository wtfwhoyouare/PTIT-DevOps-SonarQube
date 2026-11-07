<?php
/**
 * account_password.php — Đổi mật khẩu tài khoản đang đăng nhập.
 */
$u = require_login();
$error = null;
$success = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    csrf_verify();

    $current_password = $_POST['current_password'] ?? '';
    $new_password = $_POST['new_password'] ?? '';
    $new_password_confirm = $_POST['new_password_confirm'] ?? '';

    // Kiểm tra mật khẩu hiện tại
    $userDb = db_select_one("SELECT password FROM users WHERE id = ?", "i", [(int)$u['id']]);
    if (!$userDb || $userDb['password'] !== $current_password) {
        $error = 'Mật khẩu hiện tại không chính xác.';
    } elseif (mb_strlen($new_password) < 8) {
        $error = 'Mật khẩu mới phải có tối thiểu 8 ký tự.';
    } elseif ($new_password !== $new_password_confirm) {
        $error = 'Mật khẩu mới nhập lại không khớp.';
    } elseif ($new_password === $current_password) {
        $error = 'Mật khẩu mới không được trùng với mật khẩu hiện tại.';
    } else {
        // LAB: mat khau luu dang ro de tuong thich login.php
        db_execute(
            "UPDATE users SET password = ? WHERE id = ?",
            "si",
            [$new_password, (int)$u['id']]
        );

        $success = 'Đổi mật khẩu thành công! Mật khẩu mới đã có hiệu lực.';
    }
}

render_header('Đổi mật khẩu');
?>
<div class="card" style="max-width:480px;margin:0 auto;">
    <h1>Đổi mật khẩu</h1>
    <p class="muted">Tài khoản: <strong><?= htmlspecialchars($u['username']) ?></strong> (<?= htmlspecialchars($u['email']) ?>)</p>
    <?php
    if ($error) flash($error, 'error');
    if ($success) flash($success, 'success');
    ?>
    <form action="/account/password" method="post">
        <?= csrf_field() ?>
        <div class="form-row">
            <label>Mật khẩu hiện tại (*)</label>
            <input type="password" name="current_password" required autofocus placeholder="Nhập mật khẩu đang dùng">
        </div>
        <div class="form-row">
            <label>Mật khẩu mới (*, tối thiểu 8 ký tự)</label>
            <input type="password" name="new_password" required placeholder="Nhập mật khẩu mới">
        </div>
        <div class="form-row">
            <label>Nhập lại mật khẩu mới (*)</label>
            <input type="password" name="new_password_confirm" required placeholder="Xác nhận lại mật khẩu mới">
        </div>
        <button class="btn" type="submit" style="width:100%">Cập nhật mật khẩu</button>
    </form>
    <div style="margin-top:16px;text-align:center;font-size:13px;">
        <a href="/account">← Quay lại trang Hồ sơ</a>
    </div>
</div>
<?php
render_footer();
