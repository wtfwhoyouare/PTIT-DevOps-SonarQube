<?php
/**
 * admin_users.php — Quản lý người dùng (chỉ dành cho vai trò admin).
 */
$u = require_role(['admin']);
$error = null;
$success = null;

// Xử lý các thao tác POST (Tạo mới, Cập nhật, Khoá/Mở khoá)
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    csrf_verify();
    $action = $_POST['action'] ?? '';

    if ($action === 'create') {
        $username   = trim($_POST['username'] ?? '');
        $email      = trim($_POST['email'] ?? '');
        $password   = $_POST['password'] ?? '';
        $role       = $_POST['role'] ?? 'customer';
        $full_name  = trim($_POST['full_name'] ?? '');
        $phone      = trim($_POST['phone'] ?? '');
        $company    = trim($_POST['company'] ?? '');
        $address    = trim($_POST['address'] ?? '');

        $validRoles = ['customer', 'staff', 'admin'];

        if (!preg_match('/^[a-zA-Z0-9_]{3,30}$/', $username)) {
            $error = 'Tên đăng nhập không hợp lệ (3-30 ký tự, chữ, số, _).';
        } elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            $error = 'Email không hợp lệ.';
        } elseif (mb_strlen($password) < 8) {
            $error = 'Mật khẩu phải có tối thiểu 8 ký tự.';
        } elseif (!in_array($role, $validRoles, true)) {
            $error = 'Vai trò người dùng không hợp lệ.';
        } else {
            $existUser = db_select_one("SELECT id FROM users WHERE username = ?", "s", [$username]);
            $existEmail = db_select_one("SELECT id FROM users WHERE email = ?", "s", [$email]);

            if ($existUser) {
                $error = 'Tên đăng nhập đã tồn tại.';
            } elseif ($existEmail) {
                $error = 'Email đã được sử dụng.';
            } else {
                $prefix = ($role === 'admin') ? 'ILF-ADM-' : (($role === 'staff') ? 'ILF-STF-' : 'ILF-CUS-');
                $apiKey = $prefix . bin2hex(random_bytes(8));

                // LAB: mat khau luu dang ro de tuong thich login.php
                $newId = db_insert(
                    "INSERT INTO users (username, password, email, role, api_key) VALUES (?, ?, ?, ?, ?)",
                    "sssss",
                    [$username, $password, $email, $role, $apiKey]
                );

                if ($newId > 0) {
                    db_execute(
                        "INSERT INTO user_profiles (user_id, full_name, phone, company, address, is_locked, accepted_terms_at) VALUES (?, ?, ?, ?, ?, 0, NOW())",
                        "issss",
                        [$newId, $full_name, $phone, $company, $address]
                    );
                    $success = "Tạo người dùng {$username} thành công!";
                } else {
                    $error = 'Không thể tạo người dùng mới.';
                }
            }
        }
    } elseif ($action === 'edit') {
        $targetId   = (int)($_POST['target_id'] ?? 0);
        $email      = trim($_POST['email'] ?? '');
        $role       = $_POST['role'] ?? 'customer';
        $full_name  = trim($_POST['full_name'] ?? '');
        $phone      = trim($_POST['phone'] ?? '');
        $company    = trim($_POST['company'] ?? '');
        $address    = trim($_POST['address'] ?? '');

        $validRoles = ['customer', 'staff', 'admin'];

        $targetUser = db_select_one("SELECT * FROM users WHERE id = ?", "i", [$targetId]);
        if (!$targetUser) {
            $error = 'Người dùng không tồn tại.';
        } elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            $error = 'Email không hợp lệ.';
        } elseif (!in_array($role, $validRoles, true)) {
            $error = 'Vai trò không hợp lệ.';
        } elseif ($targetId === (int)$u['id'] && $role !== 'admin') {
            // Admin không được tự hạ quyền chính mình
            $error = 'Bạn không thể tự hạ quyền quản trị viên của chính mình.';
        } else {
            // Kiểm tra trùng email với user khác
            $dupEmail = db_select_one("SELECT id FROM users WHERE email = ? AND id != ?", "si", [$email, $targetId]);
            if ($dupEmail) {
                $error = 'Email này đã được sử dụng bởi tài khoản khác.';
            } else {
                db_execute("UPDATE users SET email = ?, role = ? WHERE id = ?", "ssi", [$email, $role, $targetId]);
                
                $profExist = db_select_one("SELECT user_id FROM user_profiles WHERE user_id = ?", "i", [$targetId]);
                if ($profExist) {
                    db_execute(
                        "UPDATE user_profiles SET full_name = ?, phone = ?, company = ?, address = ? WHERE user_id = ?",
                        "ssssi",
                        [$full_name, $phone, $company, $address, $targetId]
                    );
                } else {
                    db_execute(
                        "INSERT INTO user_profiles (user_id, full_name, phone, company, address, is_locked, accepted_terms_at) VALUES (?, ?, ?, ?, ?, 0, NOW())",
                        "issss",
                        [$targetId, $full_name, $phone, $company, $address]
                    );
                }
                $success = "Cập nhật tài khoản {$targetUser['username']} thành công!";
            }
        }
    } elseif ($action === 'toggle_lock') {
        $targetId = (int)($_POST['target_id'] ?? 0);
        $lockVal  = (int)($_POST['lock_val'] ?? 0);

        if ($targetId === (int)$u['id']) {
            // Admin không được tự khoá chính mình
            $error = 'Bạn không thể tự khoá tài khoản của chính mình.';
        } else {
            $targetUser = db_select_one("SELECT username FROM users WHERE id = ?", "i", [$targetId]);
            if ($targetUser) {
                $profExist = db_select_one("SELECT user_id FROM user_profiles WHERE user_id = ?", "i", [$targetId]);
                if ($profExist) {
                    db_execute("UPDATE user_profiles SET is_locked = ? WHERE user_id = ?", "ii", [$lockVal, $targetId]);
                } else {
                    db_execute(
                        "INSERT INTO user_profiles (user_id, is_locked, accepted_terms_at) VALUES (?, ?, NOW())",
                        "ii",
                        [$targetId, $lockVal]
                    );
                }
                $statusMsg = ($lockVal === 1) ? 'khoá' : 'mở khoá';
                $success = "Đã {$statusMsg} tài khoản {$targetUser['username']} thành công!";
            }
        }
    }
}

