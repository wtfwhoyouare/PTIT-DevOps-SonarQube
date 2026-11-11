<?php
/**
 * register.php — Đăng ký tài khoản khách hàng mới.
 */
$error = null;
$username = trim($_POST['username'] ?? '');
$email = trim($_POST['email'] ?? '');
$full_name = trim($_POST['full_name'] ?? '');
$phone = trim($_POST['phone'] ?? '');
$company = trim($_POST['company'] ?? '');
$address = trim($_POST['address'] ?? '');

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    csrf_verify();

    $password = $_POST['password'] ?? '';
    $password_confirm = $_POST['password_confirm'] ?? '';
    $agree_terms = isset($_POST['agree_terms']);

    if (!preg_match('/^[a-zA-Z0-9_]{3,30}$/', $username)) {
        $error = 'Tên đăng nhập phải từ 3 đến 30 ký tự (chỉ bao gồm chữ, số và dấu gạch dưới).';
    } elseif (!filter_var($email, FILTER_VALIDATE_EMAIL) || mb_strlen($email) > 150) {
        $error = 'Địa chỉ email không đúng định dạng hoặc vượt quá 150 ký tự.';
    } elseif (mb_strlen($password) < 8) {
        $error = 'Mật khẩu phải có độ dài tối thiểu 8 ký tự.';
    } elseif ($password !== $password_confirm) {
        $error = 'Mật khẩu nhập lại không khớp.';
    } elseif (empty($full_name) || mb_strlen($full_name) > 100) {
        $error = 'Vui lòng nhập họ và tên hợp lệ (tối đa 100 ký tự).';
    } elseif (empty($phone) || mb_strlen($phone) > 20) {
        $error = 'Vui lòng nhập số điện thoại liên hệ hợp lệ (tối đa 20 ký tự).';
    } elseif (mb_strlen($company) > 100 || mb_strlen($address) > 255) {
        $error = 'Tên công ty (tối đa 100 ký tự) hoặc địa chỉ (tối đa 255 ký tự) quá dài.';
    } elseif (!$agree_terms) {
        $error = 'Bạn cần đồng ý với điều khoản dịch vụ để tiếp tục.';
    } else {
        // Kiểm tra username đã tồn tại chưa
        $existUser = db_select_one("SELECT id FROM users WHERE username = ?", "s", [$username]);
        if ($existUser) {
            $error = 'Tên đăng nhập đã được sử dụng. Vui lòng chọn tên khác.';
        } else {
            // Kiểm tra email đã tồn tại chưa
            $existEmail = db_select_one("SELECT id FROM users WHERE email = ?", "s", [$email]);
            if ($existEmail) {
                $error = 'Email này đã được đăng ký tài khoản. Vui lòng sử dụng chức năng Quên mật khẩu.';
            } else {
                // Tạo API key định dạng ILF-CUS-<16 hex>
                $api_key = 'ILF-CUS-' . bin2hex(random_bytes(8));
                $remember_token = bin2hex(random_bytes(16));

                // LAB: mat khau luu dang ro de tuong thich login.php
                $userId = db_insert(
                    "INSERT INTO users (username, password, email, role, api_key, remember_token) VALUES (?, ?, ?, 'customer', ?, ?)",
                    "sssss",
                    [$username, $password, $email, $api_key, $remember_token]
                );

                if ($userId > 0) {
                    // Ghi thông tin mở rộng vào user_profiles
                    db_execute(
                        "INSERT INTO user_profiles (user_id, full_name, phone, company, address, is_locked, accepted_terms_at) VALUES (?, ?, ?, ?, ?, 0, NOW())",
                        "issss",
                        [$userId, $full_name, $phone, $company, $address]
                    );

                    // Gửi email chào mừng vào mail_outbox
                    $mailSubject = 'Chào mừng bạn đến với IlFreight Logistics';
                    $mailBody = "Kính gửi {$full_name},\n\n"
                        . "Chúc mừng bạn đã tạo tài khoản khách hàng thành công tại IlFreight Logistics.\n"
                        . "Thông tin tài khoản:\n"
                        . "- Tên đăng nhập: {$username}\n"
                        . "- Email: {$email}\n"
                        . "- API Key: {$api_key}\n\n"
                        . "Bạn có thể đăng nhập ngay tại: " . app_base_url() . "/login\n\n"
                        . "Trân trọng,\nĐội ngũ IlFreight Logistics";

                    db_insert(
                        "INSERT INTO mail_outbox (to_email, subject, body) VALUES (?, ?, ?)",
                        "sss",
                        [$email, $mailSubject, $mailBody]
                    );

                    $_SESSION['flash_msg'] = 'Đăng ký tài khoản thành công! Vui lòng đăng nhập.';
                    $_SESSION['flash_type'] = 'success';
                    header('Location: /login');
                    exit;
                } else {
                    $error = 'Có lỗi xảy ra khi tạo tài khoản. Vui lòng thử lại sau.';
                }
            }
        }
    }
}

