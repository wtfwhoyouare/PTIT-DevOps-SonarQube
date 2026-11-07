<?php
/**
 * forgot_password.php — Quên mật khẩu.
 */
$info = null;
$email = trim($_POST['email'] ?? '');

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    csrf_verify();

    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        flash('Vui lòng nhập địa chỉ email hợp lệ.', 'error');
    } else {
        // Luôn hiển thị cùng thông báo dù email có tồn tại hay không
        $info = 'Nếu email của bạn tồn tại trên hệ thống, chúng tôi đã gửi liên kết đặt lại mật khẩu vào hòm thư. Vui lòng kiểm tra hộp thư đến và làm theo hướng dẫn.';

        $user = db_select_one("SELECT id, username FROM users WHERE email = ?", "s", [$email]);
        if ($user) {
            $token = bin2hex(random_bytes(32));
            $token_hash = hash('sha256', $token);

            // Lưu token hash vào password_resets, hạn 30 phút
            db_execute(
                "INSERT INTO password_resets (user_id, token_hash, expires_at) VALUES (?, ?, DATE_ADD(NOW(), INTERVAL 30 MINUTE))",
                "is",
                [(int)$user['id'], $token_hash]
            );

            // Ghi email vào mail_outbox
            $resetUrl = 'http://127.0.0.1:8088/reset-password?token=' . urlencode($token);
            $subject = 'Khôi phục mật khẩu tài khoản IlFreight Logistics';
            $body = "Xin chào {$user['username']},\n\n"
                . "Hệ thống nhận được yêu cầu đặt lại mật khẩu cho tài khoản của bạn.\n"
                . "Vui lòng truy cập liên kết bên dưới để tạo mật khẩu mới (liên kết có giá trị trong 30 phút và chỉ sử dụng được 1 lần):\n\n"
                . $resetUrl . "\n\n"
                . "Nếu bạn không thực hiện yêu cầu này, vui lòng bỏ qua email và đảm bảo mật khẩu hiện tại của bạn vẫn an toàn.\n\n"
                . "Trân trọng,\nBan quản trị IlFreight Logistics";

            db_insert(
                "INSERT INTO mail_outbox (to_email, subject, body) VALUES (?, ?, ?)",
                "sss",
                [$email, $subject, $body]
            );
        }
    }
}

render_header('Quên mật khẩu');
?>
<div class="card" style="max-width:480px;margin:0 auto;">
    <h1>Quên mật khẩu</h1>
    <p class="muted">Nhập email đăng ký tài khoản của bạn để nhận liên kết đặt lại mật khẩu.</p>
    <?php if ($info) flash($info, 'info'); ?>
    <form action="/forgot-password" method="post">
        <?= csrf_field() ?>
        <div class="form-row">
            <label>Địa chỉ Email</label>
            <input type="email" name="email" value="<?= htmlspecialchars($email) ?>" required autofocus placeholder="email@example.com">
        </div>
        <button class="btn" type="submit" style="width:100%">Gửi liên kết khôi phục</button>
    </form>
    <div style="margin-top:16px;text-align:center;font-size:13px;">
        <a href="/login">← Quay lại trang Đăng nhập</a>
    </div>
</div>
<?php
render_footer();
