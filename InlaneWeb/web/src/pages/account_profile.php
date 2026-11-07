<?php
/**
 * account_profile.php — Cập nhật thông tin liên hệ mở rộng trong user_profiles.
 */
$u = require_login();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: /account');
    exit;
}

csrf_verify();

$full_name = trim($_POST['full_name'] ?? '');
$phone     = trim($_POST['phone'] ?? '');
$company   = trim($_POST['company'] ?? '');
$address   = trim($_POST['address'] ?? '');

$userId = (int)$u['id'];
$existing = db_select_one("SELECT user_id FROM user_profiles WHERE user_id = ?", "i", [$userId]);

if ($existing) {
    db_execute(
        "UPDATE user_profiles SET full_name = ?, phone = ?, company = ?, address = ? WHERE user_id = ?",
        "ssssi",
        [$full_name, $phone, $company, $address, $userId]
    );
} else {
    db_execute(
        "INSERT INTO user_profiles (user_id, full_name, phone, company, address, is_locked, accepted_terms_at) VALUES (?, ?, ?, ?, ?, 0, NOW())",
        "issss",
        [$userId, $full_name, $phone, $company, $address]
    );
}

$_SESSION['profile_flash'] = 'Thông tin liên hệ đã được cập nhật thành công!';
header('Location: /account');
exit;