// Tìm kiếm và phân trang
$search = trim($_GET['q'] ?? '');
$page = max(1, (int)($_GET['page'] ?? 1));
$perPage = 10;
$offset = ($page - 1) * $perPage;

$whereClause = "";
$types = "";
$params = [];

if ($search !== '') {
    $whereClause = "WHERE u.username LIKE ? OR u.email LIKE ? OR p.full_name LIKE ? OR p.company LIKE ?";
    $types = "ssss";
    $searchWild = '%' . $search . '%';
    $params = [$searchWild, $searchWild, $searchWild, $searchWild];
}

$countSql = "SELECT COUNT(*) AS total FROM users u LEFT JOIN user_profiles p ON p.user_id = u.id {$whereClause}";
$totalRow = db_select_one($countSql, $types, $params);
$totalRecords = $totalRow ? (int)$totalRow['total'] : 0;
$totalPages = max(1, (int)ceil($totalRecords / $perPage));

$querySql = "SELECT u.id, u.username, u.email, u.role, u.api_key,
                    p.full_name, p.phone, p.company, p.address, p.is_locked, p.created_at
             FROM users u
             LEFT JOIN user_profiles p ON p.user_id = u.id
             {$whereClause}
             ORDER BY u.id DESC
             LIMIT ? OFFSET ?";
$typesWithLimit = $types . "ii";
$paramsWithLimit = array_merge($params, [$perPage, $offset]);

$users = db_select($querySql, $typesWithLimit, $paramsWithLimit);

