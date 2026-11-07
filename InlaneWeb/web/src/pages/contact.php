<?php
/**
 * contact.php — Liên hệ và gửi thông điệp yêu cầu tư vấn.
 */
$error = null;
$success = null;

$full_name = trim($_POST['full_name'] ?? '');
$email     = trim($_POST['email'] ?? '');
$phone     = trim($_POST['phone'] ?? '');
$message   = trim($_POST['message'] ?? '');

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    csrf_verify();

    if (empty($full_name)) {
        $error = 'Vui lòng nhập họ và tên của bạn.';
    } elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $error = 'Địa chỉ email không đúng định dạng.';
    } elseif (empty($message)) {
        $error = 'Vui lòng nhập nội dung cần liên hệ.';
    } elseif (mb_strlen($message) < 10) {
        $error = 'Nội dung tin nhắn quá ngắn (tối thiểu 10 ký tự).';
    } else {
        db_insert(
            "INSERT INTO contact_messages (full_name, email, phone, message, is_handled) VALUES (?, ?, ?, ?, 0)",
            "ssss",
            [$full_name, $email, $phone, $message]
        );

        $success = 'Cảm ơn bạn đã liên hệ! Thông điệp của bạn đã được ghi nhận. Đội ngũ IlFreight sẽ phản hồi trong vòng 24 giờ làm việc.';
        $full_name = '';
        $email = '';
        $phone = '';
        $message = '';
    }
}

render_header('Liên hệ chúng tôi');
?>
<div class="card" style="max-width:680px;margin:0 auto;">
    <h1>Liên hệ với IlFreight Logistics</h1>
    <p class="muted">Hãy để lại lời nhắn hoặc yêu cầu hỗ trợ. Đội ngũ chuyên gia của chúng tôi luôn sẵn sàng phục vụ bạn.</p>

    <?php
    if ($error) flash($error, 'error');
    if ($success) flash($success, 'success');
    ?>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px;background:var(--panelalt);padding:16px;border-radius:8px;">
        <div>
            <strong style="color:var(--deep);">Trụ sở chính:</strong>
            <div style="font-size:13px;color:#555;margin-top:4px;">Cảng Đình Vũ, Quận Hải An, TP. Hải Phòng, Việt Nam</div>
            <div style="font-size:13px;color:#555;margin-top:2px;">Điện thoại: +84 (0) 225 3888 999</div>
        </div>
        <div>
            <strong style="color:var(--deep);">Văn phòng đại diện:</strong>
            <div style="font-size:13px;color:#555;margin-top:4px;">Tòa nhà Saigon Tower, Quận 1, TP. Hồ Chí Minh</div>
            <div style="font-size:13px;color:#555;margin-top:2px;">Email: contact@ilfreight.local</div>
        </div>
    </div>

    <form action="/contact" method="post">
        <?= csrf_field() ?>
        <div class="form-row">
            <label>Họ và tên (*)</label>
            <input type="text" name="full_name" value="<?= htmlspecialchars($full_name, ENT_QUOTES, 'UTF-8') ?>" required placeholder="Nguyễn Văn A">
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
            <div class="form-row">
                <label>Địa chỉ Email (*)</label>
                <input type="email" name="email" value="<?= htmlspecialchars($email, ENT_QUOTES, 'UTF-8') ?>" required placeholder="email@example.com">
            </div>
            <div class="form-row">
                <label>Số điện thoại liên hệ</label>
                <input type="tel" name="phone" value="<?= htmlspecialchars($phone, ENT_QUOTES, 'UTF-8') ?>" placeholder="0901234567">
            </div>
        </div>
        <div class="form-row">
            <label>Nội dung yêu cầu / Thắc mắc (*)</label>
            <textarea name="message" rows="5" required placeholder="Nhập chi tiết yêu cầu về tuyến vận tải, loại hàng hoặc dịch vụ bạn quan tâm..."><?= htmlspecialchars($message, ENT_QUOTES, 'UTF-8') ?></textarea>
        </div>
        <button class="btn" type="submit" style="width:100%;">Gửi thông tin liên hệ</button>
    </form>
</div>
<?php
render_footer();
