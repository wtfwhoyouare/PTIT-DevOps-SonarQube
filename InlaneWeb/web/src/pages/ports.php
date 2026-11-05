<?php
/**
 * ports.php — Tra cuu cang (?q=). Query SELECT, ket qua hien bang.
 *
 * !!! DIEM INJECT BẢO MẬT:
 * 1. SQL Injection (In-band UNION-based):
 *    $q noi truc tiep vao menh de WHERE LIKE -> UNION 4 cot.
 *    Payload mau: ' UNION SELECT 1,@@version,3,4-- -
 * 
 * 2. Reflected Cross-Site Scripting (Reflected XSS - CWE-79):
 *    Bien $q tu tham so GET duoc render truc tiep ra output HTML
 *    trong banner ket qua tim kiem, gia tri o input va thong bao he thong ma khong escape.
 *    Payload mau:
 *      - /ports?q=<script>alert('XSS-Reflected')</script>
 *      - /ports?q=<img src=x onerror=alert(document.domain)>
 *      - /ports?q=<svg onload=alert(document.cookie)>
 *      - /ports?q="><script>alert(1)</script>
 */
render_header('Tra cứu cảng');

$q = $_GET['q'] ?? '';
?>
<div class="card">
    <h1>Tra cứu cảng biển</h1>
    <form class="searchbar" action="/ports" method="get">
        <input type="text" name="q" value="<?= $q ?>" placeholder="Mã cảng hoặc tên thành phố...">
        <button class="btn" type="submit">Tra cứu</button>
    </form>

    <?php if ($q !== ''): ?>
        <?php
        // !!! DIEM LOI REFLECTED XSS: In truc tiep bien $q ra HTML ma khong qua htmlspecialchars !!!
        echo '<div class="search-summary" style="margin: 12px 0 16px 0; padding: 10px 14px; background: #eef5fb; border-left: 4px solid var(--primary); border-radius: 4px;">'
           . 'Kết quả tra cứu cho từ khóa: <strong>' . $q . '</strong>'
           . '</div>';

        // !!! NOI CHUOI TRUC TIEP — khong sanitize -> SQLi (UNION-based) !!!
        $sql = "SELECT code, city, country, volume FROM ports WHERE code LIKE '%$q%'";
        echo '<div class="query-box">' . htmlspecialchars($sql) . '</div>';

        $res = query($sql);
        if ($res && mysqli_num_rows($res) > 0) {
            echo '<table class="data"><tr><th>Mã cảng</th><th>Thành phố</th><th>Quốc gia</th><th>Sản lượng (M TEU)</th></tr>';
            while ($row = mysqli_fetch_row($res)) {
                echo '<tr>';
                foreach ($row as $cell) {
                    echo '<td>' . htmlspecialchars((string)$cell) . '</td>';
                }
                echo '</tr>';
            }
            echo '</table>';
        } elseif ($res) {
            flash('Không tìm thấy cảng nào khớp với từ khóa "<code>' . $q . '</code>".', 'info');
        }
        ?>
    <?php else: ?>
        <p class="muted">Nhập mã cảng để tra cứu (vd: <code>CN</code>, <code>SG</code>, <code>DXB</code>).</p>
    <?php endif; ?>
</div>
<?php
render_footer();