render_header('Quản lý người dùng');
?>
<div class="card">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
        <div>
            <h1>Quản lý người dùng (User Management)</h1>
            <p class="muted">Chỉ dành cho Quản trị viên tối cao (Admin).</p>
        </div>
        <button onclick="document.getElementById('createUserModal').style.display='block'" class="btn">+ Tạo người dùng mới</button>
    </div>

    <?php
    if ($error) flash($error, 'error');
    if ($success) flash($success, 'success');
    ?>

    <!-- Form tìm kiếm -->
    <form method="get" action="/admin/users" style="display:flex;gap:10px;margin:16px 0;">
        <input type="text" name="q" value="<?= htmlspecialchars($search, ENT_QUOTES, 'UTF-8') ?>" placeholder="Tìm theo username, email, họ tên, công ty..." style="flex:1;padding:8px 12px;border:1px solid var(--line);border-radius:6px;">
        <button type="submit" class="btn btn-sm">Tìm kiếm</button>
        <?php if ($search !== ''): ?>
            <a href="/admin/users" class="btn btn-sm" style="background:#5B6B7B;">Xoá tìm</a>
        <?php endif; ?>
    </form>

    <div class="table-responsive">
        <table class="data">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Tài khoản / Họ tên</th>
                    <th>Email / SĐT</th>
                    <th>Công ty</th>
                    <th>Vai trò</th>
                    <th>Trạng thái</th>
                    <th>Thao tác</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($users as $usr): ?>
                    <tr>
                        <td>#<?= htmlspecialchars((string)$usr['id'], ENT_QUOTES, 'UTF-8') ?></td>
                        <td>
                            <strong><?= htmlspecialchars($usr['username'], ENT_QUOTES, 'UTF-8') ?></strong><br>
                            <span class="muted"><?= htmlspecialchars($usr['full_name'] ?? '—', ENT_QUOTES, 'UTF-8') ?></span>
                        </td>
                        <td>
                            <?= htmlspecialchars($usr['email'] ?? '—', ENT_QUOTES, 'UTF-8') ?><br>
                            <span class="muted"><?= htmlspecialchars($usr['phone'] ?? '—', ENT_QUOTES, 'UTF-8') ?></span>
                        </td>
                        <td><?= htmlspecialchars($usr['company'] ?? '—', ENT_QUOTES, 'UTF-8') ?></td>
                        <td>
                            <span class="badge" style="background:<?= $usr['role'] === 'admin' ? '#fbe4e5;color:var(--danger)' : (($usr['role'] === 'staff') ? '#fff3d6;color:#8a6100' : '#e7f0f7;color:var(--deep)') ?>;">
                                <?= htmlspecialchars($usr['role'], ENT_QUOTES, 'UTF-8') ?>
                            </span>
                        </td>
                        <td>
                            <?php if (!empty($usr['is_locked'])): ?>
                                <span class="badge badge-hold">ĐÃ KHOÁ</span>
                            <?php else: ?>
                                <span class="badge badge-delivered">HOẠT ĐỘNG</span>
                            <?php endif; ?>
                        </td>
                        <td style="white-space:nowrap;">
                            <!-- Nút sửa (mở modal inline) -->
                            <details style="display:inline-block;">
                                <summary class="btn btn-sm" style="padding:3px 8px;font-size:12px;background:var(--teal);cursor:pointer;list-style:none;">Sửa</summary>
                                <div style="position:absolute;z-index:100;background:#fff;border:2px solid var(--line);box-shadow:0 4px 12px rgba(0,0,0,0.15);padding:16px;border-radius:8px;min-width:320px;margin-top:4px;">
                                    <h3>Sửa tài khoản <?= htmlspecialchars($usr['username'], ENT_QUOTES, 'UTF-8') ?></h3>
                                    <form method="post" action="/admin/users">
                                        <?= csrf_field() ?>
                                        <input type="hidden" name="action" value="edit">
                                        <input type="hidden" name="target_id" value="<?= htmlspecialchars((string)$usr['id'], ENT_QUOTES, 'UTF-8') ?>">
                                        <div class="form-row">
                                            <label>Email</label>
                                            <input type="email" name="email" value="<?= htmlspecialchars($usr['email'] ?? '', ENT_QUOTES, 'UTF-8') ?>" required>
                                        </div>
                                        <div class="form-row">
                                            <label>Vai trò</label>
                                            <select name="role">
                                                <option value="customer" <?= $usr['role'] === 'customer' ? 'selected' : '' ?>>Customer</option>
                                                <option value="staff" <?= $usr['role'] === 'staff' ? 'selected' : '' ?>>Staff</option>
                                                <option value="admin" <?= $usr['role'] === 'admin' ? 'selected' : '' ?>>Admin</option>
                                            </select>
                                        </div>
                                        <div class="form-row">
                                            <label>Họ tên</label>
                                            <input type="text" name="full_name" value="<?= htmlspecialchars($usr['full_name'] ?? '', ENT_QUOTES, 'UTF-8') ?>">
                                        </div>
                                        <div class="form-row">
                                            <label>Số điện thoại</label>
                                            <input type="text" name="phone" value="<?= htmlspecialchars($usr['phone'] ?? '', ENT_QUOTES, 'UTF-8') ?>">
                                        </div>
                                        <div class="form-row">
                                            <label>Công ty</label>
                                            <input type="text" name="company" value="<?= htmlspecialchars($usr['company'] ?? '', ENT_QUOTES, 'UTF-8') ?>">
                                        </div>
                                        <div class="form-row">
                                            <label>Địa chỉ</label>
                                            <input type="text" name="address" value="<?= htmlspecialchars($usr['address'] ?? '', ENT_QUOTES, 'UTF-8') ?>">
                                        </div>
                                        <button type="submit" class="btn btn-sm">Lưu</button>
                                    </form>
                                </div>
                            </details>

                            <!-- Nút Khoá / Mở khoá -->
                            <?php if ((int)$usr['id'] !== (int)$u['id']): ?>
                                <form method="post" action="/admin/users" style="display:inline;" onsubmit="return confirm('Bạn có chắc muốn thực hiện thao tác này?');">
                                    <?= csrf_field() ?>
                                    <input type="hidden" name="action" value="toggle_lock">
                                    <input type="hidden" name="target_id" value="<?= htmlspecialchars((string)$usr['id'], ENT_QUOTES, 'UTF-8') ?>">
                                    <?php if (!empty($usr['is_locked'])): ?>
                                        <input type="hidden" name="lock_val" value="0">
                                        <button type="submit" class="btn btn-sm" style="padding:3px 8px;font-size:12px;background:var(--ok);">Mở khoá</button>
                                    <?php else: ?>
                                        <input type="hidden" name="lock_val" value="1">
                                        <button type="submit" class="btn btn-sm btn-danger" style="padding:3px 8px;font-size:12px;">Khoá</button>
                                    <?php endif; ?>
                                </form>
                            <?php else: ?>
                                <span class="muted" style="font-size:11px;">(Chính bạn)</span>
                            <?php endif; ?>
                        </td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>

    <!-- Phân trang -->
    <?php if ($totalPages > 1): ?>
        <div class="pagination">
            <span>Trang <?= htmlspecialchars((string)$page, ENT_QUOTES, 'UTF-8') ?> / <?= htmlspecialchars((string)$totalPages, ENT_QUOTES, 'UTF-8') ?> (Tổng <?= htmlspecialchars((string)$totalRecords, ENT_QUOTES, 'UTF-8') ?>)</span>
            <?php for ($i = 1; $i <= $totalPages; $i++): ?>
                <?php $url = '/admin/users?page=' . $i . ($search !== '' ? '&q=' . urlencode($search) : ''); ?>
                <?php if ($i === $page): ?>
                    <span class="active"><?= htmlspecialchars((string)$i, ENT_QUOTES, 'UTF-8') ?></span>
                <?php else: ?>
                    <a href="<?= htmlspecialchars($url, ENT_QUOTES, 'UTF-8') ?>"><?= htmlspecialchars((string)$i, ENT_QUOTES, 'UTF-8') ?></a>
                <?php endif; ?>
            <?php endfor; ?>
        </div>
    <?php endif; ?>
