<?php
/**
 * auth.php — Authentication, Role Check, and CSRF Protection Helpers.
 */

require_once __DIR__ . '/layout.php';

/**
 * require_login() — Kiem tra dang nhap, redirect ve /login neu chua dang nhap.
 */
function require_login(): array
{
    $u = current_user();
    if (!$u) {
        $_SESSION['redirect_after_login'] = $_SERVER['REQUEST_URI'] ?? '/';
        header('Location: /login');
        exit;
    }
    return $u;
}

/**
 * require_role() — Kiem tra vai tro cua user (customer, staff, admin).
 * Neu khong co quyen, tra ve 403 Forbidden kem trang thong bao.
 */
function require_role(array $roles): array
{
    $u = require_login();
    if (!in_array($u['role'] ?? '', $roles, true)) {
        http_response_code(403);
        render_header('403 — Không có quyền truy cập');
        echo '<div class="card"><h1>403 — Truy cập bị từ chối</h1>'
            . '<p>Tài khoản của bạn (vai trò <strong>' . htmlspecialchars($u['role'] ?? 'unknown', ENT_QUOTES, 'UTF-8') . '</strong>) không có quyền truy cập trang này.</p>'
            . '<p><a href="/" class="btn btn-sm">Về trang chủ</a></p></div>';
        render_footer();
        exit;
    }
    return $u;
}

/**
 * csrf_token() — Sinh hoac lay CSRF token tu session.
 */
function csrf_token(): string
{
    if (session_status() === PHP_SESSION_NONE) {
        session_start();
    }
    if (empty($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
    }
    return $_SESSION['csrf_token'];
}

/**
 * csrf_field() — In input hidden chua CSRF token cho form POST.
 */
function csrf_field(): string
{
    $token = htmlspecialchars(csrf_token(), ENT_QUOTES, 'UTF-8');
    return '<input type="hidden" name="csrf_token" value="' . $token . '">';
}

/**
 * csrf_verify() — Xac thuc CSRF token khi submit form POST.
 * Neu sai token, tra ve 400 Bad Request va dung chuong trinh.
 */
function csrf_verify(): void
{
    if (session_status() === PHP_SESSION_NONE) {
        session_start();
    }
    $postToken = $_POST['csrf_token'] ?? '';
    $sessionToken = $_SESSION['csrf_token'] ?? '';

    if (empty($postToken) || empty($sessionToken) || !hash_equals($sessionToken, $postToken)) {
        http_response_code(400);
        render_header('400 — Yêu cầu không hợp lệ');
        echo '<div class="card"><h1>400 — Lỗi CSRF Token</h1>'
            . '<p>Yêu cầu bị từ chối do thiếu hoặc sai CSRF token. Vui lòng quay lại và thử lại.</p>'
            . '<p><a href="javascript:history.back()" class="btn btn-sm">Quay lại</a></p></div>';
        render_footer();
        exit;
    }
}

/**
 * app_base_url() — Xac dinh base URL an toan theo domain hien tai.
 */
function app_base_url(): string
{
    $proto = 'http';
    if (
        (!empty($_SERVER['HTTP_X_FORWARDED_PROTO']) && strtolower((string)$_SERVER['HTTP_X_FORWARDED_PROTO']) === 'https')
        || (!empty($_SERVER['HTTPS']) && strtolower((string)$_SERVER['HTTPS']) !== 'off')
    ) {
        $proto = 'https';
    }
    $rawHost = (string)($_SERVER['HTTP_HOST'] ?? '');
    if (preg_match('/^[a-zA-Z0-9.-]+(?::\d{1,5})?$/', $rawHost)) {
        return $proto . '://' . $rawHost;
    }
    return 'http://127.0.0.1:8088';
}