render_header('Đăng ký tài khoản');
?>
<div class="card" style="max-width:560px;margin:0 auto;">
    <h1>Đăng ký tài khoản khách hàng</h1>
    <p class="muted">Tạo tài khoản để quản lý vận đơn và đặt lịch dịch vụ logistics.</p>
    <?php if ($error) flash($error, 'error'); ?>
    <form action="/register" method="post">
        <?= csrf_field() ?>
        <div class="form-row">
            <label>Tên đăng nhập (*)</label>
            <input type="text" name="username" value="<?= htmlspecialchars($username) ?>" required autofocus placeholder="3-30 ký tự chữ, số hoặc _">
        </div>
        <div class="form-row">
            <label>Địa chỉ Email (*)</label>
            <input type="email" name="email" value="<?= htmlspecialchars($email) ?>" required placeholder="email@example.com">
        </div>
        <div class="form-row">
            <label>Mật khẩu (*, tối thiểu 8 ký tự)</label>
            <input type="password" name="password" required placeholder="Nhập mật khẩu">
        </div>
        <div class="form-row">
            <label>Nhập lại mật khẩu (*)</label>
            <input type="password" name="password_confirm" required placeholder="Xác nhận lại mật khẩu">
        </div>
        <div class="form-row">
            <label>Họ và tên (*)</label>
            <input type="text" name="full_name" value="<?= htmlspecialchars($full_name) ?>" required placeholder="Nguyễn Văn A">
        </div>
        <div class="form-row">
            <label>Số điện thoại (*)</label>
            <input type="tel" name="phone" value="<?= htmlspecialchars($phone) ?>" required placeholder="0901234567">
        </div>
        <div class="form-row">
            <label>Tên công ty / Doanh nghiệp</label>
            <input type="text" name="company" value="<?= htmlspecialchars($company) ?>" placeholder="Công ty TNHH Logistics ABC">
        </div>
        <div class="form-row">
            <label>Địa chỉ liên hệ</label>
            <input type="text" name="address" value="<?= htmlspecialchars($address) ?>" placeholder="Địa chỉ trụ sở / nhận hàng">
        </div>
        <div class="form-row" style="margin-top:16px;">
            <label style="display:flex;align-items:center;gap:8px;font-weight:normal;cursor:pointer;">
                <input type="checkbox" name="agree_terms" value="1" style="width:auto;margin:0;" <?= !empty($_POST['agree_terms']) ? 'checked' : '' ?> required>
                <span>Tôi đồng ý với <a href="/guide" target="_blank">Điều khoản dịch vụ và Quy chuẩn an toàn</a> của IlFreight.</span>
            </label>
        </div>
        <button class="btn" type="submit" style="width:100%;margin-top:12px;">Đăng ký ngay</button>
    </form>
    <p class="muted" style="margin-top:16px;text-align:center;">
        Đã có tài khoản? <a href="/login">Đăng nhập tại đây</a>
    </p>
</div>
<?php
render_footer();