</div>

<!-- Modal tạo người dùng mới -->
<div id="createUserModal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:999;overflow-y:auto;">
    <div style="background:#fff;max-width:520px;margin:50px auto;padding:24px;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,0.2);">
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--line);padding-bottom:12px;margin-bottom:16px;">
            <h2 style="margin:0;">Thêm người dùng mới</h2>
            <button onclick="document.getElementById('createUserModal').style.display='none'" style="border:none;background:none;font-size:20px;cursor:pointer;">&times;</button>
        </div>
        <form method="post" action="/admin/users">
            <?= csrf_field() ?>
            <input type="hidden" name="action" value="create">
            <div class="form-row">
                <label>Tên đăng nhập (*)</label>
                <input type="text" name="username" required placeholder="3-30 ký tự">
            </div>
            <div class="form-row">
                <label>Địa chỉ Email (*)</label>
                <input type="email" name="email" required placeholder="user@ilfreight.local">
            </div>
            <div class="form-row">
                <label>Mật khẩu khởi tạo (*, >= 8 ký tự)</label>
                <input type="password" name="password" required placeholder="Nhập mật khẩu">
            </div>
            <div class="form-row">
                <label>Vai trò (*)</label>
                <select name="role">
                    <option value="customer">Customer (Khách hàng)</option>
                    <option value="staff">Staff (Nhân viên vận hành)</option>
                    <option value="admin">Admin (Quản trị viên)</option>
                </select>
            </div>
            <div class="form-row">
                <label>Họ và tên</label>
                <input type="text" name="full_name" placeholder="Nguyễn Văn A">
            </div>
            <div class="form-row">
                <label>Số điện thoại</label>
                <input type="text" name="phone" placeholder="0901234567">
            </div>
            <div class="form-row">
                <label>Công ty</label>
                <input type="text" name="company" placeholder="Công ty ABC">
            </div>
            <div class="form-row">
                <label>Địa chỉ</label>
                <input type="text" name="address" placeholder="Địa chỉ chi tiết">
            </div>
            <div style="display:flex;gap:10px;margin-top:20px;">
                <button type="submit" class="btn">Tạo tài khoản</button>
                <button type="button" onclick="document.getElementById('createUserModal').style.display='none'" class="btn" style="background:#5B6B7B;">Đóng</button>
            </div>
        </form>
    </div>
</div>
<?php
render_footer();
